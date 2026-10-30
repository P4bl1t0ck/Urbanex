import copy
import json
from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import Property
from .engine import (
    THETA_V1,
    EngineError,
    Sample,
    compute,
    round_to_hundreds,
    same_zone,
    validate_params,
)
from .models import Appraisal, EngineParameters

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


def sample(id, price, area, status='vendido', property_type='departamento', lat=None, lon=None):
    return Sample(id=id, property_type=property_type, status=status, price=Decimal(price),
                  area=Decimal(area), latitude=lat, longitude=lon)


class EngineCalculatorTests(SimpleTestCase):
    '''Nucleo puro del motor (DS-21). El ejemplo es el de la §8 del documento.'''

    def setUp(self):
        self.subject = sample(100, '148000', '95', status='captacion')
        self.example = [
            sample(1, '150000', '100', status='disponible'),
            sample(2, '128000', '80', status='disponible'),
            sample(3, '168000', '120'),
            sample(4, '139500', '90'),
            sample(5, '92000', '90', status='disponible'),
        ]

    def test_worked_example_of_ds21(self):
        result = compute(self.subject, self.example, THETA_V1, params_version=1)
        snapshot = result.snapshot
        self.assertEqual(result.suggested_value, Decimal('143861.35'))
        self.assertEqual(result.confidence_level, 'ALTO')
        self.assertFalse(result.is_manual_fallback)
        self.assertEqual(snapshot['weighted_unit_price'], '1514.33')
        self.assertEqual(snapshot['median_unit_price'], '1518.99')
        self.assertEqual(snapshot['cv'], '0.0163')
        self.assertEqual(snapshot['display_value'], '143900')
        self.assertEqual(snapshot['parameters_version'], 1)
        by_id = {row['id']: row for row in snapshot['comparables']}
        self.assertTrue(by_id[5]['discarded'])
        self.assertEqual([by_id[i]['adjusted_unit_price'] for i in (1, 2, 3, 4)],
                         ['1518.99', '1528.36', '1476.92', '1528.77'])
        self.assertEqual(by_id[2]['weight'], '0.817074')

    def test_same_input_gives_same_output_in_any_order(self):
        first = compute(self.subject, self.example, THETA_V1)
        second = compute(self.subject, list(reversed(self.example)), THETA_V1)
        self.assertEqual(first, second)

    def test_high_dispersion_gives_medium_and_keeps_three(self):
        comparables = [self.example[0], self.example[1], sample(3, '120000', '120')]
        result = compute(self.subject, comparables, THETA_V1)
        self.assertEqual(result.confidence_level, 'MEDIO')
        self.assertEqual(result.snapshot['cv'], '0.1979')
        self.assertFalse(any(row['discarded'] for row in result.snapshot['comparables']))

    def test_fewer_than_three_is_manual_with_reference(self):
        result = compute(self.subject, self.example[:2], THETA_V1)
        self.assertIsNone(result.suggested_value)
        self.assertEqual(result.confidence_level, 'BAJO')
        self.assertTrue(result.is_manual_fallback)
        self.assertEqual(len(result.snapshot['comparables']), 2)
        self.assertIn('C-02', result.snapshot['manual_reason'])

    def test_invalid_selections_are_rejected(self):
        with self.assertRaises(EngineError):
            compute(self.subject, self.example + [sample(6, '1000', '10')], THETA_V1)
        with self.assertRaises(EngineError):
            compute(self.subject, self.example[:2] + [sample(7, '1000', '10', property_type='casa')], THETA_V1)
        with self.assertRaises(EngineError):
            compute(self.subject, self.example[:2] + [self.subject], THETA_V1)

    def test_factor_can_be_disabled_per_property_type(self):
        theta = copy.deepcopy(THETA_V1)
        theta['factores_por_tipo']['departamento'] = {
            'superficie@1': dict(THETA_V1['factores_por_tipo']['default']['superficie@1'], intensidad='0'),
        }
        result = compute(self.subject, self.example[:4], theta)
        for row in result.snapshot['comparables']:
            self.assertEqual(row['total_factor'], '1.000000')
            self.assertEqual([f['key'] for f in row['factors']], ['superficie@1'])
        # Las casas siguen con los factores por defecto.
        house = sample(200, '1', '95', property_type='casa')
        houses = [sample(i, '150000', '100', property_type='casa') for i in (11, 12, 13)]
        house_rows = compute(house, houses, theta).snapshot['comparables']
        self.assertEqual(house_rows[0]['total_factor'], '1.012658')

    def test_total_factor_is_clamped(self):
        tiny = [sample(i, '50000', '10') for i in (21, 22, 23)]
        rows = compute(self.subject, tiny, THETA_V1).snapshot['comparables']
        self.assertEqual(rows[0]['factors'][1]['value'], '0.833333')  # 1 / 1.20
        self.assertEqual(rows[0]['total_factor'], '0.850000')

    def test_round_to_hundreds(self):
        self.assertEqual(round_to_hundreds(Decimal('143861.35')), Decimal('143900'))
        self.assertEqual(round_to_hundreds(Decimal('143849.99')), Decimal('143800'))
        self.assertEqual(round_to_hundreds(Decimal('143850.00')), Decimal('143900'))

    def test_theta_validation(self):
        validate_params(THETA_V1)
        broken = copy.deepcopy(THETA_V1)
        broken['factores_por_tipo']['default']['inventado@1'] = {}
        with self.assertRaises(ValueError):
            validate_params(broken)
        broken = copy.deepcopy(THETA_V1)
        broken['estados_comparables'].append('captacion')
        with self.assertRaises(ValueError):
            validate_params(broken)
        broken = copy.deepcopy(THETA_V1)
        del broken['factores_por_tipo']['default']
        with self.assertRaises(ValueError):
            validate_params(broken)

    def test_same_zone_uses_radius_and_requires_coordinates(self):
        carolina = sample(1, '1', '1', lat=Decimal('-0.185700'), lon=Decimal('-78.483600'))
        near = sample(2, '1', '1', lat=Decimal('-0.190000'), lon=Decimal('-78.480000'))
        tumbaco = sample(3, '1', '1', lat=Decimal('-0.211700'), lon=Decimal('-78.403300'))
        self.assertTrue(same_zone(carolina, near, THETA_V1))
        self.assertFalse(same_zone(carolina, tumbaco, THETA_V1))
        self.assertFalse(same_zone(carolina, sample(4, '1', '1'), THETA_V1))


