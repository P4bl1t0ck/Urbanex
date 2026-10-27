from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import Property
from .models import Appraisal

User = get_user_model()


class AppraisalTestMixin:
    def setUp(self):
        self.client = APIClient()
        self.agent = User.objects.create_user(
            username='asesor.avaluo', email='asesor.avaluo@urbanex.ec',
            password='Password123!', role='asesor',
        )
        self.other_agent = User.objects.create_user(
            username='otro.asesor', email='otro.asesor@urbanex.ec',
            password='Password123!', role='asesor',
        )
        self.admin = User.objects.create_user(
            username='admin.avaluo', email='admin.avaluo@urbanex.ec',
            password='Password123!', role='admin',
        )
        self.property = Property.objects.create(
            agent=self.agent, title='Casa para avaluo', description='Prueba',
            property_type='casa', price=150000, area_m2=120, location='Cumbayá',
        )

    def approved_appraisal(self, value='145000.00'):
        appraisal = Appraisal.create_draft(property=self.property, agent=self.agent)
        appraisal.calibrate(calibrated_value=Decimal(value), final_justification='Valor de mercado.')
        return appraisal.approve()


class AppraisalModelTests(AppraisalTestMixin, TestCase):
    def test_draft_uses_manual_fallback_placeholder(self):
        appraisal = Appraisal.create_draft(property=self.property, agent=self.agent)
        self.assertEqual(appraisal.status, Appraisal.Status.BORRADOR)
        self.assertIsNone(appraisal.suggested_value)
        self.assertTrue(appraisal.is_manual_fallback)
        self.assertEqual(appraisal.confidence_level, Appraisal.ConfidenceLevel.BAJO)
        self.assertEqual(appraisal.comparables_snapshot, [])
        self.assertTrue(appraisal.folio.startswith('AV-'))

    def test_only_one_open_draft_per_property(self):
        Appraisal.create_draft(property=self.property, agent=self.agent)
        with self.assertRaises(ValidationError):
            Appraisal.create_draft(property=self.property, agent=self.agent)

    def test_approve_requires_calibration(self):
        appraisal = Appraisal.create_draft(property=self.property, agent=self.agent)
        with self.assertRaises(ValidationError):
            appraisal.approve()
        appraisal.refresh_from_db()
        self.assertEqual(appraisal.status, Appraisal.Status.BORRADOR)

    def test_approve_without_suggested_value_leaves_differences_null(self):
        appraisal = self.approved_appraisal()
        self.assertEqual(appraisal.status, Appraisal.Status.APROBADO)
        self.assertIsNotNone(appraisal.approved_at)
        self.assertIsNone(appraisal.difference_amount)
        self.assertIsNone(appraisal.difference_percentage)

    def test_approve_computes_differences_when_engine_value_exists(self):
        # Simula el valor del motor que llegara con HU-06 (se asigna antes del primer save).
        appraisal = Appraisal(property=self.property, agent=self.agent,
                              suggested_value=Decimal('100000.00'), is_manual_fallback=False)
        appraisal.save()
        appraisal.calibrate(calibrated_value=Decimal('110000.00'), final_justification='Ajuste.')
        appraisal.approve()
        self.assertEqual(appraisal.difference_amount, Decimal('10000.00'))
        self.assertEqual(appraisal.difference_percentage, Decimal('10.00'))

    def test_approved_appraisal_cannot_be_saved(self):
        appraisal = self.approved_appraisal()
        appraisal.calibrated_value = Decimal('1.00')
        with self.assertRaises(ValidationError):
            appraisal.save()
        appraisal.refresh_from_db()
        self.assertEqual(appraisal.calibrated_value, Decimal('145000.00'))

    def test_approved_appraisal_cannot_be_recalibrated_or_reapproved(self):
        appraisal = self.approved_appraisal()
        with self.assertRaises(ValidationError):
            appraisal.calibrate(calibrated_value=Decimal('1.00'))
        with self.assertRaises(ValidationError):
            appraisal.approve()

    def test_approved_appraisal_cannot_be_bulk_updated(self):
        self.approved_appraisal()
        with self.assertRaises(ValidationError):
            Appraisal.objects.filter(property=self.property).update(calibrated_value=Decimal('1.00'))

    def test_draft_engine_fields_are_immutable(self):
        appraisal = Appraisal.create_draft(property=self.property, agent=self.agent)
        appraisal.suggested_value = Decimal('99999.00')
        with self.assertRaises(ValidationError):
            appraisal.save()
        with self.assertRaises(ValidationError):
            Appraisal.objects.filter(pk=appraisal.pk).update(confidence_level='ALTO')

    def test_appraisals_cannot_be_deleted(self):
        appraisal = Appraisal.create_draft(property=self.property, agent=self.agent)
        with self.assertRaises(ValidationError):
            appraisal.delete()
        with self.assertRaises(ValidationError):
            Appraisal.objects.all().delete()
        self.assertTrue(Appraisal.objects.filter(pk=appraisal.pk).exists())

    def test_new_draft_allowed_after_approval(self):
        first = self.approved_appraisal()
        second = Appraisal.create_draft(property=self.property, agent=self.agent)
        self.assertNotEqual(first.pk, second.pk)
        self.assertEqual(Appraisal.objects.filter(property=self.property).count(), 2)


class AppraisalApiTests(AppraisalTestMixin, TestCase):
    url = '/api/appraisals/'

    def test_owner_creates_draft(self):
        self.client.force_authenticate(user=self.agent)
        response = self.client.post(self.url, {'property': self.property.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'BORRADOR')
        self.assertIsNone(response.data['suggested_value'])
        self.assertTrue(response.data['is_manual_fallback'])
        self.assertEqual(response.data['agent'], self.agent.id)

    def test_other_agent_cannot_create_or_see(self):
        Appraisal.create_draft(property=self.property, agent=self.agent)
        self.client.force_authenticate(user=self.other_agent)
        response = self.client.post(self.url, {'property': self.property.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(self.url)
        self.assertEqual(response.data, [])

    def test_admin_sees_all(self):
        Appraisal.create_draft(property=self.property, agent=self.agent)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {'property': self.property.id})
        self.assertEqual(len(response.data), 1)

    def test_anonymous_rejected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_calibrate_and_approve_flow(self):
        appraisal = Appraisal.create_draft(property=self.property, agent=self.agent)
        self.client.force_authenticate(user=self.agent)
        detail = f'{self.url}{appraisal.id}/'

        response = self.client.patch(detail, {
            'calibrated_value': '148000.00',
            'final_justification': 'Comparado con ventas recientes de la zona.',
            'suggested_value': '1.00',  # campo del motor: se ignora
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['calibrated_value'], '148000.00')
        self.assertIsNone(response.data['suggested_value'])

        response = self.client.post(f'{detail}approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'APROBADO')

        response = self.client.patch(detail, {'calibrated_value': '1.00'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(f'{detail}approve/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        appraisal.refresh_from_db()
        self.assertEqual(appraisal.calibrated_value, Decimal('148000.00'))

    def test_approve_without_calibration_rejected(self):
        appraisal = Appraisal.create_draft(property=self.property, agent=self.agent)
        self.client.force_authenticate(user=self.agent)
        response = self.client.post(f'{self.url}{appraisal.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('calibrated_value', response.data)

    def test_put_and_delete_not_allowed(self):
        appraisal = Appraisal.create_draft(property=self.property, agent=self.agent)
        self.client.force_authenticate(user=self.agent)
        detail = f'{self.url}{appraisal.id}/'
        self.assertEqual(self.client.put(detail, {}, format='json').status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(detail).status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
