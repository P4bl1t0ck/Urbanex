from django.urls import path
from .views import (
    LoginView,
    MyPropertiesView,
    PropertyDetailView,
    PropertyImageViewSet,
    PropertyListCreateView,
    PropertyPublishView,
    UserActivationView,
    UserDeactivateView,
    UserDetailView,
    UserListCreateView,
    UserResendActivationView,
)
from rest_framework.routers import DefaultRouter


#Tuvimos que modificar todo el patron de rutas para que se reparer un problema de el inicio de sesion y eel login.
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/activate/", UserActivationView.as_view(), name="user-activate"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/deactivate/", UserDeactivateView.as_view(), name="user-deactivate"),
    path("users/<int:pk>/resend-activation/", UserResendActivationView.as_view(), name="user-resend-activation"),
    path("properties/", PropertyListCreateView.as_view(), name="property-list-create"),  # <-- Agregada esta ruta
    path("properties/mine/", MyPropertiesView.as_view(), name="my-properties"),
    path("properties/<int:pk>/", PropertyDetailView.as_view(), name="property-detail"), #No aparece la ruta por error
    path("properties/<int:pk>/publish/", PropertyPublishView.as_view(), name="property-publish"),
]

router = DefaultRouter()
router.register(r'property-images', PropertyImageViewSet, basename='property-image')

urlpatterns += router.urls