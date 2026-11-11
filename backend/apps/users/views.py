import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status, viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from .authentication import PasswordVersionRefreshToken
from .serializers import (
    LoginSerializer,
    ManagedUserSerializer,
    PasswordAwareRefreshSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetEmailError,
    PasswordResetRequestSerializer,
    PropertySerializer,
    PropertyImageSerializer,
    UserActivationSerializer,
    UserDeactivationSerializer,
    send_password_reset_email,
    send_activation_email,
)
from .models import PasswordResetToken, Property, PropertyImage, UserActivationToken
from apps.appraisals.models import Appraisal
from apps.documents.models import Document

User = get_user_model()
LOGIN_ERROR_MESSAGE = "Credenciales inválidas."
PASSWORD_RESET_RESPONSE = (
    "Si existe una cuenta activa con ese correo, recibirás instrucciones para "
    "restablecer tu contraseña."
)
PASSWORD_RESET_TOKEN_ERROR = "El enlace no es válido, ya se usó o venció."


def set_refresh_cookie(response, refresh_token):
    lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        refresh_token,
        max_age=int(lifetime.total_seconds()),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path=settings.JWT_REFRESH_COOKIE_PATH,
    )
    return response


def delete_refresh_cookie(response):
    response.delete_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        path=settings.JWT_REFRESH_COOKIE_PATH,
        samesite="Lax",
    )
    return response


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.role == User.Role.ADMIN
        )


# DT-07 / HU-01: estados visibles en el catalogo publico. 'reservador' es el valor
# real guardado hoy (errata DT-16); cambiar a 'reservado' cuando se migre.
PUBLIC_STATUSES = ("disponible", "reservador")


def get_missing_publication_requirements(property_obj):
    '''
    HU-53 / RF-01: requisitos para pasar de captacion a disponible (contexto maestro §11).
    Devuelve una lista vacia si la propiedad se puede publicar.
    '''
    missing = []

    if not property_obj.images.exists():
        missing.append({
            "code": "image",
            "message": "Debe cargar al menos una fotografía.",
        })

    # Solo existe una version vigente por tipo; si esa esta vencida o rechazada no cuenta
    # aunque una version anterior haya sido valida. PENDIENTE si permite publicar (N-01).
    corretaje = Document.objects.current().filter(
        property=property_obj,
        doc_type=Document.DocType.CORRETAJE,
    ).first()
    if corretaje is None:
        missing.append({
            "code": "brokerage_contract",
            "message": "Falta el contrato de corretaje.",
        })
    elif corretaje.validation_status == Document.ValidationStatus.RECHAZADO:
        missing.append({
            "code": "brokerage_contract",
            "message": "El contrato de corretaje fue rechazado por el Administrador; suba una nueva versión.",
        })
    elif corretaje.expiration_date < timezone.localdate():
        missing.append({
            "code": "brokerage_contract",
            "message": "El contrato de corretaje está vencido; suba una nueva versión.",
        })

    if not Appraisal.objects.approved().filter(property=property_obj).exists():
        missing.append({
            "code": "appraisal",
            "message": "La propiedad necesita un avalúo aprobado.",
        })

    return missing

'''
The Views work to enrute, fetch, grab, get and retrive the information from the database and send it to the Template. 
MVT (Model-View-Template): User -> (View <-> Database) --> Template ->> User.
MVC (Model-View.Controller): User -> (View -> Model -> Database) --> View ->> User.

The main difference between this two patterns designs is a bit tricky, not because they are different, its because they dothe same thing.
Fetch data -> Send it to a Urls, or HTML template and then send it again on a template to the user again (template.)
Same MVC patter as the MVT pattern on django and on comparassion with  laravel(.php)

So that´s why some of the functions and methods inside the classes, are so similar to a query to the database.

'''
class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    # Corrección de nombres de variables
    parser_classes = [MultiPartParser, FormParser] 
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    '''
    As you can see, this method its the great example of the fecth, get, or query the database. 
    '''
@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginView(APIView):
    def post(self, request): #Post Function WEB
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()
        password = serializer.validated_data["password"]

        user = User.objects.filter(email__iexact=email).first()

        if not user or not user.is_active or user.is_locked:
            return Response(
                {"detail": LOGIN_ERROR_MESSAGE},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password): #Regla de negocio.
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.is_locked = True
            user.save(update_fields=["failed_attempts", "is_locked"])
            return Response(
                {"detail": LOGIN_ERROR_MESSAGE},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.failed_attempts = 0
        user.save(update_fields=["failed_attempts"])

        refresh = PasswordVersionRefreshToken.for_user(user)
        response = Response({
            "access": str(refresh.access_token),
            "role": user.role,
        })
        return set_refresh_cookie(response, str(refresh))


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfCookieView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"detail": "Cookie CSRF preparada."})


