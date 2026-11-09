from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AgendaView,
    AvailabilityExceptionViewSet,
    AvailabilityViewSet,
    PropertyFreeSlotsView,
    PublicVisitView,
    VisitOutcomeView,
    VisitRequestView,
)

router = DefaultRouter()
router.register(r'availability', AvailabilityViewSet, basename='availability')
router.register(r'exceptions', AvailabilityExceptionViewSet, basename='availability-exception')

urlpatterns = [
    path('properties/<int:property_id>/free-slots/', PropertyFreeSlotsView.as_view(),
         name='property-free-slots'),
    path('properties/<int:property_id>/request/', VisitRequestView.as_view(),
         name='property-visit-request'),
    path('public/<uuid:token>/', PublicVisitView.as_view(), name='public-visit'),
    path('<int:visit_id>/outcome/', VisitOutcomeView.as_view(), name='visit-outcome'),
    path('agenda/', AgendaView.as_view(), name='agenda'),
] + router.urls
