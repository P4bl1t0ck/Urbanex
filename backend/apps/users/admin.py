from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin 
from  .models import User, Property, PropertyImage

#Que podemos de gestionar dentro del portal del admin.

# Prevenimos el conflicto desregistrando User si ya existía en el admin.
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserAdmin)
admin.site.register(Property)
admin.site.register(PropertyImage)
