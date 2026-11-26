import uuid
from datetime import datetime, time, timedelta, timezone
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.management import CommandError, call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.opportunities.models import (
    SYSTEM_REASON_CLIENT_PORTAL,
    Contact,
    OriginChannel,
    Opportunity,
)
from apps.users.models import Property
from .models import ECUADOR_TZ, AgentAvailability, AvailabilityException, Visit, ecuador_today
from .services import free_slots
from .views import VisitRequestBurstThrottle

AVAILABILITY_URL = '/api/visits/availability/'
EXCEPTIONS_URL = '/api/visits/exceptions/'


def free_slots_url(property_id):
    return f'/api/visits/properties/{property_id}/free-slots/'

User = get_user_model()


def next_weekday(weekday, weeks_ahead=1):
    '''Fecha de Ecuador del proximo `weekday` (0 = lunes), al menos una semana adelante.'''
    today = ecuador_today()
    return today + timedelta(days=(weekday - today.weekday()) % 7 + 7 * weeks_ahead)


def local(day, hour, minute=0):
    return datetime.combine(day, time(hour, minute), tzinfo=ECUADOR_TZ)


class VisitsTestMixin:
    def setUp(self):
        self.agent = User.objects.create_user(
            username='asesor.visitas', email='asesor.visitas@urbanex.ec',
            password='Password123!', role='asesor', first_name='Ana', last_name='Asesora',
        )
        self.other_agent = User.objects.create_user(
            username='otro.asesor', email='otro.asesor@urbanex.ec',
            password='Password123!', role='asesor',
        )
        self.admin = User.objects.create_user(
            username='admin.visitas', email='admin.visitas@urbanex.ec',
            password='Password123!', role='admin',
        )
        self.client = APIClient()

    def login(self, user):
        self.client.force_authenticate(user=user)

    def rule(self, agent=None, day=0, start=time(9), end=time(12), duration=60):
        return AgentAvailability.objects.create(
            agent=agent or self.agent, day_of_week=day, start_time=start, end_time=end,
            slot_duration_minutes=duration,
        )


# --- HU-22, criterio 1: "Permite definir franjas por dia" (RF-09: minimo 30 minutos) -------------

