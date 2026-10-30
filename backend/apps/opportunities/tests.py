from datetime import datetime
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import SimpleTestCase, TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import Property, PropertyImage
from .models import Contact, OriginChannel, Opportunity, OpportunityStatusHistory
from .validators import normalize_phone

OPPORTUNITIES_URL = '/api/opportunities/'
ELIGIBLE_URL = '/api/opportunities/eligible-properties/'
AGENTS_URL = '/api/opportunities/agents/'

User = get_user_model()


class NormalizePhoneTests(SimpleTestCase):
    def test_local_mobile_is_stored_in_e164(self):
        self.assertEqual(normalize_phone('0991234567'), '+593991234567')

    def test_separators_are_ignored(self):
        self.assertEqual(normalize_phone('099-123 4567'), '+593991234567')
        self.assertEqual(normalize_phone('+593 (99) 123.4567'), '+593991234567')

    def test_e164_mobile_is_kept(self):
        self.assertEqual(normalize_phone('+593991234567'), '+593991234567')

    def test_rejects_landlines_foreign_and_malformed_numbers(self):
        for raw in ['022345678', '0891234567', '099123456', '+573001234567', '593991234567',
                    'abc0991234567', '', None]:
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                normalize_phone(raw)


class OpportunityTestMixin:
    def setUp(self):
        self.agent = User.objects.create_user(
            username='asesor.oportunidades', email='asesor.oportunidades@urbanex.ec',
            password='Password123!', role='asesor',
        )
        self.property = Property.objects.create(
            agent=self.agent, title='Casa en Cumbayá', description='Prueba',
            property_type='casa', price=150000, area_m2=120, location='Cumbayá',
            status='disponible',
        )
        self.other_property = Property.objects.create(
            agent=self.agent, title='Departamento en La Carolina', description='Prueba',
            property_type='departamento', price=120000, area_m2=90, location='La Carolina',
            status='disponible',
        )
        self.contact = Contact.objects.create(
            full_name='Ana Interesada', phone='+593991234567', origin_channel=OriginChannel.MANUAL,
        )

    def opportunity(self, property=None, status=Opportunity.Status.CONTACTO_INICIAL):
        return Opportunity.objects.create(
            contact=self.contact, property=property or self.property, assigned_agent=self.agent,
            origin_channel=OriginChannel.MANUAL, status=status,
        )


class ContactModelTests(OpportunityTestMixin, TestCase):
    def test_phone_is_unique(self):
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Contact.objects.create(full_name='Otra persona', phone='+593991234567',
                                   origin_channel=OriginChannel.MANUAL)

    def test_full_clean_rejects_a_phone_that_was_not_normalized(self):
        contact = Contact(full_name='Sin normalizar', phone='0997654321',
                          origin_channel=OriginChannel.MANUAL)
        with self.assertRaises(ValidationError):
            contact.full_clean()


class OpportunityModelTests(OpportunityTestMixin, TestCase):
    def test_new_opportunity_starts_in_contacto_inicial(self):
        opportunity = self.opportunity()
        self.assertEqual(opportunity.status, Opportunity.Status.CONTACTO_INICIAL)
        self.assertTrue(opportunity.is_active)
        self.assertIsNotNone(opportunity.last_activity_at)

    def test_only_one_active_opportunity_per_contact_and_property(self):
        self.opportunity()
        with transaction.atomic(), self.assertRaises(IntegrityError):
            self.opportunity()

    def test_lista_interesados_and_pendiente_comision_count_as_active(self):
        for status in (Opportunity.Status.LISTA_INTERESADOS, Opportunity.Status.PENDIENTE_COMISION):
            with self.subTest(status=status):
                first = self.opportunity(status=status)
                with transaction.atomic(), self.assertRaises(IntegrityError):
                    self.opportunity()
                Opportunity.objects.filter(pk=first.pk).update(status=Opportunity.Status.PERDIDA)

    def test_terminal_statuses_allow_a_new_opportunity(self):
        for status in (Opportunity.Status.PERDIDA, Opportunity.Status.CIERRE):
            with self.subTest(status=status):
                self.opportunity(status=status)
                new = self.opportunity()
                Opportunity.objects.filter(pk=new.pk).update(status=Opportunity.Status.PERDIDA)
        self.assertEqual(Opportunity.objects.filter(contact=self.contact).count(), 4)
        self.assertFalse(Opportunity.objects.active().exists())

    def test_same_contact_can_have_active_opportunities_on_other_properties(self):
        self.opportunity()
        self.opportunity(property=self.other_property)
        self.assertEqual(Opportunity.objects.active().count(), 2)

    def test_opportunity_with_history_cannot_be_deleted(self):
        opportunity = self.opportunity()
        OpportunityStatusHistory.objects.create(
            opportunity=opportunity, new_status=opportunity.status, changed_by=self.agent,
        )
        with self.assertRaises(ProtectedError):
            opportunity.delete()

    def test_property_with_opportunities_cannot_be_deleted(self):
        self.opportunity()
        with self.assertRaises(ProtectedError):
            self.property.delete()


