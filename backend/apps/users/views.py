from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import action
from .serializers import LoginSerializer, PropertySerializer, PropertyImageSerializer
from .models import Property, PropertyImage
from rest_framework import permissions
from apps.appraisals.models import Appraisal
from apps.documents.models import Document

User = get_user_model()

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
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=email).first()

        if user and user.is_locked:
            return Response({"detail": "Cuenta bloqueada. Contacta al administrador."}, status=403)

        if not user or not user.check_password(password): #Regla de negocio.
            if user:
                user.failed_attempts += 1
                if user.failed_attempts >= 5:
                    user.is_locked = True
                user.save()
            return Response({"detail": "Credenciales inválidas."}, status=401)

        user.failed_attempts = 0
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
        })
        
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
