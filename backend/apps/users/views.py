import hashlib

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from .serializers import (
    LoginSerializer,
    ManagedUserSerializer,
    PropertySerializer,
    PropertyImageSerializer,
    UserActivationSerializer,
    UserDeactivationSerializer,
    send_activation_email,
)
from .models import Property, PropertyImage, UserActivationToken
from apps.appraisals.models import Appraisal
from apps.documents.models import Document

User = get_user_model()


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
class LoginView(APIView):
    def post(self, request): #Post Function WEB
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()
        password = serializer.validated_data["password"]

        user = User.objects.filter(email__iexact=email).first()

        if not user or not user.is_active:
            return Response({"detail": "Credenciales inválidas."}, status=401)

        if user and user.is_locked:
            return Response({"detail": "Cuenta bloqueada. Contacta al administrador."}, status=403)

        if not user.check_password(password): #Regla de negocio.
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.is_locked = True
            user.save(update_fields=["failed_attempts", "is_locked"])
            return Response({"detail": "Credenciales inválidas."}, status=401)

        user.failed_attempts = 0
        user.save(update_fields=["failed_attempts"])

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
        })


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