class OpportunityStatusHistoryTests(OpportunityTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.entry = OpportunityStatusHistory.objects.create(
            opportunity=self.opportunity(), new_status=Opportunity.Status.CONTACTO_INICIAL,
            changed_by=self.agent,
        )

    def test_opening_entry_has_no_previous_status(self):
        self.assertEqual(self.entry.previous_status, '')
        self.assertIsNotNone(self.entry.created_at)

    def test_entry_cannot_be_modified(self):
        self.entry.reason = 'Cambio retroactivo'
        with self.assertRaises(ValidationError):
            self.entry.save()
        with self.assertRaises(ValidationError):
            OpportunityStatusHistory.objects.update(reason='Cambio retroactivo')
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.reason, '')

    def test_entry_cannot_be_deleted(self):
        with self.assertRaises(ValidationError):
            self.entry.delete()
        with self.assertRaises(ValidationError):
            OpportunityStatusHistory.objects.all().delete()
        self.assertTrue(OpportunityStatusHistory.objects.filter(pk=self.entry.pk).exists())


class OpportunityApiMixin(OpportunityTestMixin):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.other_agent = User.objects.create_user(
            username='otro.asesor', email='otro.asesor@urbanex.ec',
            password='Password123!', role='asesor',
        )
        self.admin = User.objects.create_user(
            username='admin.oportunidades', email='admin.oportunidades@urbanex.ec',
            password='Password123!', role='admin',
        )

    def payload(self, **overrides):
        data = {
            'full_name': 'Bruno Comprador', 'phone': '0987654321', 'email': 'bruno@correo.ec',
            'property': self.property.id, 'privacy_accepted': True,
        }
        data.update(overrides)
        return data

    def open(self, user, **overrides):
        self.client.force_authenticate(user)
        return self.client.post(OPPORTUNITIES_URL, self.payload(**overrides), format='json')


