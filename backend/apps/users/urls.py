from django.urls import path
from .views import LoginView, PropertyListCreateView, PropertyDetailView, PropertyPublishView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path('<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    path('<int:pk>/publish/', PropertyPublishView.as_view(), name='property-publish'),
]