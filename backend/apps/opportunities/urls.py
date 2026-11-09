from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import OpportunityViewSet, PropertyInterestView, PropertyWhatsAppView

router = DefaultRouter()
router.register(r'', OpportunityViewSet, basename='opportunity')

# Endpoints publicos de la ficha P-07 (lote 4, DS-50), antes de las rutas del router.
urlpatterns = [
    path('public/properties/<int:property_id>/whatsapp/', PropertyWhatsAppView.as_view(),
         name='opportunity-public-whatsapp'),
    path('public/properties/<int:property_id>/interest/', PropertyInterestView.as_view(),
         name='opportunity-public-interest'),
] + router.urls