class OpportunityOpenApiTests(OpportunityApiMixin, TestCase):
    def test_agent_opens_a_manual_opportunity_for_himself(self):
        response = self.open(self.other_agent)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertFalse(response.data['contact_reused'])

        opportunity = Opportunity.objects.get(pk=response.data['opportunity']['id'])
        self.assertEqual(opportunity.status, Opportunity.Status.CONTACTO_INICIAL)
        self.assertEqual(opportunity.origin_channel, OriginChannel.MANUAL)
        # RF-08: la oportunidad manual se asigna a quien la registra, aunque no sea el captador.
        self.assertEqual(opportunity.assigned_agent, self.other_agent)
        self.assertEqual(opportunity.contact.phone, '+593987654321')
        self.assertEqual(opportunity.contact.origin_channel, OriginChannel.MANUAL)
        self.assertIsNotNone(opportunity.contact.privacy_accepted_at)

        history = list(opportunity.status_history.all())
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].previous_status, '')
        self.assertEqual(history[0].new_status, Opportunity.Status.CONTACTO_INICIAL)
        self.assertEqual(history[0].changed_by, self.other_agent)

    def test_invalid_phone_is_rejected_and_nothing_is_created(self):
        response = self.open(self.agent, phone='022345678')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)
        self.assertFalse(Opportunity.objects.exists())
        self.assertEqual(Contact.objects.count(), 1)  # Solo el del setUp

    def test_privacy_acceptance_is_required(self):
        response = self.open(self.agent, privacy_accepted=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('privacy_accepted', response.data)
        self.assertFalse(Opportunity.objects.exists())

    def test_existing_contact_is_reused_without_changing_its_data(self):
        response = self.open(self.agent, phone='099 123 4567', full_name='Otro nombre',
                             email='otro@correo.ec')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(response.data['contact_reused'])
        self.assertEqual(response.data['opportunity']['contact']['id'], self.contact.id)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.full_name, 'Ana Interesada')
        self.assertEqual(self.contact.email, '')
        self.assertEqual(Contact.objects.count(), 1)

    def test_second_active_opportunity_on_the_same_property_returns_409(self):
        first = self.open(self.agent)
        response = self.open(self.agent, phone='+593 98 765 4321')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['existing_opportunity_id'], first.data['opportunity']['id'])
        self.assertEqual(Opportunity.objects.count(), 1)

    def test_property_that_is_not_available_is_rejected(self):
        for property_status in ('captacion', 'reservador', 'vendido', 'no_disponible'):
            with self.subTest(status=property_status):
                Property.objects.filter(pk=self.property.pk).update(status=property_status)
                response = self.open(self.agent)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('property', response.data)
        self.assertFalse(Opportunity.objects.exists())

    def test_agent_cannot_assign_another_agent(self):
        response = self.open(self.agent, assigned_agent=self.other_agent.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('assigned_agent', response.data)

    def test_admin_must_choose_an_active_agent(self):
        inactive = User.objects.create_user(
            username='inactivo', email='inactivo@urbanex.ec', password='Password123!',
            role='asesor', is_active=False,
        )
        for assigned in (None, inactive.id, self.admin.id):
            with self.subTest(assigned_agent=assigned):
                response = self.open(self.admin, assigned_agent=assigned)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('assigned_agent', response.data)

        response = self.open(self.admin, assigned_agent=self.other_agent.id)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        opportunity = Opportunity.objects.get()
        self.assertEqual(opportunity.assigned_agent, self.other_agent)
        self.assertEqual(opportunity.status_history.get().changed_by, self.admin)

    def test_only_internal_users_can_open(self):
        client_user = User.objects.create_user(
            username='cliente', email='cliente@correo.ec', password='Password123!', role='cliente',
        )
        self.assertEqual(self.open(client_user).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(None)
        response = self.client.post(OPPORTUNITIES_URL, self.payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Opportunity.objects.exists())


class OpportunityListApiTests(OpportunityApiMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.mine = self.opportunity()
        self.mine_other_property = self.opportunity(property=self.other_property,
                                                    status=Opportunity.Status.PERDIDA)
        other_contact = Contact.objects.create(
            full_name='Carla', phone='+593981112222', origin_channel=OriginChannel.MANUAL,
        )
        self.theirs = Opportunity.objects.create(
            contact=other_contact, property=self.property, assigned_agent=self.other_agent,
            origin_channel=OriginChannel.MANUAL,
        )

    def ids(self, user, query=''):
        self.client.force_authenticate(user)
        response = self.client.get(OPPORTUNITIES_URL + query)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        return {row['id'] for row in response.data['results']}

    def test_agent_sees_only_his_portfolio_and_admin_sees_all(self):
        self.assertEqual(self.ids(self.agent), {self.mine.id, self.mine_other_property.id})
        self.assertEqual(self.ids(self.admin),
                         {self.mine.id, self.mine_other_property.id, self.theirs.id})

    def test_agent_filter_does_not_leak_other_portfolios(self):
        self.assertEqual(self.ids(self.agent, f'?assigned_agent={self.other_agent.id}'), set())

    def test_filters_combine(self):
        query = f'?property={self.property.id}&status=CONTACTO_INICIAL'
        self.assertEqual(self.ids(self.admin, query), {self.mine.id, self.theirs.id})
        query += f'&assigned_agent={self.agent.id}'
        self.assertEqual(self.ids(self.admin, query), {self.mine.id})

    def test_date_range_is_read_in_ecuador_time(self):
        # 23:30 del 30-10 en Ecuador = 04:30 del 31-10 en UTC (DT-01); 00:30 del 31-10 = 05:30 UTC.
        ecuador = ZoneInfo('America/Guayaquil')
        Opportunity.objects.filter(pk=self.mine.pk).update(
            created_at=datetime(2026, 10, 30, 23, 30, tzinfo=ecuador))
        Opportunity.objects.filter(pk=self.mine_other_property.pk).update(
            created_at=datetime(2026, 10, 31, 0, 30, tzinfo=ecuador))
        self.assertEqual(self.ids(self.agent, '?created_from=2026-10-30&created_to=2026-10-30'),
                         {self.mine.id})
        self.assertEqual(self.ids(self.agent, '?created_from=2026-10-31&created_to=2026-10-31'),
                         {self.mine_other_property.id})

    def test_malformed_filters_return_400(self):
        self.client.force_authenticate(self.agent)
        for query in ('?status=CERRADA', '?created_from=30-10-2026', '?property=abc',
                      '?created_from=2026-10-31&created_to=2026-10-30'):
            with self.subTest(query=query):
                response = self.client.get(OPPORTUNITIES_URL + query)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_is_paginated_and_shows_no_internal_property_data(self):
        self.client.force_authenticate(self.agent)
        response = self.client.get(OPPORTUNITIES_URL)
        self.assertEqual(response.data['count'], 2)
        row = response.data['results'][0]
        self.assertEqual(set(row['property']), {'id', 'title', 'sector', 'property_type'})
        self.assertEqual(row['assigned_agent']['id'], self.agent.id)

    def test_client_role_cannot_list(self):
        client_user = User.objects.create_user(
            username='cliente', email='cliente@correo.ec', password='Password123!', role='cliente',
        )
        self.client.force_authenticate(client_user)
        self.assertEqual(self.client.get(OPPORTUNITIES_URL).status_code, status.HTTP_403_FORBIDDEN)


class EligiblePropertiesApiTests(OpportunityApiMixin, TestCase):
    def test_only_available_properties_with_public_data(self):
        Property.objects.create(
            agent=self.agent, title='En captación', description='Prueba', property_type='casa',
            price=99000, area_m2=80, location='Tumbaco',
        )
        PropertyImage.objects.create(property=self.property, image='properties/images/foto.png')
        self.client.force_authenticate(self.other_agent)
        response = self.client.get(ELIGIBLE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({row['id'] for row in response.data},
                         {self.property.id, self.other_property.id})
        row = next(row for row in response.data if row['id'] == self.property.id)
        # DS-28: solo datos publicos del catalogo; nada del asesor ni datos internos.
        self.assertEqual(set(row), {'id', 'title', 'sector', 'property_type',
                                    'property_type_display', 'price', 'photo'})
        self.assertEqual(row['sector'], 'Cumbayá')
        self.assertTrue(row['photo'].endswith('/media/properties/images/foto.png'))


class AgentsApiTests(OpportunityApiMixin, TestCase):
    def test_admin_lists_active_agents_only(self):
        User.objects.create_user(username='inactivo', email='inactivo@urbanex.ec',
                                 password='Password123!', role='asesor', is_active=False)
        self.client.force_authenticate(self.admin)
        response = self.client.get(AGENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({row['id'] for row in response.data}, {self.agent.id, self.other_agent.id})

    def test_agent_cannot_list_agents(self):
        self.client.force_authenticate(self.agent)
        self.assertEqual(self.client.get(AGENTS_URL).status_code, status.HTTP_403_FORBIDDEN)
