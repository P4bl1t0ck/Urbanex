from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.documents.models import Document
from apps.users.models import Property, PropertyImage
from .models import DailyMapLoads


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_active and request.user.role == 'admin')


class MapLoadThrottle(AnonRateThrottle):
    rate = '30/min'
    scope = 'map_loads'


class MapLoadInput(serializers.Serializer):
    property_id = serializers.IntegerField(min_value=1)
    screen = serializers.ChoiceField(choices=['detail'])
    provider = serializers.ChoiceField(choices=['leaflet'])


@method_decorator(csrf_protect, name='dispatch')
class MapLoadView(APIView):
    # Public anonymous report: intentionally no access token or personal identifiers.
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [MapLoadThrottle]

    def post(self, request):
        payload = MapLoadInput(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data
        if not Property.objects.filter(pk=data['property_id'], status__in=['disponible', 'reservador']).exists():
            return Response({'detail': 'Propiedad no disponible.'}, status=404)
        with transaction.atomic():
            counter, _ = DailyMapLoads.objects.get_or_create(
                day=timezone.localdate(), screen=data['screen'], provider=data['provider'],
            )
            DailyMapLoads.objects.filter(pk=counter.pk).update(loads=F('loads') + 1)
        return Response(status=204)


class DevStatsView(APIView):
    permission_classes = [AdminOnly]

    def get(self, request):
        today = timezone.localdate()
        month_start = today.replace(day=1)
        daily = list(DailyMapLoads.objects.filter(day__gte=month_start, day__lte=today)
                     .order_by('day', 'screen', 'provider').values('day', 'screen', 'provider', 'loads'))
        images = PropertyImage.objects.exclude(image='')
        cloud = images.filter(image__startswith='cloudinary/').count()
        documents = Document.objects.all()
        response = Response({
            'generated_at': timezone.now(),
            'period': {'from': month_start, 'to': today, 'timezone': str(timezone.get_current_timezone())},
            'maps': {
                'measurement': 'client_reported_initializations',
                'total': sum(row['loads'] for row in daily), 'daily': daily,
                'billing_equivalent': False,
                'limitations': 'Reportes del navegador: pueden faltar o repetirse. No son cargas facturadas ni usuarios únicos.',
            },
            'images': {
                'registered_files': images.count(), 'cloudinary_references': cloud,
                'local_references': images.count() - cloud,
                'storage_bytes': None, 'bandwidth_bytes': None, 'transformations': None,
            },
            'documents': {
                'registered_versions': documents.count(),
                'current_versions': documents.filter(is_current_version=True).count(),
                'registered_bytes_all_versions': documents.aggregate(total=Sum('file_size_bytes'))['total'] or 0,
                'storage': 'private_local',
            },
            'unmeasured': ['email_delivery', 'database_size', 'hosting_traffic', 'provider_billing', 'orphan_files'],
            'inventory_note': 'Inventario de registros, no auditoría de archivos existentes ni consumo oficial de proveedores.',
        })
        response['Cache-Control'] = 'private, no-store'
        return response
