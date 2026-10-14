from django.urls import path
from .views import LoginView, PropertyListCreateView, PropertyDetailView, PropertyPublishView, PropertyImageViewSet , PropertyImageViewSet
from rest_framework.routers import DefaultRouter


#Tuvimos que modificar todo el patron de rutas para que se reparer un problema de el inicio de sesion y eel login.
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("properties/", PropertyListCreateView.as_view(), name="property-list-create"),  # <-- Agregada esta ruta
    path("properties/<int:pk>/", PropertyDetailView.as_view(), name="property-detail"), #No aparece la ruta por error
    path("properties/<int:pk>/publish/", PropertyPublishView.as_view(), name="property-publish"),
]

router = DefaultRouter()
router.register(r'properties', PropertyImageViewSet, basename='property')
router.register(r'property-images', PropertyImageViewSet, basename='property-image')

urlpatterns = router.urls