class EngineParametersTests(AppraisalTestMixin, TestCase):
    def test_theta_v1_is_active_after_migration(self):
        active = EngineParameters.active()
        self.assertEqual(active.version, 1)
        self.assertEqual(active.parameters, THETA_V1)
        self.assertIn('cv_max', active.sources)

    def test_version_is_immutable_and_not_deletable(self):
        active = EngineParameters.active()
        active.parameters = dict(active.parameters, alfa='0')
        with self.assertRaises(ValidationError):
            active.save()
        with self.assertRaises(ValidationError):
            EngineParameters.active().delete()
        self.assertEqual(EngineParameters.active().parameters['alfa'], '5')

    def test_new_version_is_activated_and_history_kept(self):
        theta = copy.deepcopy(THETA_V1)
        theta['alfa'] = '0'
        second = EngineParameters.create_version(parameters=theta, created_by=self.admin,
                                                 note='Promedio simple')
        self.assertEqual(second.version, 2)
        self.assertEqual(EngineParameters.active().pk, second.pk)
        self.assertFalse(EngineParameters.objects.get(version=1).is_active)

        EngineParameters.objects.get(version=1).activate()
        self.assertEqual(EngineParameters.active().version, 1)
        self.assertEqual(EngineParameters.objects.filter(is_active=True).count(), 1)

    def test_invalid_theta_is_rejected(self):
        theta = copy.deepcopy(THETA_V1)
        theta['cv_max'] = '2'
        with self.assertRaises(ValidationError):
            EngineParameters.create_version(parameters=theta, created_by=self.admin)
        self.assertEqual(EngineParameters.objects.count(), 1)


