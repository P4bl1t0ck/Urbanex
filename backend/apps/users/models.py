from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings 

# Create your models here.
class User(AbstractUser):
    # The class about our Users
    ROLE_CHOICES = [
        ("admin","Administrador"),
        ("asesor","Captador"), #Correcion por predefiniciones hechas previamente
        ("cliente","Cliente"),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="cliente")
    failed_attempts = models.PositiveIntegerField(default=0)
    is_locked = models.BooleanField(default=False)
class Property(models.Model):
    #The class about every property.
    # We create 
    OPERATION_CHOICES = [('venta','Venta'),('arriendo','Arriendo'),]
    PROPERTY_TYPES = [('casa','Casa'),('departamento','Deparrtamento'),('local','Local Comercial'),]
    STATUS_CHOICES = [('captacion','En captación'),('disponible','Disponible'),('reservador','Reservado'),('vendido', 'Vendido'),('arrendado', 'Arrendado'),('no_disponible', 'No disponible'),]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=STATUS_CHOICES, default='captacion')
    
    price = models.DecimalField(max_digits=12, decimal_places=2)
    area_m2 = models.FloatField()
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    parking_spaces = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=500)
    
    #HU-01 Y HU-02 : Asesor captador y responsable inicial
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True,
        realted_name='properties'
    )
    
    # HU-09: Motivo  de salida del mercado si pasa a No Disponible
    unavailability_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        # Definimos nuestra respuesta en string con un simple estatus y titulo.
        return f"{self.title} ({self.status})"
    