from datetime import datetime, time, timedelta, timezone

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import ECUADOR_TZ, AgentAvailability, AvailabilityException, ecuador_today
from .services import free_slots

AVAILABILITY_URL = '/api/visits/availability/'
EXCEPTIONS_URL = '/api/visits/exceptions/'

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