class EngineParametersAdminTests(AppraisalTestMixin, TestCase):
    '''V-25: el rol admin (staff, sin superusuario, sin permisos de modelo) gestiona theta.'''
    changelist_url = '/admin/appraisals/engineparameters/'

    def test_role_admin_without_model_permissions_sees_and_adds_versions(self):
        self.admin.is_staff = True
        self.admin.save(update_fields=['is_staff'])
        self.client.force_login(self.admin)

        self.assertContains(self.client.get('/admin/'), self.changelist_url)
        self.assertEqual(self.client.get(self.changelist_url).status_code, 200)
        self.assertEqual(self.client.get(self.changelist_url + 'add/').status_code, 200)

        theta = copy.deepcopy(THETA_V1)
        theta['alfa'] = '0'
        response = self.client.post(self.changelist_url + 'add/', {
            'parameters': json.dumps(theta),
            'sources': json.dumps(EngineParameters.active().sources),
            'note': 'Promedio simple',
        })
        self.assertEqual(response.status_code, 302)
        active = EngineParameters.active()
        self.assertEqual(active.version, 2)
        self.assertEqual(active.created_by, self.admin)

    def test_staff_advisor_cannot_see_theta(self):
        self.agent.is_staff = True
        self.agent.save(update_fields=['is_staff'])
        self.client.force_login(self.agent)

        self.assertNotContains(self.client.get('/admin/'), self.changelist_url)
        self.assertEqual(self.client.get(self.changelist_url).status_code, 403)
        self.assertEqual(self.client.get(self.changelist_url + 'add/').status_code, 403)


class SetupComparablesDemoCommandTests(TestCase):
    def run_command(self):
        call_command('setup_comparables_demo', stdout=StringIO())

    def synthetic(self, property_type):
        return Property.objects.filter(title__startswith='[COMP-SINT]', property_type=property_type)

    @override_settings(DEBUG=False)
    def test_refuses_outside_development(self):
        with self.assertRaises(CommandError):
            self.run_command()

    @override_settings(DEBUG=True)
    def test_creates_sold_market_data_once(self):
        self.run_command()
        self.run_command()
        synthetic = Property.objects.filter(title__startswith='[COMP-SINT]')
        self.assertEqual(synthetic.count(), 11)
        self.assertEqual(set(synthetic.values_list('status', flat=True)), {'vendido'})
        self.assertFalse(synthetic.exclude(agent=None).exists())
        response = APIClient().get('/api/auth/properties/')
        self.assertFalse(any(row['title'].startswith('[COMP-SINT]') for row in response.data))

    @override_settings(DEBUG=True)
    def test_scenarios_cover_high_medium_and_manual(self):
        self.run_command()
        carolina = sample(1000, '148000', '95', status='captacion',
                          lat=Decimal('-0.185700'), lon=Decimal('-78.483600'))
        flats = [Sample.from_property(p) for p in self.synthetic('departamento')]
        self.assertTrue(all(same_zone(carolina, flat, THETA_V1) for flat in flats))
        example = [flat for flat in flats if flat.area != Decimal('95.0')]  # los 5 de DS-21 §8
        result = compute(carolina, example, THETA_V1)
        self.assertEqual(result.suggested_value, Decimal('143861.35'))
        self.assertEqual(result.confidence_level, 'ALTO')

        cumbaya = sample(1001, '285000', '240', status='captacion', property_type='casa')
        houses = [Sample.from_property(p) for p in self.synthetic('casa')]
        self.assertEqual(compute(cumbaya, houses, THETA_V1).confidence_level, 'MEDIO')

        mariscal = sample(1002, '120000', '80', status='captacion', property_type='local')
        shops = [Sample.from_property(p) for p in self.synthetic('local')]
        self.assertTrue(compute(mariscal, shops, THETA_V1).is_manual_fallback)
        self.assertFalse(self.synthetic('terreno').exists())


