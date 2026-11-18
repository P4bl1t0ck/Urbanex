from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.documents.models import Document
from apps.users.models import Property, PropertyImage
from .models import DailyMapLoads


class TelemetryTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin = get_user_model().objects.create_user(username='metrics_admin', email='admin@example.test', role='admin')
        self.advisor = get_user_model().objects.create_user(username='metrics_advisor', email='advisor@example.test', role='asesor', is_staff=True)
        self.property = Property.objects.create(title='Mapa de prueba', status='disponible', price=100000,
                                                area_m2=100, location='Quito', property_type='casa', agent=self.advisor)
        self.client = APIClient()

    def test_stats_requires_admin_role_not_staff(self):
        self.assertIn(self.client.get('/api/dev/stats/').status_code, [401, 403])
        self.client.force_authenticate(self.advisor)
        self.assertEqual(self.client.get('/api/dev/stats/').status_code, 403)
        self.client.force_authenticate(self.admin)
        response = self.client.get('/api/dev/stats/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        self.assertIsNone(response.data['images']['storage_bytes'])
        self.assertEqual(response.data['documents']['registered_bytes_all_versions'], 0)
        self.assertFalse(response.data['maps']['billing_equivalent'])

    def test_public_counts_aggregate_without_property_or_personal_data(self):
        payload = {'property_id': self.property.pk, 'screen': 'detail', 'provider': 'leaflet'}
        for _ in range(2):
            self.assertEqual(self.client.post('/api/telemetry/map-loads/', payload, format='json').status_code, 204)
        self.assertEqual(DailyMapLoads.objects.count(), 1)
        self.assertEqual(DailyMapLoads.objects.get().loads, 2)
        self.client.force_authenticate(self.admin)
        data = self.client.get('/api/dev/stats/').data
        self.assertEqual(data['maps']['total'], 2)
        self.assertEqual(set(data['maps']['daily'][0]), {'day', 'screen', 'provider', 'loads'})

    def test_private_properties_and_invalid_dimensions_do_not_count(self):
        payload = {'property_id': self.property.pk, 'screen': 'detail', 'provider': 'leaflet'}
        self.property.status = 'captacion'
        self.property.save()
        self.assertEqual(self.client.post('/api/telemetry/map-loads/', payload, format='json').status_code, 404)
        self.assertEqual(self.client.post('/api/telemetry/map-loads/', {**payload, 'provider': 'google'}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/telemetry/map-loads/', {**payload, 'screen': 'anything'}, format='json').status_code, 400)
        self.assertFalse(DailyMapLoads.objects.exists())

    def test_report_requires_csrf_and_throttles(self):
        payload = {'property_id': self.property.pk, 'screen': 'detail', 'provider': 'leaflet'}
        client = APIClient(enforce_csrf_checks=True)
        self.assertEqual(client.post('/api/telemetry/map-loads/', payload, format='json').status_code, 403)
        client.get('/api/auth/csrf/')
        token = client.cookies['csrftoken'].value
        for _ in range(30):
            self.assertEqual(client.post('/api/telemetry/map-loads/', payload, format='json', HTTP_X_CSRFTOKEN=token).status_code, 204)
        self.assertEqual(client.post('/api/telemetry/map-loads/', payload, format='json', HTTP_X_CSRFTOKEN=token).status_code, 429)

    def test_report_only_current_month_through_today(self):
        today = timezone.localdate()
        DailyMapLoads.objects.create(day=today.replace(day=1) - timedelta(days=1), screen='detail', loads=9)
        DailyMapLoads.objects.create(day=today + timedelta(days=1), screen='detail', loads=8)
        DailyMapLoads.objects.create(day=today, screen='detail', loads=3)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get('/api/dev/stats/').data['maps']['total'], 3)

    def test_inventory_counts_local_cloud_and_all_document_versions(self):
        PropertyImage.objects.create(property=self.property, image='properties/images/example.png')
        PropertyImage.objects.create(property=self.property, image='cloudinary/demo/' + 'a' * 32)
        for version, size in [(1, 100), (2, 250)]:
            Document.objects.create(
                property=self.property, doc_type='OTRO', file=f'documents/example{version}.pdf',
                original_filename='example.pdf', file_size_bytes=size, mime_type='application/pdf',
                version=version, is_current_version=version == 2, uploaded_by=self.advisor,
                issue_date=timezone.localdate(), expiration_date=timezone.localdate() + timedelta(days=30),
            )
        self.client.force_authenticate(self.admin)
        data = self.client.get('/api/dev/stats/').data
        self.assertEqual(data['images']['registered_files'], 2)
        self.assertEqual(data['images']['cloudinary_references'], 1)
        self.assertEqual(data['images']['local_references'], 1)
        self.assertEqual(data['documents']['registered_versions'], 2)
        self.assertEqual(data['documents']['current_versions'], 1)
        self.assertEqual(data['documents']['registered_bytes_all_versions'], 350)
