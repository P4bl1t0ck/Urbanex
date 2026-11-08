from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AgendaView,
    AvailabilityExceptionViewSet,
    AvailabilityViewSet,
    PropertyFreeSlotsView,
)

router = DefaultRouter()
router.register(r'availability', AvailabilityViewSet, basename='availability')
router.register(r'exceptions', AvailabilityExceptionViewSet, basename='availability-exception')

urlpatterns = [
    path('properties/<int:property_id>/free-slots/', PropertyFreeSlotsView.as_view(),
         name='property-free-slots'),
    path('agenda/', AgendaView.as_view(), name='agenda'),
] + router.urls
