from django.urls import path
from .views import (
    CsrfCookieView,
    LoginView,
    LogoutView,
    MyPropertiesView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PropertyDetailView,
    PropertyImageViewSet,
    PropertyListCreateView,
    PropertyPublicationRequirementsView,
    PropertyPublishView,
    PropertyWithdrawalView,
    PropertyReactivationView,
    UserActivationView,
    UserDeactivateView,
    UserDetailView,
    UserListCreateView,
    UserResendActivationView,
    UserUnlockView,
)
from rest_framework.routers import DefaultRouter


#Tuvimos que modificar todo el patron de rutas para que se reparer un problema de el inicio de sesion y eel login.
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("csrf/", CsrfCookieView.as_view(), name="csrf-cookie"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password-reset/request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/activate/", UserActivationView.as_view(), name="user-activate"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/deactivate/", UserDeactivateView.as_view(), name="user-deactivate"),
    path("users/<int:pk>/unlock/", UserUnlockView.as_view(), name="user-unlock"),
    path("users/<int:pk>/resend-activation/", UserResendActivationView.as_view(), name="user-resend-activation"),
    path("properties/", PropertyListCreateView.as_view(), name="property-list-create"),  # <-- Agregada esta ruta
    path("properties/mine/", MyPropertiesView.as_view(), name="my-properties"),
    path("properties/<int:pk>/", PropertyDetailView.as_view(), name="property-detail"), #No aparece la ruta por error
    path("properties/<int:pk>/publish/", PropertyPublishView.as_view(), name="property-publish"),
    path("properties/<int:pk>/withdraw/", PropertyWithdrawalView.as_view(), name="property-withdraw"),
    path("properties/<int:pk>/reactivate/", PropertyReactivationView.as_view(), name="property-reactivate"),
    path(
        "properties/<int:pk>/publication-requirements/",
        PropertyPublicationRequirementsView.as_view(),
        name="property-publication-requirements",
    ),
]

router = DefaultRouter()
router.register(r'property-images', PropertyImageViewSet, basename='property-image')

urlpatterns += router.urls
