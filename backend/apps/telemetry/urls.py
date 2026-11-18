from django.urls import path
from .views import DevStatsView, MapLoadView

urlpatterns = [
    path('dev/stats/', DevStatsView.as_view(), name='dev-stats'),
    path('telemetry/map-loads/', MapLoadView.as_view(), name='map-loads'),
]
