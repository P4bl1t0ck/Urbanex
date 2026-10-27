from rest_framework.routers import DefaultRouter

from .views import AppraisalViewSet

router = DefaultRouter()
router.register(r'', AppraisalViewSet, basename='appraisal')

urlpatterns = router.urls
