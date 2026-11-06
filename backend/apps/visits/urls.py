from rest_framework.routers import DefaultRouter

from .views import AvailabilityExceptionViewSet, AvailabilityViewSet

router = DefaultRouter()
router.register(r'availability', AvailabilityViewSet, basename='availability')
router.register(r'exceptions', AvailabilityExceptionViewSet, basename='availability-exception')

urlpatterns = router.urls