class AvailabilityRulesTests(VisitsTestMixin, TestCase):
    def test_advisor_defines_a_weekly_slot_and_sees_the_day_name(self):
        self.login(self.agent)
        response = self.client.post(AVAILABILITY_URL, {
            'day_of_week': 0, 'start_time': '09:00', 'end_time': '12:00',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['agent'], self.agent.pk)
        self.assertEqual(response.data['day_name'], 'Lunes')
        self.assertEqual(response.data['slot_duration_minutes'], 60)  # Por defecto
        self.assertEqual(response.data['agent_name'], 'Ana Asesora')

    def test_several_slots_per_day_and_per_week(self):
        self.login(self.agent)
        for day, start, end in [(0, '09:00', '12:00'), (0, '14:00', '18:00'), (5, '10:00', '13:00')]:
            response = self.client.post(AVAILABILITY_URL, {
                'day_of_week': day, 'start_time': start, 'end_time': end,
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        response = self.client.get(AVAILABILITY_URL)
        self.assertEqual([(r['day_name'], r['start_time']) for r in response.data], [
            ('Lunes', '09:00:00'), ('Lunes', '14:00:00'), ('Sábado', '10:00:00'),
        ])

    def test_rejects_slot_shorter_than_30_minutes(self):
        self.login(self.agent)
        response = self.client.post(AVAILABILITY_URL, {
            'day_of_week': 1, 'start_time': '09:00', 'end_time': '09:29', 'slot_duration_minutes': 30,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_time', response.data)

    def test_accepts_exactly_30_minutes(self):
        self.login(self.agent)
        response = self.client.post(AVAILABILITY_URL, {
            'day_of_week': 1, 'start_time': '09:00', 'end_time': '09:30', 'slot_duration_minutes': 30,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_rejects_end_before_or_equal_to_start(self):
        self.login(self.agent)
        for end in ['09:00', '08:00']:
            with self.subTest(end=end):
                response = self.client.post(AVAILABILITY_URL, {
                    'day_of_week': 1, 'start_time': '09:00', 'end_time': end,
                }, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('end_time', response.data)

    def test_rejects_visit_duration_below_30_or_longer_than_the_slot(self):
        self.login(self.agent)
        for duration, field in [(29, 'slot_duration_minutes'), (120, 'slot_duration_minutes')]:
            with self.subTest(duration=duration):
                response = self.client.post(AVAILABILITY_URL, {
                    'day_of_week': 2, 'start_time': '09:00', 'end_time': '10:00',
                    'slot_duration_minutes': duration,
                }, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)

    def test_rejects_invalid_weekday(self):
        self.login(self.agent)
        response = self.client.post(AVAILABILITY_URL, {
            'day_of_week': 7, 'start_time': '09:00', 'end_time': '12:00',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('day_of_week', response.data)

    def test_rejects_overlapping_slots_on_the_same_day(self):
        self.rule(day=0, start=time(9), end=time(12))
        self.login(self.agent)
        for start, end in [('11:00', '13:00'), ('08:00', '09:30'), ('10:00', '11:00'), ('08:00', '13:00')]:
            with self.subTest(start=start, end=end):
                response = self.client.post(AVAILABILITY_URL, {
                    'day_of_week': 0, 'start_time': start, 'end_time': end,
                }, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('start_time', response.data)
        self.assertEqual(AgentAvailability.objects.count(), 1)

    def test_adjacent_slots_other_days_and_other_advisors_do_not_overlap(self):
        self.rule(day=0, start=time(9), end=time(12))
        self.rule(agent=self.other_agent, day=1, start=time(9), end=time(12))
        self.login(self.agent)
        for day, start, end in [(0, '12:00', '14:00'), (1, '09:00', '12:00')]:
            response = self.client.post(AVAILABILITY_URL, {
                'day_of_week': day, 'start_time': start, 'end_time': end,
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_partial_update_revalidates_with_the_final_values(self):
        first = self.rule(day=0, start=time(9), end=time(12))
        self.rule(day=0, start=time(14), end=time(16))
        self.login(self.agent)
        # Sin cambios reales no se cruza consigo misma.
        response = self.client.patch(f'{AVAILABILITY_URL}{first.pk}/', {'end_time': '12:00'},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        # Alargarla hasta la otra franja si se cruza.
        response = self.client.patch(f'{AVAILABILITY_URL}{first.pk}/', {'end_time': '15:00'},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        first.refresh_from_db()
        self.assertEqual(first.end_time, time(12))

    def test_advisor_deletes_own_slot(self):
        rule = self.rule()
        self.login(self.agent)
        response = self.client.delete(f'{AVAILABILITY_URL}{rule.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AgentAvailability.objects.exists())

    def test_model_clean_and_database_enforce_the_rules_outside_the_api(self):
        with self.assertRaises(ValidationError):
            AgentAvailability(agent=self.agent, day_of_week=0, start_time=time(9),
                              end_time=time(9, 15)).full_clean()
        with transaction.atomic(), self.assertRaises(IntegrityError):
            AgentAvailability.objects.create(agent=self.agent, day_of_week=0,
                                             start_time=time(12), end_time=time(9))
        with transaction.atomic(), self.assertRaises(IntegrityError):
            AgentAvailability.objects.create(agent=self.agent, day_of_week=0, start_time=time(9),
                                             end_time=time(12), slot_duration_minutes=10)


# --- HU-22, criterio 2: "Las excepciones bloquean fechas especificas" --------------------------

class AvailabilityExceptionTests(VisitsTestMixin, TestCase):
    def test_full_day_exception_without_hours(self):
        self.login(self.agent)
        day = next_weekday(0)
        response = self.client.post(EXCEPTIONS_URL, {
            'exception_date': day.isoformat(), 'reason': 'Trámite personal',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(response.data['is_full_day'])
        self.assertIsNone(response.data['start_time'])

    def test_partial_exception_with_hours(self):
        self.login(self.agent)
        response = self.client.post(EXCEPTIONS_URL, {
            'exception_date': next_weekday(0).isoformat(), 'start_time': '10:00', 'end_time': '11:00',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertFalse(response.data['is_full_day'])

    def test_rejects_only_one_hour_or_inverted_range(self):
        self.login(self.agent)
        day = next_weekday(0).isoformat()
        for payload in [{'start_time': '10:00'}, {'end_time': '10:00'},
                        {'start_time': '11:00', 'end_time': '10:00'}]:
            with self.subTest(payload=payload):
                response = self.client.post(EXCEPTIONS_URL, {'exception_date': day, **payload},
                                            format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('end_time', response.data)

    def test_rejects_past_dates_and_accepts_today(self):
        self.login(self.agent)
        yesterday = ecuador_today() - timedelta(days=1)
        response = self.client.post(EXCEPTIONS_URL, {'exception_date': yesterday.isoformat()},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('exception_date', response.data)
        response = self.client.post(EXCEPTIONS_URL, {'exception_date': ecuador_today().isoformat()},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_full_day_exception_removes_every_slot_of_that_date(self):
        monday = next_weekday(0)
        self.rule(day=0, start=time(9), end=time(12))
        AvailabilityException.objects.create(agent=self.agent, exception_date=monday)
        following_monday = monday + timedelta(days=7)
        slots = free_slots(self.agent, monday, following_monday, now=local(monday, 0) - timedelta(days=1))
        self.assertEqual({slot.start.date() for slot in slots}, {following_monday})
        self.assertEqual(len(slots), 3)

    def test_partial_exception_removes_only_the_crossing_slots(self):
        monday = next_weekday(0)
        self.rule(day=0, start=time(9), end=time(12))
        AvailabilityException.objects.create(agent=self.agent, exception_date=monday,
                                             start_time=time(10, 30), end_time=time(11))
        slots = free_slots(self.agent, monday, monday, now=local(monday, 0))
        self.assertEqual([slot.start for slot in slots], [local(monday, 9), local(monday, 11)])

    def test_another_advisors_exception_does_not_block(self):
        monday = next_weekday(0)
        self.rule(day=0, start=time(9), end=time(12))
        AvailabilityException.objects.create(agent=self.other_agent, exception_date=monday)
        self.assertEqual(len(free_slots(self.agent, monday, monday, now=local(monday, 0))), 3)


# --- free_slots: base de HU-18 y HU-19 (hora de Ecuador explicita) ----------------------------

class FreeSlotsTests(VisitsTestMixin, TestCase):
    def test_slots_are_in_ecuador_time_with_the_rule_duration(self):
        monday = next_weekday(0)
        self.rule(day=0, start=time(9), end=time(12))
        slots = free_slots(self.agent, monday, monday, now=local(monday, 0))
        self.assertEqual([(s.start, s.end) for s in slots], [
            (local(monday, 9), local(monday, 10)),
            (local(monday, 10), local(monday, 11)),
            (local(monday, 11), local(monday, 12)),
        ])
        # 09:00 en Ecuador (UTC-5) son las 14:00 UTC, con TIME_ZONE = 'UTC' (DT-01).
        self.assertEqual(slots[0].start.utcoffset(), timedelta(hours=-5))
        self.assertEqual(slots[0].start.astimezone(timezone.utc).hour, 14)

    def test_30_minute_visits_and_leftover_time(self):
        monday = next_weekday(0)
        self.rule(day=0, start=time(9), end=time(10, 30), duration=30)
        self.rule(day=0, start=time(15), end=time(16, 30), duration=60)
        slots = free_slots(self.agent, monday, monday, now=local(monday, 0))
        self.assertEqual([s.start for s in slots], [
            local(monday, 9), local(monday, 9, 30), local(monday, 10), local(monday, 15),
        ])

    def test_only_days_with_rules_and_never_slots_that_already_started(self):
        monday = next_weekday(0)
        self.rule(day=0, start=time(9), end=time(12))
        tuesday = monday + timedelta(days=1)
        self.assertEqual(free_slots(self.agent, tuesday, tuesday, now=local(monday, 0)), [])
        # Sin antelacion (HU-18 la prueba aparte): solo se excluye lo que ya empezo.
        slots = free_slots(self.agent, monday, monday, now=local(monday, 10, 15),
                           lead_time=timedelta(0))
        self.assertEqual([s.start for s in slots], [local(monday, 11)])

    def test_slots_belong_only_to_the_requested_advisor(self):
        monday = next_weekday(0)
        self.rule(agent=self.other_agent, day=0, start=time(9), end=time(12))
        self.assertEqual(free_slots(self.agent, monday, monday, now=local(monday, 0)), [])


# --- RF-09: cada asesor define solo lo suyo; el admin edita a cualquiera ----------------------

class AvailabilityPermissionTests(VisitsTestMixin, TestCase):
    def test_anonymous_gets_401(self):
        for url in [AVAILABILITY_URL, EXCEPTIONS_URL]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)
                response = self.client.post(url, {}, format='json')
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_advisor_lists_only_own_rules_and_exceptions(self):
        own = self.rule()
        self.rule(agent=self.other_agent)
        AvailabilityException.objects.create(agent=self.other_agent, exception_date=next_weekday(0))
        self.login(self.agent)
        self.assertEqual([r['id'] for r in self.client.get(AVAILABILITY_URL).data], [own.pk])
        self.assertEqual(self.client.get(EXCEPTIONS_URL).data, [])
        # El filtro ?agent= no abre lo ajeno al asesor.
        response = self.client.get(AVAILABILITY_URL, {'agent': self.other_agent.pk})
        self.assertEqual([r['id'] for r in response.data], [own.pk])

    def test_advisor_gets_404_on_another_advisors_records(self):
        rule = self.rule(agent=self.other_agent)
        exception = AvailabilityException.objects.create(agent=self.other_agent,
                                                         exception_date=next_weekday(0))
        self.login(self.agent)
        for url in [f'{AVAILABILITY_URL}{rule.pk}/', f'{EXCEPTIONS_URL}{exception.pk}/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
                self.assertEqual(self.client.patch(url, {'reason': 'x', 'end_time': '13:00'},
                                                   format='json').status_code,
                                 status.HTTP_404_NOT_FOUND)
                self.assertEqual(self.client.delete(url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(AgentAvailability.objects.filter(pk=rule.pk, end_time=time(12)).exists())
        self.assertTrue(AvailabilityException.objects.filter(pk=exception.pk).exists())

    def test_advisor_gets_403_when_creating_for_another_advisor(self):
        self.login(self.agent)
        response = self.client.post(AVAILABILITY_URL, {
            'agent': self.other_agent.pk, 'day_of_week': 0, 'start_time': '09:00', 'end_time': '12:00',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(EXCEPTIONS_URL, {
            'agent': self.other_agent.pk, 'exception_date': next_weekday(0).isoformat(),
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(AgentAvailability.objects.exists())
        self.assertFalse(AvailabilityException.objects.exists())

    def test_advisor_may_send_own_id_as_agent(self):
        self.login(self.agent)
        response = self.client.post(AVAILABILITY_URL, {
            'agent': self.agent.pk, 'day_of_week': 0, 'start_time': '09:00', 'end_time': '12:00',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_admin_must_choose_an_active_advisor(self):
        inactive = User.objects.create_user(username='inactivo', email='inactivo@urbanex.ec',
                                            password='Password123!', role='asesor', is_active=False)
        self.login(self.admin)
        base = {'day_of_week': 0, 'start_time': '09:00', 'end_time': '12:00'}
        for agent in [None, 'abc', inactive.pk, self.admin.pk, 999999]:
            with self.subTest(agent=agent):
                payload = dict(base) if agent is None else {**base, 'agent': agent}
                response = self.client.post(AVAILABILITY_URL, payload, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('agent', response.data)
        self.assertFalse(AgentAvailability.objects.exists())

    def test_admin_creates_and_edits_any_advisors_availability(self):
        self.login(self.admin)
        response = self.client.post(AVAILABILITY_URL, {
            'agent': self.other_agent.pk, 'day_of_week': 3, 'start_time': '09:00', 'end_time': '12:00',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['agent'], self.other_agent.pk)
        rule_id = response.data['id']
        response = self.client.patch(f'{AVAILABILITY_URL}{rule_id}/', {'end_time': '13:00'},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        response = self.client.post(EXCEPTIONS_URL, {
            'agent': self.other_agent.pk, 'exception_date': next_weekday(3).isoformat(),
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_admin_lists_all_or_filters_by_advisor(self):
        own = self.rule()
        other = self.rule(agent=self.other_agent)
        self.login(self.admin)
        self.assertEqual({r['id'] for r in self.client.get(AVAILABILITY_URL).data}, {own.pk, other.pk})
        response = self.client.get(AVAILABILITY_URL, {'agent': self.other_agent.pk})
        self.assertEqual([r['id'] for r in response.data], [other.pk])
        response = self.client.get(AVAILABILITY_URL, {'agent': 'abc'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_the_advisor_of_a_record_cannot_be_changed(self):
        rule = self.rule()
        self.login(self.admin)
        response = self.client.patch(f'{AVAILABILITY_URL}{rule.pk}/', {'agent': self.other_agent.pk},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        rule.refresh_from_db()
        self.assertEqual(rule.agent, self.agent)


# === HU-18 (URB-18, P-07): franjas libres del asesor responsable ===============================

class HU18TestMixin(VisitsTestMixin):
    def setUp(self):
        super().setUp()
        cache.clear()  # El throttle del endpoint publico guarda sus contadores en la cache
        self.property = Property.objects.create(
            agent=self.agent, title='Casa en Cumbayá', description='Prueba', property_type='casa',
            price=150000, area_m2=120, location='Cumbayá', status='disponible',
        )
        self.contact = Contact.objects.create(
            full_name='Carla Cliente', phone='+593991234567', email='carla@correo.ec',
            origin_channel=OriginChannel.MANUAL,
        )
        self.opportunity = Opportunity.objects.create(
            contact=self.contact, property=self.property, assigned_agent=self.agent,
            origin_channel=OriginChannel.MANUAL,
        )
        self.monday = next_weekday(0)

    def visit(self, start, end, status=Visit.Status.PROGRAMADA, agent=None, opportunity=None):
        opportunity = opportunity or self.opportunity
        return Visit.objects.create(
            opportunity=opportunity, property=opportunity.property, agent=agent or self.agent,
            scheduled_start=start, scheduled_end=end, status=status,
        )


class VisitModelTests(HU18TestMixin, TestCase):
    def candidate(self, start, end, **extra):
        values = {'opportunity': self.opportunity, 'property': self.property, 'agent': self.agent,
                  'scheduled_start': start, 'scheduled_end': end, **extra}
        return Visit(**values)

    def test_new_visit_is_programada_with_a_unique_cancellation_token(self):
        first = self.visit(local(self.monday, 9), local(self.monday, 10))
        second = self.visit(local(self.monday, 10), local(self.monday, 11))
        self.assertEqual(first.status, Visit.Status.PROGRAMADA)
        self.assertNotEqual(first.cancellation_token, second.cancellation_token)

    def test_rejects_overlapping_programmed_visits_of_the_same_advisor(self):
        self.visit(local(self.monday, 9), local(self.monday, 10))
        with self.assertRaises(ValidationError) as error:
            self.candidate(local(self.monday, 9, 30), local(self.monday, 10, 30)).full_clean()
        self.assertIn('scheduled_start', error.exception.message_dict)
        # Contigua: si se puede.
        self.candidate(local(self.monday, 10), local(self.monday, 11)).full_clean()

    def test_cancelled_visit_does_not_block_and_other_advisor_is_independent(self):
        self.visit(local(self.monday, 9), local(self.monday, 10), status=Visit.Status.CANCELADA)
        self.candidate(local(self.monday, 9), local(self.monday, 10)).full_clean()
        other_property = Property.objects.create(
            agent=self.other_agent, title='Otra', description='Prueba', property_type='casa',
            price=1, area_m2=1, location='Quito', status='disponible',
        )
        other_opportunity = Opportunity.objects.create(
            contact=self.contact, property=other_property, assigned_agent=self.other_agent,
            origin_channel=OriginChannel.MANUAL,
        )
        self.visit(local(self.monday, 9), local(self.monday, 10), agent=self.other_agent,
                   opportunity=other_opportunity)
        self.candidate(local(self.monday, 9), local(self.monday, 10)).full_clean()

    def test_rejects_wrong_property_end_before_start_admin_agent_and_closed_opportunity(self):
        other_property = Property.objects.create(
            agent=self.agent, title='Otra', description='Prueba', property_type='casa',
            price=1, area_m2=1, location='Quito', status='disponible',
        )
        cases = [
            ({'property': other_property}, 'property'),
            ({'scheduled_end': local(self.monday, 8)}, 'scheduled_end'),
            ({'agent': self.admin}, 'agent'),
        ]
        for extra, field in cases:
            with self.subTest(field=field):
                values = {'opportunity': self.opportunity, 'property': self.property,
                          'agent': self.agent, 'scheduled_start': local(self.monday, 9),
                          'scheduled_end': local(self.monday, 10), **extra}
                with self.assertRaises(ValidationError) as error:
                    Visit(**values).full_clean()
                self.assertIn(field, error.exception.message_dict)
        Opportunity.objects.filter(pk=self.opportunity.pk).update(status='PERDIDA')
        self.opportunity.refresh_from_db()
        with self.assertRaises(ValidationError) as error:
            self.candidate(local(self.monday, 9), local(self.monday, 10)).full_clean()
        self.assertIn('opportunity', error.exception.message_dict)

    def test_database_rejects_end_before_start(self):
        with transaction.atomic(), self.assertRaises(IntegrityError):
            self.visit(local(self.monday, 10), local(self.monday, 9))

    def test_creating_a_visit_does_not_change_the_opportunity_status(self):
        self.visit(local(self.monday, 9), local(self.monday, 10))
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, Opportunity.Status.CONTACTO_INICIAL)


class FreeSlotsWithVisitsTests(HU18TestMixin, TestCase):
    def test_programmed_visit_removes_its_slot_and_partial_overlaps(self):
        self.rule(day=0, start=time(9), end=time(13))
        self.visit(local(self.monday, 9), local(self.monday, 10))
        self.visit(local(self.monday, 11, 30), local(self.monday, 12))  # Cruza 11-12 en parte
        slots = free_slots(self.agent, self.monday, self.monday, now=local(self.monday, 0))
        self.assertEqual([s.start for s in slots], [local(self.monday, 10), local(self.monday, 12)])

    def test_cancelled_realizada_and_no_asistida_visits_do_not_occupy(self):
        self.rule(day=0, start=time(9), end=time(12))
        for hour, visit_status in [(9, Visit.Status.CANCELADA), (10, Visit.Status.REALIZADA),
                                   (11, Visit.Status.NO_ASISTIDA)]:
            self.visit(local(self.monday, hour), local(self.monday, hour + 1), status=visit_status)
        slots = free_slots(self.agent, self.monday, self.monday, now=local(self.monday, 0))
        self.assertEqual(len(slots), 3)

    def test_visit_of_another_property_of_the_same_advisor_also_occupies(self):
        self.rule(day=0, start=time(9), end=time(11))
        other_property = Property.objects.create(
            agent=self.agent, title='Otra del mismo asesor', description='Prueba',
            property_type='casa', price=1, area_m2=1, location='Quito', status='disponible',
        )
        other_opportunity = Opportunity.objects.create(
            contact=self.contact, property=other_property, assigned_agent=self.agent,
            origin_channel=OriginChannel.MANUAL,
        )
        self.visit(local(self.monday, 9), local(self.monday, 10), opportunity=other_opportunity)
        slots = free_slots(self.agent, self.monday, self.monday, now=local(self.monday, 0))
        self.assertEqual([s.start for s in slots], [local(self.monday, 10)])

    def test_minimum_lead_time_comes_from_settings(self):
        self.rule(day=0, start=time(9), end=time(13))
        now = local(self.monday, 8, 30)
        # Por defecto 120 minutos: 09:00 y 10:00 quedan antes de las 10:30.
        slots = free_slots(self.agent, self.monday, self.monday, now=now)
        self.assertEqual([s.start for s in slots], [local(self.monday, 11), local(self.monday, 12)])
        with override_settings(VISIT_MIN_LEAD_TIME_MINUTES=30):
            slots = free_slots(self.agent, self.monday, self.monday, now=now)
        self.assertEqual([s.start for s in slots][0], local(self.monday, 9))

    @override_settings(VISIT_MIN_LEAD_TIME_MINUTES=120)
    def test_slot_exactly_at_the_lead_time_is_offered(self):
        self.rule(day=0, start=time(9), end=time(10))
        slots = free_slots(self.agent, self.monday, self.monday, now=local(self.monday, 7))
        self.assertEqual([s.start for s in slots], [local(self.monday, 9)])


class PublicFreeSlotsEndpointTests(HU18TestMixin, TestCase):
    def get(self, property_id=None, **params):
        return self.client.get(free_slots_url(property_id or self.property.pk), params)

    def test_anonymous_client_sees_the_responsible_advisors_free_slots(self):
        self.rule(day=0, start=time(9), end=time(12))
        self.rule(agent=self.other_agent, day=0, start=time(14), end=time(16))  # No es responsable
        response = self.get(**{'from': self.monday.isoformat(), 'to': self.monday.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['property'], self.property.pk)
        self.assertEqual(response.data['timezone'], 'America/Guayaquil')
        self.assertEqual([s['start'] for s in response.data['slots']], [
            local(self.monday, 9).isoformat(), local(self.monday, 10).isoformat(),
            local(self.monday, 11).isoformat(),
        ])
        self.assertTrue(response.data['slots'][0]['start'].endswith('-05:00'))

    def test_response_contains_only_free_slots_and_no_private_data(self):
        '''Pedido de Pablo (2026-11-06): nada de clientes, visitas ni del asesor.'''
        self.rule(day=0, start=time(9), end=time(12))
        visit = self.visit(local(self.monday, 9), local(self.monday, 10))
        response = self.get(**{'from': self.monday.isoformat(), 'to': self.monday.isoformat()})
        self.assertEqual(set(response.data), {'property', 'timezone', 'slots'})
        for slot in response.data['slots']:
            self.assertEqual(set(slot), {'start', 'end'})
        body = response.content.decode()
        for private in [self.agent.username, self.agent.email, self.agent.first_name,
                        self.agent.last_name, self.contact.full_name, self.contact.phone,
                        self.contact.email, str(visit.cancellation_token), 'PROGRAMADA',
                        '"agent"', '"visit', '"contact', '"opportunity']:
            with self.subTest(private=private):
                self.assertNotIn(private, body)

    def test_occupied_slots_disappear_and_return_in_real_time(self):
        self.rule(day=0, start=time(9), end=time(11))
        params = {'from': self.monday.isoformat(), 'to': self.monday.isoformat()}
        self.assertEqual(len(self.get(**params).data['slots']), 2)
        visit = self.visit(local(self.monday, 9), local(self.monday, 10))
        starts = [s['start'] for s in self.get(**params).data['slots']]
        self.assertEqual(starts, [local(self.monday, 10).isoformat()])
        visit.status = Visit.Status.CANCELADA
        visit.save()
        self.assertEqual(len(self.get(**params).data['slots']), 2)

    def test_exceptions_hide_slots_in_the_public_endpoint(self):
        self.rule(day=0, start=time(9), end=time(11))
        AvailabilityException.objects.create(agent=self.agent, exception_date=self.monday)
        response = self.get(**{'from': self.monday.isoformat(), 'to': self.monday.isoformat()})
        self.assertEqual(response.data['slots'], [])

    def test_404_for_every_status_other_than_disponible_and_for_missing_property(self):
        for property_status in ['captacion', 'reservador', 'vendido', 'arrendado', 'no_disponible']:
            with self.subTest(status=property_status):
                Property.objects.filter(pk=self.property.pk).update(status=property_status)
                self.assertEqual(self.get().status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.get(property_id=999999).status_code, status.HTTP_404_NOT_FOUND)

    def test_inactive_or_missing_responsible_advisor_returns_empty_slots(self):
        self.rule(day=0, start=time(9), end=time(12))
        params = {'from': self.monday.isoformat(), 'to': self.monday.isoformat()}
        User.objects.filter(pk=self.agent.pk).update(is_active=False)
        response = self.get(**params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['slots'], [])
        Property.objects.filter(pk=self.property.pk).update(agent=None)
        self.assertEqual(self.get(**params).data['slots'], [])

    def test_default_range_is_14_days_from_today(self):
        for day in range(7):
            self.rule(day=day, start=time(9), end=time(10))
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        days = {datetime.fromisoformat(s['start']).date() for s in response.data['slots']}
        today = ecuador_today()
        self.assertEqual(max(days), today + timedelta(days=13))
        self.assertGreaterEqual(min(days), today)
        self.assertGreaterEqual(len(days), 13)  # Hoy puede quedar fuera por la antelacion

    def test_range_validation(self):
        today = ecuador_today()
        cases = [
            ({'from': (today - timedelta(days=1)).isoformat()}, 'from'),
            ({'from': today.isoformat(), 'to': (today - timedelta(days=1)).isoformat()}, 'to'),
            ({'from': today.isoformat(), 'to': (today + timedelta(days=31)).isoformat()}, 'to'),
            ({'from': '09-11-2026'}, 'from'),
            ({'to': 'mañana'}, 'to'),
        ]
        for params, field in cases:
            with self.subTest(params=params):
                response = self.get(**params)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        response = self.get(**{'from': today.isoformat(),
                               'to': (today + timedelta(days=30)).isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 31 dias: el maximo

    def test_expired_or_invalid_token_does_not_block_the_public_endpoint(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer token-invalido')
        self.assertEqual(self.get().status_code, status.HTTP_200_OK)

    def test_public_endpoint_has_its_own_rate_limit(self):
        for _ in range(30):
            self.assertEqual(self.get().status_code, status.HTTP_200_OK)
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        # El limite es solo de este endpoint: la API interna sigue respondiendo.
        self.login(self.agent)
        self.assertEqual(self.client.get(AVAILABILITY_URL).status_code, status.HTTP_200_OK)


class SetupVisitsDemoCommandTests(HU18TestMixin, TestCase):
    def run_command(self, *args):
        out = StringIO()
        call_command('setup_visits_demo', *args, stdout=out)
        return out.getvalue()

    @override_settings(DEBUG=False)
    def test_refuses_to_run_outside_development(self):
        with self.assertRaises(CommandError):
            self.run_command()

    @override_settings(DEBUG=True)
    def test_creates_one_visit_per_initial_contact_opportunity_without_changing_its_status(self):
        lost_property = Property.objects.create(
            agent=self.agent, title='Perdida', description='Prueba', property_type='casa',
            price=1, area_m2=1, location='Quito', status='disponible',
        )
        Opportunity.objects.create(contact=self.contact, property=lost_property,
                                   assigned_agent=self.agent, origin_channel=OriginChannel.MANUAL,
                                   status=Opportunity.Status.PERDIDA)
        output = self.run_command('--with-availability')
        self.assertIn('Visitas creadas: 1', output)
        visit = Visit.objects.get()
        self.assertEqual(visit.opportunity, self.opportunity)
        self.assertEqual(visit.agent, self.agent)
        self.assertEqual(visit.status, Visit.Status.PROGRAMADA)
        self.assertEqual(AgentAvailability.objects.filter(agent=self.agent).count(), 5)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, Opportunity.Status.CONTACTO_INICIAL)
        # La visita sale de una franja libre: ya no se ofrece en el endpoint publico.
        day = visit.scheduled_start.astimezone(ECUADOR_TZ).date().isoformat()
        starts = [s['start'] for s in self.client.get(
            free_slots_url(self.property.pk), {'from': day, 'to': day}).data['slots']]
        self.assertNotIn(visit.scheduled_start.astimezone(ECUADOR_TZ).isoformat(), starts)

    @override_settings(DEBUG=True)
    def test_is_idempotent_and_skips_advisors_without_availability(self):
        output = self.run_command()
        self.assertIn('no tiene disponibilidad', output)
        self.assertFalse(Visit.objects.exists())
        self.run_command('--with-availability')
        output = self.run_command('--with-availability')
        self.assertIn('ya tiene una visita programada', output)
        self.assertEqual(Visit.objects.count(), 1)


# === HU-24 (URB-27, I-08): agenda de visitas del asesor ========================================

AGENDA_URL = '/api/visits/agenda/'


class AgendaTests(HU18TestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.week = {'from': self.monday.isoformat(),
                     'to': (self.monday + timedelta(days=6)).isoformat()}

    def agenda(self, **params):
        return self.client.get(AGENDA_URL, params)

    # Criterio 1: "Muestra las visitas con propiedad, cliente, fecha y hora"
    def test_each_visit_shows_property_client_date_and_time(self):
        visit = self.visit(local(self.monday, 9), local(self.monday, 10))
        self.login(self.agent)
        response = self.agenda(**self.week)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['agent'], self.agent.pk)
        self.assertEqual(response.data['timezone'], 'America/Guayaquil')
        [item] = response.data['visits']
        # Lote 3 (DS-39): aviso de WhatsApp, asesor de la oportunidad y resultado (HU-20, HU-25).
        self.assertEqual(set(item), {'id', 'scheduled_start', 'scheduled_end', 'status',
                                     'status_display', 'property', 'client', 'opportunity',
                                     'needs_whatsapp_confirmation', 'followup_agent_name',
                                     'can_record_outcome', 'outcome_notes',
                                     'outcome_recorded_at', 'outcome_recorded_by_name',
                                     'can_cancel'})  # HU-21 (DS-52)
        self.assertEqual(item['id'], visit.pk)
        self.assertEqual(item['scheduled_start'], local(self.monday, 9).isoformat())
        self.assertTrue(item['scheduled_end'].endswith('-05:00'))
        self.assertEqual(item['status_display'], 'Programada')
        self.assertEqual(item['property'], {'id': self.property.pk, 'title': 'Casa en Cumbayá',
                                            'location': 'Cumbayá'})
        self.assertEqual(item['client'], {'full_name': 'Carla Cliente', 'phone': '+593991234567',
                                          'email': 'carla@correo.ec'})
        self.assertEqual(item['opportunity'], self.opportunity.pk)
        self.assertNotIn(str(visit.cancellation_token), response.content.decode())

    def test_client_without_email_returns_empty_email(self):
        Contact.objects.filter(pk=self.contact.pk).update(email='')
        self.visit(local(self.monday, 9), local(self.monday, 10))
        self.login(self.agent)
        [item] = self.agenda(**self.week).data['visits']
        self.assertEqual(item['client']['email'], '')

    def test_visits_are_ordered_by_start(self):
        later = self.visit(local(self.monday + timedelta(days=2), 9),
                           local(self.monday + timedelta(days=2), 10))
        earlier = self.visit(local(self.monday, 11), local(self.monday, 12))
        self.login(self.agent)
        ids = [item['id'] for item in self.agenda(**self.week).data['visits']]
        self.assertEqual(ids, [earlier.pk, later.pk])

    # Criterio 2: "Solo muestra la agenda propia del asesor"
    def test_advisor_sees_only_own_agenda_and_agent_param_is_ignored(self):
        own = self.visit(local(self.monday, 9), local(self.monday, 10))
        other_property = Property.objects.create(
            agent=self.other_agent, title='Del otro asesor', description='Prueba',
            property_type='casa', price=1, area_m2=1, location='Quito', status='disponible',
        )
        other_opportunity = Opportunity.objects.create(
            contact=self.contact, property=other_property, assigned_agent=self.other_agent,
            origin_channel=OriginChannel.MANUAL,
        )
        self.visit(local(self.monday, 9), local(self.monday, 10), agent=self.other_agent,
                   opportunity=other_opportunity)
        self.login(self.agent)
        for params in [self.week, {**self.week, 'agent': self.other_agent.pk}]:
            with self.subTest(params=params):
                response = self.agenda(**params)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['agent'], self.agent.pk)
                self.assertEqual([item['id'] for item in response.data['visits']], [own.pk])
                self.assertNotIn('Del otro asesor', response.content.decode())

    def test_anonymous_gets_401(self):
        self.assertEqual(self.agenda().status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_must_choose_an_advisor(self):
        self.login(self.admin)
        for agent in [None, 'abc', self.admin.pk, 999999]:
            with self.subTest(agent=agent):
                params = dict(self.week) if agent is None else {**self.week, 'agent': agent}
                response = self.agenda(**params)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('agent', response.data)

    def test_admin_sees_the_chosen_advisors_agenda_even_if_inactive(self):
        visit = self.visit(local(self.monday, 9), local(self.monday, 10))
        self.login(self.admin)
        response = self.agenda(**self.week, agent=self.agent.pk)
        self.assertEqual([item['id'] for item in response.data['visits']], [visit.pk])
        self.assertEqual(self.agenda(**self.week, agent=self.other_agent.pk).data['visits'], [])
        User.objects.filter(pk=self.agent.pk).update(is_active=False)  # Historial consultable
        response = self.agenda(**self.week, agent=self.agent.pk)
        self.assertEqual([item['id'] for item in response.data['visits']], [visit.pk])

    def test_visit_stays_with_its_advisor_after_the_property_is_reassigned(self):
        visit = self.visit(local(self.monday, 9), local(self.monday, 10))
        Property.objects.filter(pk=self.property.pk).update(agent=self.other_agent)
        self.login(self.agent)
        self.assertEqual([i['id'] for i in self.agenda(**self.week).data['visits']], [visit.pk])
        self.login(self.other_agent)
        self.assertEqual(self.agenda(**self.week).data['visits'], [])

    # Rango (respuesta 3 de Pablo, 2026-11-06)
    def test_default_range_is_the_current_week_monday_to_sunday_in_ecuador(self):
        today = ecuador_today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        inside = [
            self.visit(local(week_start, 0, 0), local(week_start, 1)),
            self.visit(local(week_end, 23, 0), local(week_end, 23, 30)),  # Lunes 04:00 UTC
        ]
        self.visit(local(week_start - timedelta(days=1), 23), local(week_start - timedelta(days=1), 23, 30))
        self.visit(local(week_end + timedelta(days=1), 0), local(week_end + timedelta(days=1), 1))
        self.login(self.agent)
        response = self.agenda()
        self.assertEqual(response.data['from'], week_start.isoformat())
        self.assertEqual(response.data['to'], week_end.isoformat())
        self.assertEqual([item['id'] for item in response.data['visits']], [v.pk for v in inside])

    def test_past_dates_are_accepted_as_history(self):
        past_day = ecuador_today() - timedelta(days=14)
        visit = self.visit(local(past_day, 9), local(past_day, 10), status=Visit.Status.REALIZADA)
        self.login(self.agent)
        response = self.agenda(**{'from': past_day.isoformat(), 'to': past_day.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.data['visits']], [visit.pk])

    def test_only_one_date_gives_a_7_day_range(self):
        self.login(self.agent)
        response = self.agenda(**{'from': self.monday.isoformat()})
        self.assertEqual(response.data['to'], (self.monday + timedelta(days=6)).isoformat())
        response = self.agenda(**{'to': self.monday.isoformat()})
        self.assertEqual(response.data['from'], (self.monday - timedelta(days=6)).isoformat())

    def test_range_validation(self):
        self.login(self.agent)
        start = self.monday
        cases = [
            ({'from': start.isoformat(), 'to': (start - timedelta(days=1)).isoformat()}, 'to'),
            ({'from': start.isoformat(), 'to': (start + timedelta(days=31)).isoformat()}, 'to'),
            ({'from': '2026/11/09'}, 'from'),
            ({'to': 'lunes'}, 'to'),
        ]
        for params, field in cases:
            with self.subTest(params=params):
                response = self.agenda(**params)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        response = self.agenda(**{'from': start.isoformat(),
                                  'to': (start + timedelta(days=30)).isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 31 dias: el maximo

    # Estados (respuesta 4 de Pablo, 2026-11-06)
    def test_status_filter_default_single_and_all(self):
        by_status = {}
        for hour, visit_status in [(9, Visit.Status.PROGRAMADA), (10, Visit.Status.REALIZADA),
                                   (11, Visit.Status.NO_ASISTIDA), (12, Visit.Status.CANCELADA)]:
            by_status[visit_status] = self.visit(local(self.monday, hour),
                                                 local(self.monday, hour + 1), status=visit_status)
        self.login(self.agent)

        def ids(**params):
            response = self.agenda(**self.week, **params)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
            return [item['id'] for item in response.data['visits']]

        # Por defecto: todas menos las canceladas.
        self.assertEqual(ids(), [by_status[s].pk for s in (
            Visit.Status.PROGRAMADA, Visit.Status.REALIZADA, Visit.Status.NO_ASISTIDA)])
        # Un estado concreto, incluida CANCELADA.
        for visit_status, visit in by_status.items():
            with self.subTest(status=visit_status):
                self.assertEqual(ids(status=visit_status), [visit.pk])
        # all: todas, canceladas incluidas.
        self.assertEqual(ids(status='all'), [v.pk for v in by_status.values()])
        response = self.agenda(**self.week, status='ANULADA')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)


class CleanWithoutTimesTests(VisitsTestMixin, TestCase):
    '''Auditoria del PR #19 (2026-11-08): sin horas, clean() no debe lanzar ValueError (500 en el admin).'''

    def test_missing_times_give_validation_error_not_value_error(self):
        for obj in (AgentAvailability(agent=self.agent, day_of_week=0), Visit(agent=self.agent)):
            with self.subTest(model=type(obj).__name__):
                with self.assertRaises(ValidationError):
                    obj.full_clean()


# =============================================================================================
# Lote 3 (DS-39): HU-19 solicitar visita, HU-20 confirmacion y P-08, HU-25 resultado
# =============================================================================================

def request_url(property_id):
    return f'/api/visits/properties/{property_id}/request/'


def public_url(token):
    return f'/api/visits/public/{token}/'


def outcome_url(visit_id):
    return f'/api/visits/{visit_id}/outcome/'


NEW_PHONE = '0987654321'
NEW_PHONE_E164 = '+593987654321'
EXISTING_PHONE = '0991234567'  # El de Carla Cliente en HU18TestMixin


class HU19TestMixin(HU18TestMixin):
    def setUp(self):
        super().setUp()
        settings_override = override_settings(FRONTEND_BASE_URL='http://portal.test')
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        self.rule(day=0)  # Lunes 09:00-12:00, visitas de 60 min
        self.start = local(self.monday, 9)
        self.url = request_url(self.property.pk)

    def payload(self, start=None, **overrides):
        data = {'start': (start or self.start).isoformat(), 'full_name': 'Nuevo Cliente',
                'phone': NEW_PHONE, 'email': '', 'email_opt_in': False,
                'privacy_accepted': True}
        data.update(overrides)
        return data

    def post(self, data, execute_on_commit=True):
        with self.captureOnCommitCallbacks(execute=execute_on_commit):
            return self.client.post(self.url, data, format='json')


class VisitRequestTests(HU19TestMixin, TestCase):
    '''HU-19 (P-07, RF-04): solicitud del cliente sin cuenta.'''

    # Criterio: se registra la visita, se bloquea la franja y la oportunidad pasa a Visita Programada
    def test_new_contact_creates_contact_opportunity_and_visit(self):
        response = self.post(self.payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(set(response.data),
                         {'detail', 'scheduled_start', 'scheduled_end', 'confirmation'})
        self.assertEqual(response.data['scheduled_start'], self.start.isoformat())
        self.assertEqual(response.data['confirmation'], 'whatsapp')

        contact = Contact.objects.get(phone=NEW_PHONE_E164)
        self.assertEqual(contact.origin_channel, OriginChannel.CATALOGO_WEB)
        self.assertIsNotNone(contact.privacy_accepted_at)
        self.assertFalse(contact.email_opt_in)
        opportunity = Opportunity.objects.get(contact=contact)
        self.assertEqual(opportunity.assigned_agent, self.agent)
        self.assertEqual(opportunity.origin_channel, OriginChannel.CATALOGO_WEB)
        self.assertEqual(opportunity.status, Opportunity.Status.VISITA_PROGRAMADA)
        visit = Visit.objects.get(opportunity=opportunity)
        self.assertEqual((visit.agent, visit.status, visit.scheduled_start),
                         (self.agent, Visit.Status.PROGRAMADA, self.start))
        self.assertNotIn(str(visit.cancellation_token), response.content.decode())
        self.assertNotIn(self.agent.email, response.content.decode())

        history = list(opportunity.status_history.values_list(
            'previous_status', 'new_status', 'changed_by', 'reason'))
        self.assertEqual(history, [
            ('', 'CONTACTO_INICIAL', None, SYSTEM_REASON_CLIENT_PORTAL),
            ('CONTACTO_INICIAL', 'VISITA_PROGRAMADA', None, SYSTEM_REASON_CLIENT_PORTAL),
        ])
        # La franja queda bloqueada para el siguiente cliente (HU-18)
        self.assertNotIn(self.start, [s.start for s in free_slots(self.agent, self.monday,
                                                                    self.monday)])

    def test_existing_contact_reuses_opportunity_and_is_not_modified(self):
        response = self.post(self.payload(phone=EXISTING_PHONE, full_name='Otro Nombre',
                                          email='nuevo@correo.ec', email_opt_in=True))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.contact.refresh_from_db()
        self.assertEqual((self.contact.full_name, self.contact.email, self.contact.email_opt_in),
                         ('Carla Cliente', 'carla@correo.ec', False))
        self.assertEqual(Contact.objects.count(), 1)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, Opportunity.Status.VISITA_PROGRAMADA)
        visit = self.opportunity.visits.get()
        # DS-39: la confirmacion va al correo de esta solicitud, guardado en la visita
        self.assertEqual(visit.confirmation_email, 'nuevo@correo.ec')

    def test_response_is_the_same_whether_contact_exists_or_not(self):
        new = self.post(self.payload())
        existing = self.post(self.payload(start=local(self.monday, 10), phone=EXISTING_PHONE))
        self.assertEqual(new.status_code, existing.status_code)
        self.assertEqual(set(new.data), set(existing.data))
        self.assertEqual(new.data['detail'], existing.data['detail'])

    def test_new_contact_with_opt_in_saves_email_and_opt_in(self):
        response = self.post(self.payload(email='cliente@correo.ec', email_opt_in=True))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['confirmation'], 'email')
        contact = Contact.objects.get(phone=NEW_PHONE_E164)
        self.assertEqual((contact.email, contact.email_opt_in), ('cliente@correo.ec', True))

    def test_email_without_opt_in_gets_whatsapp_confirmation(self):
        response = self.post(self.payload(email='cliente@correo.ec', email_opt_in=False))
        self.assertEqual(response.data['confirmation'], 'whatsapp')
        self.assertEqual(Visit.objects.get().confirmation_email, '')

    # Criterio: la franja debe ser exactamente una de las ofrecidas (DS-39 punto 3)
    def test_slot_not_offered_is_rejected(self):
        for start in (local(self.monday, 9, 30), local(self.monday, 14),
                      local(self.monday + timedelta(days=1), 9)):
            with self.subTest(start=start):
                response = self.post(self.payload(start=start))
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('start', response.data)
        self.assertFalse(Visit.objects.exists())
        self.assertFalse(Contact.objects.filter(phone=NEW_PHONE_E164).exists())

    def test_taken_slot_is_rejected(self):
        other_property = Property.objects.create(
            agent=self.agent, title='Otra', description='x', property_type='casa', price=1,
            area_m2=1, location='Quito', status='disponible',
        )
        other_opportunity = Opportunity.objects.create(
            contact=self.contact, property=other_property, assigned_agent=self.agent,
            origin_channel=OriginChannel.MANUAL,
        )
        self.visit(local(self.monday, 9), local(self.monday, 10), opportunity=other_opportunity)
        response = self.post(self.payload())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start', response.data)

    def test_second_client_cannot_take_the_same_slot(self):
        first = self.post(self.payload())
        second = self.post(self.payload(phone='0981112233', full_name='Segundo'))
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Visit.objects.count(), 1)

    def test_stale_slot_list_is_still_blocked_by_model_validation(self):
        '''
        Concurrencia en SQLite: simula que otra solicitud ocupo la franja despues de calcular
        free_slots(). La validacion de Visit.clean() dentro de la transaccion la rechaza. En
        PostgreSQL falta la restriccion de exclusion (DT-143).
        '''
        from . import services
        stale = services.free_slots(self.agent, self.monday, self.monday)
        self.visit(local(self.monday, 9), local(self.monday, 10))
        with mock.patch.object(services, 'free_slots', return_value=stale):
            response = self.post(self.payload())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Visit.objects.count(), 1)
        self.assertFalse(Contact.objects.filter(phone=NEW_PHONE_E164).exists())

    def test_requires_privacy_valid_phone_and_name(self):
        response = self.post(self.payload(privacy_accepted=False, phone='022345678',
                                          full_name='  '))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {'privacy_accepted', 'phone', 'full_name'})
        self.assertFalse(Visit.objects.exists())

    def test_opt_in_requires_email_and_email_must_be_valid(self):
        for overrides, field in (({'email_opt_in': True}, 'email'),
                                 ({'email': 'no-es-correo'}, 'email')):
            with self.subTest(overrides=overrides):
                response = self.post(self.payload(**overrides))
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)

    def test_conflict_when_opportunity_already_has_a_scheduled_visit(self):
        self.visit(local(self.monday, 11), local(self.monday, 12))
        response = self.post(self.payload(phone=EXISTING_PHONE))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Visit.objects.count(), 1)

    def test_status_does_not_go_back_when_opportunity_is_further(self):
        Opportunity.objects.filter(pk=self.opportunity.pk).update(
            status=Opportunity.Status.EN_NEGOCIACION)
        response = self.post(self.payload(phone=EXISTING_PHONE))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, Opportunity.Status.EN_NEGOCIACION)
        self.assertFalse(self.opportunity.status_history.exists())

    def test_only_available_properties(self):
        Property.objects.filter(pk=self.property.pk).update(status='reservado')
        response = self.post(self.payload())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.post(request_url(999999), self.payload(),
                                          format='json').status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_inactive_agent_offers_nothing(self):
        User.objects.filter(pk=self.agent.pk).update(is_active=False)
        response = self.post(self.payload())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start', response.data)

    def test_visit_agent_is_property_agent_even_if_opportunity_has_another(self):
        Opportunity.objects.filter(pk=self.opportunity.pk).update(assigned_agent=self.other_agent)
        response = self.post(self.payload(phone=EXISTING_PHONE))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        visit = Visit.objects.get()
        self.assertEqual(visit.agent, self.agent)
        self.assertEqual(visit.opportunity.assigned_agent, self.other_agent)


class VisitRequestThrottleTests(HU19TestMixin, TestCase):
    '''DS-39 punto 4: 3 por minuto y 10 por dia por IP.'''

    def test_three_per_minute(self):
        codes = [self.post(self.payload(privacy_accepted=False)).status_code for _ in range(4)]
        self.assertEqual(codes[:3], [status.HTTP_400_BAD_REQUEST] * 3)
        self.assertEqual(codes[3], status.HTTP_429_TOO_MANY_REQUESTS)

    def test_ten_per_day(self):
        with mock.patch.object(VisitRequestBurstThrottle, 'rate', '100/minute'):
            codes = [self.post(self.payload(privacy_accepted=False)).status_code
                     for _ in range(11)]
        self.assertEqual(codes[:10], [status.HTTP_400_BAD_REQUEST] * 10)
        self.assertEqual(codes[10], status.HTTP_429_TOO_MANY_REQUESTS)


class VisitNotificationTests(HU19TestMixin, TestCase):
    '''HU-20: correos despues del commit (DS-39 punto 5).'''

    def test_client_with_opt_in_receives_link_and_agent_is_notified(self):
        response = self.post(self.payload(email='cliente@correo.ec', email_opt_in=True))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        visit = Visit.objects.get()
        recipients = sorted(message.to[0] for message in mail.outbox)
        self.assertEqual(recipients, ['asesor.visitas@urbanex.ec', 'cliente@correo.ec'])
        client_mail = next(m for m in mail.outbox if m.to == ['cliente@correo.ec'])
        self.assertIn(f'http://portal.test/visits/{visit.cancellation_token}', client_mail.body)
        agent_mail = next(m for m in mail.outbox if m.to == ['asesor.visitas@urbanex.ec'])
        self.assertNotIn(str(visit.cancellation_token), agent_mail.body)

    def test_without_opt_in_only_agent_is_notified_with_whatsapp_hint(self):
        self.post(self.payload(email='cliente@correo.ec'))
        self.assertEqual([m.to for m in mail.outbox], [['asesor.visitas@urbanex.ec']])
        self.assertIn('WhatsApp', mail.outbox[0].body)

    def test_mail_is_sent_only_after_commit(self):
        self.post(self.payload(email='cliente@correo.ec', email_opt_in=True),
                  execute_on_commit=False)
        self.assertEqual(mail.outbox, [])

    def test_followup_agent_is_also_notified(self):
        Opportunity.objects.filter(pk=self.opportunity.pk).update(assigned_agent=self.other_agent)
        self.post(self.payload(phone=EXISTING_PHONE))
        self.assertEqual(sorted(m.to[0] for m in mail.outbox),
                         ['asesor.visitas@urbanex.ec', 'otro.asesor@urbanex.ec'])

    def test_mail_failure_does_not_revert_the_visit(self):
        with mock.patch('apps.visits.services.send_mail', side_effect=OSError('SMTP caido')):
            with self.assertLogs('apps.visits.services', level='ERROR'):
                response = self.post(self.payload(email='cliente@correo.ec', email_opt_in=True))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Visit.objects.exists())


class PublicVisitTests(HU18TestMixin, TestCase):
    '''HU-20 (P-08): solo lectura por token, hasta la hora de inicio.'''

    def setUp(self):
        super().setUp()
        User.objects.filter(pk=self.agent.pk).update(phone='0991112222')

    def test_shows_property_date_status_and_agent_until_start(self):
        visit = self.visit(local(self.monday, 9), local(self.monday, 10))
        response = self.client.get(public_url(visit.cancellation_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {'scheduled_start', 'scheduled_end', 'status',
                                              'status_display', 'property', 'visit_agent',
                                              'followup_agent',
                                              # HU-21 (DS-52)
                                              'can_cancel', 'cancel_until'})
        self.assertEqual(response.data['visit_agent'],
                         {'first_name': 'Ana', 'last_name': 'Asesora', 'phone': '0991112222'})
        self.assertIsNone(response.data['followup_agent'])
        body = response.content.decode()
        for private in ('Carla', '+593991234567', 'carla@correo.ec', 'asesor.visitas@urbanex.ec'):
            self.assertNotIn(private, body)

    def test_shows_followup_agent_when_different(self):
        Opportunity.objects.filter(pk=self.opportunity.pk).update(assigned_agent=self.other_agent)
        visit = self.visit(local(self.monday, 9), local(self.monday, 10))
        response = self.client.get(public_url(visit.cancellation_token))
        self.assertEqual(response.data['followup_agent'],
                         {'first_name': '', 'last_name': '', 'phone': ''})

    def test_expired_or_unknown_token_is_404(self):
        yesterday = ecuador_today() - timedelta(days=1)
        past = self.visit(local(yesterday, 9), local(yesterday, 10))
        self.assertEqual(self.client.get(public_url(past.cancellation_token)).status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.get(public_url(uuid.uuid4())).status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_agenda_marks_whatsapp_confirmation(self):
        with_email = self.visit(local(self.monday, 9), local(self.monday, 10))
        Visit.objects.filter(pk=with_email.pk).update(confirmation_email='c@correo.ec')
        self.visit(local(self.monday, 10), local(self.monday, 11),
                   opportunity=Opportunity.objects.create(
                       contact=Contact.objects.create(full_name='Sin correo',
                                                      phone='+593980000000',
                                                      origin_channel=OriginChannel.MANUAL),
                       property=self.property, assigned_agent=self.agent,
                       origin_channel=OriginChannel.MANUAL))
        self.login(self.agent)
        week = {'from': self.monday.isoformat(), 'to': (self.monday + timedelta(days=6)).isoformat()}
        flags = [v['needs_whatsapp_confirmation']
                 for v in self.client.get(AGENDA_URL, week).data['visits']]
        self.assertEqual(flags, [False, True])


class VisitOutcomeTests(HU18TestMixin, TestCase):
    '''HU-25 (I-08, RF-04): resultado de la visita (DS-39 punto 6).'''

    def setUp(self):
        super().setUp()
        Opportunity.objects.filter(pk=self.opportunity.pk).update(
            status=Opportunity.Status.VISITA_PROGRAMADA)
        yesterday = ecuador_today() - timedelta(days=1)
        self.past = self.visit(local(yesterday, 9), local(yesterday, 10))

    def record(self, visit=None, outcome='REALIZADA', notes='El cliente quiere negociar.'):
        return self.client.post(outcome_url((visit or self.past).pk),
                                {'status': outcome, 'outcome_notes': notes}, format='json')

    def test_agent_records_realizada_once_without_advancing_opportunity(self):
        self.login(self.agent)
        response = self.record()
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['status'], 'REALIZADA')
        self.assertFalse(response.data['can_record_outcome'])
        self.past.refresh_from_db()
        self.assertEqual(self.past.outcome_notes, 'El cliente quiere negociar.')
        self.assertEqual(self.past.outcome_recorded_by, self.agent)
        self.assertIsNotNone(self.past.outcome_recorded_at)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, Opportunity.Status.VISITA_PROGRAMADA)
        # Una sola vez
        self.assertEqual(self.record(outcome='CANCELADA').status_code, status.HTTP_409_CONFLICT)

    def test_not_before_start(self):
        future = self.visit(local(self.monday, 9), local(self.monday, 10))
        self.login(self.agent)
        response = self.record(visit=future)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        future.refresh_from_db()
        self.assertEqual(future.status, Visit.Status.PROGRAMADA)

    def test_notes_and_valid_status_are_required(self):
        self.login(self.agent)
        self.assertIn('outcome_notes', self.record(notes='   ').data)
        for outcome in ('PROGRAMADA', 'OTRA'):
            response = self.record(outcome=outcome)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('status', response.data)

    def test_permissions(self):
        self.assertEqual(self.record().status_code, status.HTTP_401_UNAUTHORIZED)
        self.login(self.other_agent)
        self.assertEqual(self.record().status_code, status.HTTP_404_NOT_FOUND)
        self.login(self.admin)
        response = self.record(outcome='NO_ASISTIDA')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['outcome_recorded_by_name'], 'admin.visitas')

    def test_no_show_of_only_active_visit_returns_to_contacto_inicial(self):
        for outcome in ('NO_ASISTIDA', 'CANCELADA'):
            with self.subTest(outcome=outcome):
                Opportunity.objects.filter(pk=self.opportunity.pk).update(
                    status=Opportunity.Status.VISITA_PROGRAMADA)
                yesterday = ecuador_today() - timedelta(days=1)
                visit = self.visit(local(yesterday, 11), local(yesterday, 12))
                Visit.objects.filter(pk=self.past.pk).update(status=Visit.Status.REALIZADA)
                self.login(self.agent)
                response = self.record(visit=visit, outcome=outcome)
                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
                self.opportunity.refresh_from_db()
                self.assertEqual(self.opportunity.status, Opportunity.Status.CONTACTO_INICIAL)
                last = self.opportunity.status_history.last()
                self.assertEqual((last.previous_status, last.new_status, last.changed_by),
                                 ('VISITA_PROGRAMADA', 'CONTACTO_INICIAL', self.agent))

    def test_other_active_visit_keeps_visita_programada(self):
        self.visit(local(self.monday, 9), local(self.monday, 10))
        self.login(self.agent)
        self.assertEqual(self.record(outcome='CANCELADA').status_code, status.HTTP_200_OK)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, Opportunity.Status.VISITA_PROGRAMADA)

    def test_agenda_offers_outcome_only_after_start(self):
        future = self.visit(local(self.monday, 9), local(self.monday, 10))
        self.login(self.agent)
        yesterday = ecuador_today() - timedelta(days=1)
        response = self.client.get(AGENDA_URL, {'from': yesterday.isoformat(),
                                                'to': self.monday.isoformat()})
        flags = {v['id']: v['can_record_outcome'] for v in response.data['visits']}
        self.assertEqual(flags, {self.past.pk: True, future.pk: False})


# =============================================================================================
# Lotes 5 y 6 (DS-52): HU-21 cancelar una visita
# =============================================================================================

def public_cancel_url(token):
    return f'/api/visits/public/{token}/cancel/'


def agent_cancel_url(visit_id):
    return f'/api/visits/{visit_id}/cancel/'


def minutes_from_now(minutes):
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


class VisitCancelTestMixin(HU18TestMixin):
    def setUp(self):
        super().setUp()
        Opportunity.objects.filter(pk=self.opportunity.pk).update(
            status=Opportunity.Status.VISITA_PROGRAMADA)
        self.opportunity.refresh_from_db()

    def visit_in(self, minutes, **extra):
        start = minutes_from_now(minutes)
        return self.visit(start, start + timedelta(hours=1), **extra)

    def client_cancel(self, visit):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(public_cancel_url(visit.cancellation_token))

    def agent_cancel(self, visit, reason='El cliente pidió cancelar por WhatsApp.'):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(agent_cancel_url(visit.pk), {'reason': reason},
                                    format='json')


class ClientVisitCancelTests(VisitCancelTestMixin, TestCase):
    '''HU-21 (P-08): el cliente cancela con su enlace hasta 1 hora antes (DS-52).'''

    def test_client_cancels_frees_the_slot_and_opportunity_goes_back(self):
        self.rule(day=0)  # Lunes 09:00-12:00
        visit = self.visit(local(self.monday, 9), local(self.monday, 10))
        Visit.objects.filter(pk=visit.pk).update(confirmation_email='carla@correo.ec')
        self.assertNotIn(local(self.monday, 9),
                         [s.start for s in free_slots(self.agent, self.monday, self.monday)])

        response = self.client_cancel(visit)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual((response.data['status'], response.data['can_cancel']),
                         ('CANCELADA', False))
        visit.refresh_from_db()
        self.assertEqual(visit.status, Visit.Status.CANCELADA)
        self.assertIsNone(visit.outcome_recorded_by)
        # La franja vuelve a ofrecerse
        self.assertIn(local(self.monday, 9),
                      [s.start for s in free_slots(self.agent, self.monday, self.monday)])
        # Unica visita activa: Visita programada -> Contacto inicial, sin usuario (portal)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, Opportunity.Status.CONTACTO_INICIAL)
        last = self.opportunity.status_history.last()
        self.assertEqual((last.changed_by, last.reason), (None, SYSTEM_REASON_CLIENT_PORTAL))
        # Entrada SISTEMA en el historial de la oportunidad (HU-33)
        event = self.opportunity.interactions.get()
        self.assertEqual((event.interaction_type, event.author, event.visit_id),
                         ('SISTEMA', None, visit.pk))
        self.assertIn('El cliente canceló', event.notes)
        # Aviso solo al asesor
        self.assertEqual([m.to for m in mail.outbox], [['asesor.visitas@urbanex.ec']])

    def test_only_until_one_hour_before(self):
        late = self.visit_in(50)
        response = self.client_cancel(late)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        late.refresh_from_db()
        self.assertEqual(late.status, Visit.Status.PROGRAMADA)
        self.assertFalse(self.client.get(public_url(late.cancellation_token)).data['can_cancel'])

        on_time = self.visit_in(90)
        self.assertTrue(self.client.get(public_url(on_time.cancellation_token))
                        .data['can_cancel'])
        self.assertEqual(self.client_cancel(on_time).status_code, status.HTTP_200_OK)

    def test_already_cancelled_is_409_and_started_or_unknown_is_404(self):
        visit = self.visit_in(180)
        self.assertEqual(self.client_cancel(visit).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client_cancel(visit).status_code, status.HTTP_409_CONFLICT)
        started = self.visit_in(-5)
        self.assertEqual(self.client_cancel(started).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.post(public_cancel_url(uuid.uuid4())).status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_other_active_visit_keeps_visita_programada(self):
        visit = self.visit_in(180)
        self.visit_in(60 * 30)
        self.assertEqual(self.client_cancel(visit).status_code, status.HTTP_200_OK)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, Opportunity.Status.VISITA_PROGRAMADA)

    def test_response_has_no_client_data(self):
        body = self.client_cancel(self.visit_in(180)).content.decode()
        for private in ('Carla', '+593991234567', 'carla@correo.ec'):
            self.assertNotIn(private, body)


class AgentVisitCancelTests(VisitCancelTestMixin, TestCase):
    '''HU-21 (I-08): el asesor o el admin cancelan hasta la hora de inicio, con motivo (DS-52).'''

    def test_agent_cancels_with_reason_and_client_is_notified(self):
        visit = self.visit_in(30)  # Dentro de la ultima hora: el asesor si puede
        Visit.objects.filter(pk=visit.pk).update(confirmation_email='carla@correo.ec')
        self.login(self.agent)
        response = self.agent_cancel(visit)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual((response.data['status'], response.data['can_cancel']),
                         ('CANCELADA', False))
        visit.refresh_from_db()
        self.assertEqual(visit.outcome_recorded_by, self.agent)
        self.assertIn('El cliente pidió cancelar', visit.outcome_notes)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, Opportunity.Status.CONTACTO_INICIAL)
        self.assertEqual(self.opportunity.status_history.last().changed_by, self.agent)
        self.assertIn('Motivo: El cliente pidió cancelar',
                      self.opportunity.interactions.get().notes)
        self.assertEqual([m.to for m in mail.outbox], [['carla@correo.ec']])
        self.assertIn('cancelada por tu asesor', mail.outbox[0].body)

    def test_without_client_email_no_mail_is_sent(self):
        self.login(self.agent)
        self.assertEqual(self.agent_cancel(self.visit_in(120)).status_code, status.HTTP_200_OK)
        self.assertEqual(mail.outbox, [])

    def test_reason_is_required(self):
        visit = self.visit_in(120)
        self.login(self.agent)
        for reason in ('', '   '):
            response = self.agent_cancel(visit, reason=reason)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('reason', response.data)
        visit.refresh_from_db()
        self.assertEqual(visit.status, Visit.Status.PROGRAMADA)

    def test_not_after_start_and_409_if_not_programmed(self):
        self.login(self.agent)
        started = self.visit_in(-5)
        self.assertEqual(self.agent_cancel(started).status_code, status.HTTP_400_BAD_REQUEST)
        done = self.visit_in(-120, status=Visit.Status.REALIZADA)
        self.assertEqual(self.agent_cancel(done).status_code, status.HTTP_409_CONFLICT)

    def test_permissions(self):
        visit = self.visit_in(120)
        self.assertEqual(self.agent_cancel(visit).status_code, status.HTTP_401_UNAUTHORIZED)
        self.login(self.other_agent)
        self.assertEqual(self.agent_cancel(visit).status_code, status.HTTP_404_NOT_FOUND)
        self.login(self.admin)
        self.assertEqual(self.agent_cancel(visit).status_code, status.HTTP_200_OK)

    def test_agenda_marks_which_visits_can_be_cancelled(self):
        future = self.visit_in(60 * 24)
        started = self.visit_in(-30)
        self.login(self.agent)
        today = ecuador_today()
        response = self.client.get(AGENDA_URL, {'from': (today - timedelta(days=1)).isoformat(),
                                                'to': (today + timedelta(days=2)).isoformat()})
        flags = {v['id']: v['can_cancel'] for v in response.data['visits']}
        self.assertEqual(flags, {future.pk: True, started.pk: False})


# =============================================================================================
# Lotes 5 y 6 (DS-52): HU-23 registrar o reprogramar una visita coordinada
# =============================================================================================

COORDINATED_URL = '/api/visits/coordinated/'
COORDINATED_SLOTS_URL = '/api/visits/coordinated/free-slots/'


def reschedule_url(visit_id):
    return f'/api/visits/{visit_id}/reschedule/'


def reschedule_slots_url(visit_id):
    return f'/api/visits/{visit_id}/reschedule-slots/'


class CoordinatedVisitTests(HU19TestMixin, TestCase):
    '''HU-23 (I-08): el asesor registra la visita coordinada por WhatsApp (DS-52).'''

    def coordinated(self, user=None, start=None, at=None, **overrides):
        data = self.payload(start=start, property=self.property.pk, **overrides)
        if user is not None:
            self.login(user)
        with mock.patch('django.utils.timezone.now',
                        return_value=at or local(self.monday, 6)):
            return self.post_to(COORDINATED_URL, data)

    def post_to(self, url, data):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(url, data, format='json')

    def test_agent_registers_new_contact_with_whatsapp_channel(self):
        response = self.coordinated(self.agent)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['status'], 'PROGRAMADA')
        contact = Contact.objects.get(phone=NEW_PHONE_E164)
        self.assertEqual(contact.origin_channel, OriginChannel.WHATSAPP)
        visit = Visit.objects.get()
        self.assertEqual((visit.agent, visit.scheduled_start), (self.agent, self.start))
        opportunity = visit.opportunity
        self.assertEqual(opportunity.status, Opportunity.Status.VISITA_PROGRAMADA)
        self.assertTrue(all(row.changed_by == self.agent
                            for row in opportunity.status_history.all()))
        event = opportunity.interactions.get()
        self.assertIn('registró la visita coordinada', event.notes)
        self.assertIn('avisa por WhatsApp', event.notes)  # Sin correo del cliente
        self.assertEqual(mail.outbox, [])  # Quien registra no se avisa a si mismo

    def test_existing_contact_and_opportunity_are_reused_without_changes(self):
        Opportunity.objects.filter(pk=self.opportunity.pk).update(
            status=Opportunity.Status.CONTACTO_INICIAL)
        response = self.coordinated(self.agent, phone=EXISTING_PHONE, full_name='Otro Nombre')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.full_name, 'Carla Cliente')
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Visit.objects.get().opportunity, self.opportunity)

    def test_client_email_gets_the_confirmation_link(self):
        response = self.coordinated(self.agent, email='nuevo@correo.ec', email_opt_in=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        visit = Visit.objects.get()
        self.assertEqual([m.to for m in mail.outbox], [['nuevo@correo.ec']])
        self.assertIn(str(visit.cancellation_token), mail.outbox[0].body)
        self.assertNotIn('avisa por WhatsApp', visit.opportunity.interactions.get().notes)

    def test_agent_needs_30_minutes_while_client_still_needs_2_hours(self):
        at = local(self.monday, 8, 15)  # 45 min antes de las 09:00
        with mock.patch('django.utils.timezone.now', return_value=at):
            client_response = self.post(self.payload())
        self.assertEqual(client_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.coordinated(self.agent, at=at).status_code,
                         status.HTTP_201_CREATED)
        late = local(self.monday, 9, 40)  # 20 min antes de las 10:00: no
        response = self.coordinated(self.agent, start=local(self.monday, 10), at=late,
                                    phone='0981112222')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start', response.data)

    def test_no_double_booking(self):
        self.assertEqual(self.coordinated(self.agent).status_code, status.HTTP_201_CREATED)
        response = self.coordinated(self.agent, phone='0981112222')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Visit.objects.count(), 1)

    def test_already_scheduled_opportunity_is_409(self):
        self.coordinated(self.agent)
        response = self.coordinated(self.agent, start=local(self.monday, 10))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_lopdp_and_phone_are_required(self):
        self.assertIn('privacy_accepted',
                      self.coordinated(self.agent, privacy_accepted=False).data)
        self.assertIn('phone', self.coordinated(self.agent, phone='022345678').data)
        self.assertFalse(Visit.objects.exists())

    def test_permissions(self):
        self.assertEqual(self.coordinated().status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.coordinated(self.other_agent).status_code,
                         status.HTTP_403_FORBIDDEN)
        response = self.coordinated(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Visit.objects.get().agent, self.agent)  # El asesor de la propiedad
        self.assertEqual([m.to for m in mail.outbox], [['asesor.visitas@urbanex.ec']])

    def test_free_slots_for_the_agent_use_30_minutes(self):
        self.login(self.agent)
        params = {'property': self.property.pk, 'from': self.monday.isoformat(),
                  'to': self.monday.isoformat()}
        with mock.patch('django.utils.timezone.now', return_value=local(self.monday, 8, 15)):
            starts = [slot['start'] for slot in
                      self.client.get(COORDINATED_SLOTS_URL, params).data['slots']]
        self.assertEqual(starts[0], local(self.monday, 9).isoformat())
        self.login(self.other_agent)
        self.assertEqual(self.client.get(COORDINATED_SLOTS_URL, params).status_code,
                         status.HTTP_403_FORBIDDEN)


class RescheduleVisitTests(HU19TestMixin, TestCase):
    '''HU-23 (I-08): reprogramar sin solapes y con aviso (DS-52).'''

    def setUp(self):
        super().setUp()
        Opportunity.objects.filter(pk=self.opportunity.pk).update(
            status=Opportunity.Status.VISITA_PROGRAMADA)
        self.scheduled = self.visit(local(self.monday, 9), local(self.monday, 10))
        Visit.objects.filter(pk=self.scheduled.pk).update(confirmation_email='carla@correo.ec')

    def reschedule(self, user=None, start=None, at=None, visit=None):
        if user is not None:
            self.login(user)
        with mock.patch('django.utils.timezone.now',
                        return_value=at or local(self.monday, 6)):
            with self.captureOnCommitCallbacks(execute=True):
                return self.client.post(reschedule_url((visit or self.scheduled).pk),
                                        {'start': (start or local(self.monday, 11)).isoformat()},
                                        format='json')

    def test_moves_the_same_visit_frees_old_slot_and_notifies_client(self):
        token = self.scheduled.cancellation_token
        response = self.reschedule(self.agent)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.scheduled.refresh_from_db()
        self.assertEqual((self.scheduled.scheduled_start, self.scheduled.scheduled_end),
                         (local(self.monday, 11), local(self.monday, 12)))
        self.assertEqual(self.scheduled.cancellation_token, token)  # Mismo enlace de P-08
        starts = [s.start for s in free_slots(self.agent, self.monday, self.monday,
                                              now=local(self.monday, 6))]
        self.assertIn(local(self.monday, 9), starts)
        self.assertNotIn(local(self.monday, 11), starts)
        event = self.opportunity.interactions.get()
        self.assertIn('reprogramó la visita', event.notes)
        self.assertEqual([m.to for m in mail.outbox], [['carla@correo.ec']])
        self.assertIn(str(token), mail.outbox[0].body)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, Opportunity.Status.VISITA_PROGRAMADA)

    def test_without_client_email_history_says_whatsapp(self):
        Visit.objects.filter(pk=self.scheduled.pk).update(confirmation_email='')
        self.assertEqual(self.reschedule(self.agent).status_code, status.HTTP_200_OK)
        self.assertIn('avisa por WhatsApp', self.opportunity.interactions.get().notes)
        self.assertEqual(mail.outbox, [])

    def test_no_overlap_with_another_visit(self):
        other = Opportunity.objects.create(
            contact=Contact.objects.create(full_name='Otro', phone='+593980000000',
                                           origin_channel=OriginChannel.MANUAL),
            property=self.property, assigned_agent=self.agent,
            origin_channel=OriginChannel.MANUAL)
        self.visit(local(self.monday, 11), local(self.monday, 12), opportunity=other)
        response = self.reschedule(self.agent)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start', response.data)
        self.scheduled.refresh_from_db()
        self.assertEqual(self.scheduled.scheduled_start, local(self.monday, 9))

    def test_needs_30_minutes_and_only_before_start(self):
        later = self.visit(local(self.monday, 11), local(self.monday, 12),
                           opportunity=Opportunity.objects.create(
                               contact=Contact.objects.create(
                                   full_name='Otro', phone='+593980000000',
                                   origin_channel=OriginChannel.MANUAL),
                               property=self.property, assigned_agent=self.agent,
                               origin_channel=OriginChannel.MANUAL))
        Visit.objects.filter(pk=self.scheduled.pk).update(status=Visit.Status.REALIZADA)
        # A las 10:00 con 25 min de antelacion: no; con 35 min: si
        self.assertEqual(self.reschedule(self.agent, start=local(self.monday, 10),
                                         at=local(self.monday, 9, 35), visit=later).status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.reschedule(self.agent, start=local(self.monday, 10),
                                         at=local(self.monday, 9, 25), visit=later).status_code,
                         status.HTTP_200_OK)
        # Visita ya empezada
        self.assertEqual(self.reschedule(self.agent, start=local(self.monday, 11),
                                         at=local(self.monday, 10, 5), visit=later).status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_not_programmed_is_409(self):
        Visit.objects.filter(pk=self.scheduled.pk).update(status=Visit.Status.CANCELADA)
        self.assertEqual(self.reschedule(self.agent).status_code, status.HTTP_409_CONFLICT)

    def test_permissions(self):
        self.assertEqual(self.reschedule().status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.reschedule(self.other_agent).status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.reschedule(self.admin).status_code, status.HTTP_200_OK)
        # El admin reprograma: avisan al cliente y al asesor de la visita
        self.assertEqual(sorted(m.to[0] for m in mail.outbox),
                         ['asesor.visitas@urbanex.ec', 'carla@correo.ec'])

    def test_reschedule_slots_exclude_the_current_slot(self):
        self.login(self.agent)
        with mock.patch('django.utils.timezone.now', return_value=local(self.monday, 6)):
            response = self.client.get(reschedule_slots_url(self.scheduled.pk),
                                       {'from': self.monday.isoformat(),
                                        'to': self.monday.isoformat()})
        self.assertEqual([slot['start'] for slot in response.data['slots']],
                         [local(self.monday, 10).isoformat(), local(self.monday, 11).isoformat()])