class AppraisalEngineApiTests(AppraisalTestMixin, TestCase):
    '''HU-04 (candidatos) y HU-06 (avaluo calculado al crear), DS-21.'''
    url = '/api/appraisals/'

    def setUp(self):
        super().setUp()
        with override_settings(DEBUG=True):
            call_command('setup_comparables_demo', stdout=StringIO())
        self.subject = Property.objects.create(
            agent=self.agent, title='Departamento sujeto', description='Prueba',
            property_type='departamento', price=148000, area_m2=95, location='La Carolina',
            latitude=Decimal('-0.185700'), longitude=Decimal('-78.483600'),
        )
        # '[COMP-SINT] Departamento vendido La Carolina 5 (atipico)' -> '5'
        self.flats = {
            p.title.split('Carolina ')[1][0]: p
            for p in Property.objects.filter(title__startswith='[COMP-SINT] Departamento')
        }
        self.example_ids = [self.flats[k].id for k in ('1', '2', '3', '4', '5')]
        self.client.force_authenticate(user=self.agent)

    def test_candidates_are_same_type_zone_and_ranked(self):
        response = self.client.get(f'{self.url}candidates/', {'property': self.subject.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data['can_calculate'])
        self.assertEqual(data['parameters_version'], 1)
        self.assertEqual(len(data['candidates']), 6)
        self.assertEqual({row['property_type'] for row in data['candidates']}, {'departamento'})
        # El de 95 m2 (identico en superficie) va primero; el de 120 m2 queda fuera de los 5.
        self.assertEqual(data['candidates'][0]['id'], self.flats['6'].id)
        self.assertEqual(len(data['suggested_ids']), 5)
        self.assertNotIn(self.flats['3'].id, data['suggested_ids'])

    def test_candidates_exclude_stale_data_and_explain_blockers(self):
        Property.objects.filter(title__startswith='[COMP-SINT] Departamento').update(
            updated_at=timezone.now() - timedelta(days=400))
        response = self.client.get(f'{self.url}candidates/', {'property': self.subject.id})
        self.assertFalse(response.data['can_calculate'])
        self.assertIn('C-02', response.data['blocker'])

        response = self.client.get(f'{self.url}candidates/', {'property': self.property.id})
        self.assertFalse(response.data['can_calculate'])
        self.assertIn('coordenadas', response.data['blocker'])

    def test_candidates_of_other_agent_property_are_hidden(self):
        self.client.force_authenticate(user=self.other_agent)
        response = self.client.get(f'{self.url}candidates/', {'property': self.subject.id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_with_comparables_runs_the_engine(self):
        response = self.client.post(self.url, {
            'property': self.subject.id, 'comparables': self.example_ids,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['suggested_value'], '143861.35')
        self.assertEqual(response.data['suggested_value_display'], '143900.00')
        self.assertEqual(response.data['confidence_level'], 'ALTO')
        self.assertFalse(response.data['is_manual_fallback'])
        self.assertEqual(response.data['engine_parameters_version'], 1)
        self.assertEqual(len(response.data['comparables_snapshot']['comparables']), 5)

        appraisal = Appraisal.objects.get(pk=response.data['id'])
        appraisal.calibrate(calibrated_value=Decimal('148000.00'), final_justification='Ajuste.')
        appraisal.approve()
        self.assertEqual(appraisal.difference_amount, Decimal('4138.65'))
        self.assertEqual(appraisal.difference_percentage, Decimal('2.88'))

    def test_two_comparables_give_manual_with_reference(self):
        response = self.client.post(self.url, {
            'property': self.subject.id, 'comparables': self.example_ids[:2],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['suggested_value'])
        self.assertTrue(response.data['is_manual_fallback'])
        self.assertIsNone(response.data['engine_parameters_version'])
        self.assertEqual(len(response.data['comparables_snapshot']['comparables']), 2)

    def test_invalid_comparables_are_rejected_without_creating(self):
        house = Property.objects.filter(title__startswith='[COMP-SINT] Casa').first()
        for comparables in ([*self.example_ids[:2], house.id],
                            [*self.example_ids[:2], self.property.id],
                            self.example_ids + [self.flats['6'].id]):
            response = self.client.post(self.url, {
                'property': self.subject.id, 'comparables': comparables,
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('comparables', response.data)
        self.assertFalse(Appraisal.objects.filter(property=self.subject).exists())

    def test_engine_fields_stay_immutable(self):
        response = self.client.post(self.url, {
            'property': self.subject.id, 'comparables': self.example_ids,
        }, format='json')
        detail = f'{self.url}{response.data["id"]}/'
        response = self.client.patch(detail, {'suggested_value': '1.00',
                                              'final_justification': 'x'}, format='json')
        self.assertEqual(response.data['suggested_value'], '143861.35')