class CookieTokenRefreshView(TokenRefreshView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordAwareRefreshSerializer

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if not refresh_token:
            return delete_refresh_cookie(
                Response(
                    {"detail": "El refresh token no es válido."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            return delete_refresh_cookie(
                Response(
                    {"detail": "El refresh token no es válido."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_protect)
    def post(self, request):
        return delete_refresh_cookie(
            Response(status=status.HTTP_204_NO_CONTENT)
        )


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email__iexact=serializer.validated_data["email"],
            is_active=True,
        ).first()

        if user is not None:
            generator_token = default_token_generator.make_token(user)
            raw_token = f"{generator_token}.{secrets.token_urlsafe(16)}"
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
                expires_at=timezone.now()
                + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT),
            )
            try:
                send_password_reset_email(user, raw_token)
            except PasswordResetEmailError:
                reset_token.is_used = True
                reset_token.save(update_fields=["is_used"])

        return Response(
            {"detail": PASSWORD_RESET_RESPONSE},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_token = serializer.validated_data["token"]
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        with transaction.atomic():
            reset_token = (
                PasswordResetToken.objects.select_for_update()
                .filter(
                    pk=serializer.validated_data["reset_token_id"],
                    token_hash=token_hash,
                    is_used=False,
                    expires_at__gt=timezone.now(),
                )
                .first()
            )
            if reset_token is None:
                return Response(
                    {"token": PASSWORD_RESET_TOKEN_ERROR},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.select_for_update().filter(
                pk=reset_token.user_id
            ).first()
            if (
                user is None
                or not user.is_active
                or not default_token_generator.check_token(
                    user,
                    serializer.validated_data["generator_token"],
                )
            ):
                return Response(
                    {"token": PASSWORD_RESET_TOKEN_ERROR},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(serializer.validated_data["password"])
            user.is_locked = False
            user.failed_attempts = 0
            user.save(update_fields=["password", "is_locked", "failed_attempts"])
            PasswordResetToken.objects.filter(
                user=user,
                is_used=False,
            ).update(is_used=True)

        return Response(
            {"detail": "La contraseña se restableció. Ya puedes iniciar sesión."},
            status=status.HTTP_200_OK,
        )


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.order_by("last_name", "first_name", "email")
    serializer_class = ManagedUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ManagedUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    http_method_names = ["get", "patch", "head", "options"]


class UserDeactivateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def post(self, request, pk):
        serializer = UserDeactivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = get_object_or_404(User.objects.select_for_update(), pk=pk)
            if user.pk == request.user.pk:
                return Response(
                    {"detail": "No puedes desactivar tu propia cuenta."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not user.is_active:
                return Response(
                    {"detail": "La cuenta ya está desactivada."},
                    status=status.HTTP_409_CONFLICT,
                )

            if user.role == User.Role.ADVISOR:
                Property.objects.filter(agent=user).update(agent=None)

            user.is_active = False
            user.deactivation_reason = serializer.validated_data["reason"]
            user.save(update_fields=["is_active", "deactivation_reason"])
            UserActivationToken.objects.filter(
                user=user,
                used_at__isnull=True,
            ).update(used_at=timezone.now())

        return Response(ManagedUserSerializer(user).data, status=status.HTTP_200_OK)


class UserUnlockView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def post(self, request, pk):
        with transaction.atomic():
            user = get_object_or_404(User.objects.select_for_update(), pk=pk)
            if not user.is_locked:
                return Response(
                    {"detail": "La cuenta no está bloqueada."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.is_locked = False
            user.failed_attempts = 0
            user.save(update_fields=["is_locked", "failed_attempts"])

        return Response(ManagedUserSerializer(user).data, status=status.HTTP_200_OK)


class UserResendActivationView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def post(self, request, pk):
        with transaction.atomic():
            user = get_object_or_404(User.objects.select_for_update(), pk=pk)
            if user.is_active or user.deactivation_reason:
                return Response(
                    {"detail": "La cuenta está activa o fue desactivada y no puede reactivarse desde este enlace."},
                    status=status.HTTP_409_CONFLICT,
                )

            UserActivationToken.objects.filter(
                user=user,
                used_at__isnull=True,
            ).update(used_at=timezone.now())
            send_activation_email(user)

        return Response(
            {"detail": "Se envió un nuevo enlace de activación."},
            status=status.HTTP_200_OK,
        )


class UserActivationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activation = serializer.validated_data["activation"]
        token_hash = hashlib.sha256(
            serializer.validated_data["token"].encode("utf-8")
        ).hexdigest()

        with transaction.atomic():
            activation = get_object_or_404(
                UserActivationToken.objects.select_for_update().select_related("user"),
                pk=activation.pk,
                token_hash=token_hash,
                used_at__isnull=True,
                expires_at__gt=timezone.now(),
                user__is_active=False,
                user__deactivation_reason="",
            )
            user = activation.user
            user.set_password(serializer.validated_data["password"])
            user.is_active = True
            user.deactivation_reason = ""
            user.save(update_fields=["password", "is_active", "deactivation_reason"])
            activation.used_at = timezone.now()
            activation.save(update_fields=["used_at"])

        return Response(
            {"detail": "Cuenta activada. Ya puedes iniciar sesión."},
            status=status.HTTP_200_OK,
        )
        
class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    
    #The reason why it doesnt fetch all the properties.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # DT-07: un anonimo solo ve el catalogo publico, nunca fichas en captacion.
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status__in=PUBLIC_STATUSES)
        return queryset

    def perform_create(self, serializer): # Revisar sobre un inesperado error al momento de intentar crear una propiedad.
        #Verificado.
        serializer.save(agent=self.request.user)

class PropertyOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or bool(request.user and request.user.is_authenticated)
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.agent_id == request.user.id or request.user.role == "admin"

class MyPropertiesView(generics.ListAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Property.objects.filter(agent=self.request.user)
        
class PropertyPublishView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly] #Deseeperate options.

    def post(self, request, pk):
        # HU-53: la verificacion y el cambio de estado van en la misma transaccion;
        # select_for_update evita publicar dos veces en paralelo.
        with transaction.atomic():
            try:
                property_obj = Property.objects.select_for_update().get(pk=pk)
            except Property.DoesNotExist:
                return Response({"detail": "Propiedad no encontrada."}, status=status.HTTP_404_NOT_FOUND)

            #Validacion de seguridad
            if request.user != property_obj.agent and request.user.role != 'admin':
                return Response({"detail":"No tienes permiso para publicar esta propiedad."}, status=status.HTTP_403_FORBIDDEN)

            # Publicar es solo EN_CAPTACION -> DISPONIBLE (contexto maestro §11).
            if property_obj.status != 'captacion':
                return Response(
                    {"detail": "Solo se puede publicar una propiedad en captación.",
                     "status": property_obj.status},
                    status=status.HTTP_409_CONFLICT,
                )

            missing = get_missing_publication_requirements(property_obj)
            if missing:
                return Response(
                    {
                        "detail": "No se puede publicar: " + " ".join(item["message"] for item in missing),
                        "missing_requirements": missing,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            property_obj.status = 'disponible'
            property_obj.save(update_fields=['status', 'updated_at'])

        return Response(
            {
                "detail": "Propiedad publicada con éxito. Ahora es visible en el catálogo público.",
                "status": property_obj.status
            },
            status=status.HTTP_200_OK
        )


class PropertyPublicationRequirementsView(APIView):
    '''
    HU-53 / DS-15: estado de los requisitos de publicacion sin intentar publicar.
    Usa la misma regla que PropertyPublishView, asi el Expediente muestra lo mismo
    que respondera el 400 de publicar.
    '''
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            property_obj = Property.objects.get(pk=pk)
        except Property.DoesNotExist:
            return Response({"detail": "Propiedad no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Mismo permiso que publicar: dueno o admin.
        if request.user != property_obj.agent and request.user.role != 'admin':
            return Response({"detail": "No tienes permiso sobre esta propiedad."}, status=status.HTTP_403_FORBIDDEN)

        missing = get_missing_publication_requirements(property_obj)
        return Response({
            "status": property_obj.status,
            "can_publish": property_obj.status == 'captacion' and not missing,
            "missing_requirements": missing,
        })


class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all() #Query
    serializer_class = PropertySerializer
    permission_classes = [PropertyOwnerOrAdminOrReadOnly]

    def get_queryset(self):
        # DT-07: una ficha fuera del catalogo responde 404 a un anonimo.
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status__in=PUBLIC_STATUSES)
        return queryset
