from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from .serializers import LoginSerializer, PropertySerializer, PropertyImageSerializer
from .models import Property, PropertyImage

User = get_user_model()

'''
The Views work to enrute, fetch, grab, get and retrive the information from the database and send it to the Template. 
MVT (Model-View-Template): User -> (View <-> Database) --> Template ->> User.
MVC (Model-View.Controller): User -> (View -> Model -> Database) --> View ->> User.

The main difference between this two patterns designs is a bit tricky, not because they are different, its because they dothe same thing.
Fetch data -> Send it to a Urls, or HTML template and then send it again on a template to the user again (template.)
Same MVC patter as the MVT pattern on django and on comparassion with  laravel(.php)

So that´s why some of the functions and methods inside the classes, are so similar to a query to the database.

'''
class PropertyImageViewSet(viewsets.ModelViewSet): #We pass the viewsets
    queryset  = PropertyImage.objects.all() # Mismas funciones que las de un controlador.
    serializer_class = PropertyImageSerializer
    permissions_classes = (MultiPartParser, FormParser) # Nesecario para procesas imagenes
    
    def create(self, request, *arsg, **kwargs):
        #Permite crear un objeto para la imagen y subir la imagen.
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

        if not user or not user.check_password(password):
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
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self): #
        user = self.request.user
        if user.role == 'admin':
            return Property.objects.all()
        return Property.objects.filter(agent=user)
    
    ##This function have a change on status = 'captacion', check it out if it part of the bussiness nesecity.
    def perform_create(self, serializer): # Revisar sobre un inesperado error al momento de intentar crear una propiedad.
        # TODO: Verificar en las historias de usuario si se requiere un campo 'status' o 'property_type' para la etapa de captación.
        # serializer.save(agent=self.request.user, status='captacion')
        serializer.save(agent=self.request.user, property_type='captacion') #It must have to be captacion
        
class PropertyPublishView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            property_obj = Property.objects.get(pk=pk)
        except Property.DoesNotExist:
            return Response({"detail": "Propiedad no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        property_obj.status = 'disponible'
        property_obj.save()

        return Response(
            {
                "detail": "Propiedad publicada con éxito. Ahora es visible en el catálogo público.",
                "status": property_obj.status
            },
            status=status.HTTP_200_OK
        )
class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    
