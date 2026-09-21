from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin","Administrador"),
        ("captador","Captador"),
        ("cliente","Cliente"),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="cliente")
    failed_attempts = models.PositiveIntegerField(default=0)
    is_locked = models.BooleanField(default=False)