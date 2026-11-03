from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.conf import settings 
import uuid
from datetime import timedelta

from django.utils import timezone


def activation_token_expiry():
    return timezone.now() + timedelta(hours=24)


class UserManager(DjangoUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        return super().create_superuser(
            username,
            email=email,
            password=password,
            **extra_fields,
        )


# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        ADVISOR = "asesor", "Asesor"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADVISOR)
    failed_attempts = models.PositiveIntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    phone = models.CharField(max_length=32, blank=True, default="")
    deactivation_reason = models.TextField(blank=True, default="")

    objects = UserManager()


class UserActivationToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activation_tokens",
    )
    token_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=activation_token_expiry)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Activation token for user {self.user_id}"
class Property(models.Model):
    #The class about every property.
    # We create 
    OPERATION_CHOICES = [('venta','Venta'),('arriendo','Arriendo'),]
    PROPERTY_TYPES = [('casa','Casa'),('departamento','Departamento'),('local','Local Comercial'),('terreno','Terreno'),]
    STATUS_CHOICES = [('captacion','En captación'),('disponible','Disponible'),('reservador','Reservado'),('vendido', 'Vendido'),('arrendado', 'Arrendado'),('no_disponible', 'No disponible'),]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='departamento')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='captacion') # We add the status field to our model, for better handle errors
    
    price = models.DecimalField(max_digits=12, decimal_places=2)
    area_m2 = models.FloatField()
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    parking_spaces = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=500)
    # HU-05: Coordenadas exactas capturadas con el mapa (6 decimales ~ 10 cm)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    #HU-01 Y HU-02 : Asesor captador y responsable inicial
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='properties'  # <-- Se corrigió 'realted_name'
    )
    
    # HU-09: Motivo  de salida del mercado si pasa a No Disponible
    unavailability_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        # Definimos nuestra respuesta en string con un simple estatus y titulo.
        return f"{self.title} ({self.status})"
    
class PropertyImage(models.Model): #We create the model for the images of our properties
    '''
    Modelo para guardar multiples imagnees por cada propiedad por medio de una FK a Property
    '''
    property = models.ForeignKey( #La conexion directa de Property(model) con las imagenes como FK.
        Property,
        on_delete=models.CASCADE,
        related_name='images'
    )
    
    image = models.ImageField(upload_to='properties/images/')#Folder de guardado de imagenes
    caption = models.CharField(max_length=150, blank=True, null=True) # Descripcion
    uploaded_at = models.DateTimeField(auto_now_add=True) #Info de carga.
    
    def __str__(self):
        return f"Imagen de {self.property.title}" 
    #Nuestro ToString de nuestra clase