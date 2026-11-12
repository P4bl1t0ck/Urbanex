from datetime import datetime, timedelta
from decimal import Decimal
from unittest import mock
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import Property, PropertyImage
from apps.visits.models import Visit
from .models import (
    Contact, OriginChannel, Opportunity, OpportunityInteraction, OpportunityStatusHistory,
)
from .services import WEB_FORM_EMPTY_NOTE, WEB_FORM_NOTE_PREFIX, WEB_FORM_OPENING_REASON
from .validators import normalize_phone
from .views import INTEREST_OK_MESSAGE, WebInterestBurstThrottle

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


class OpportunityInteractionModelTests(OpportunityTestMixin, TestCase):
    '''HU-30 (DS-50): historial inmutable de interacciones y negociacion.'''

    def setUp(self):
        super().setUp()
        self.opp = self.opportunity()
        self.other_opp = self.opportunity(property=self.other_property)

    def interaction(self, **kwargs):
        data = {'opportunity': self.opp, 'author': self.agent,
                'interaction_type': OpportunityInteraction.Type.NOTA, 'notes': 'Llamó el cliente'}
        data.update(kwargs)
        return OpportunityInteraction(**data)

    def visit_for(self, opportunity):
        start = timezone.now() + timedelta(days=1)
        return Visit.objects.create(
            opportunity=opportunity, property=opportunity.property, agent=self.agent,
            scheduled_start=start, scheduled_end=start + timedelta(hours=1),
        )

    def test_valid_note_counteroffer_and_system_entries(self):
        cases = [
            self.interaction(),
            self.interaction(interaction_type=OpportunityInteraction.Type.CONTRAOFERTA,
                             offered_price=Decimal('140000.00'), notes='Ofrece menos'),
            self.interaction(interaction_type=OpportunityInteraction.Type.SISTEMA, author=None,
                             notes='Interés desde el formulario web: ¿sigue disponible?'),
        ]
        for entry in cases:
            with self.subTest(type=entry.interaction_type):
                entry.full_clean()
                entry.save()
                self.assertIsNotNone(entry.created_at)
        self.assertEqual(self.opp.interactions.count(), 3)

    def test_counteroffer_requires_a_positive_price(self):
        for price in (None, Decimal('0'), Decimal('-1')):
            with self.subTest(price=price), self.assertRaises(ValidationError) as ctx:
                self.interaction(interaction_type=OpportunityInteraction.Type.CONTRAOFERTA,
                                 offered_price=price).full_clean()
            self.assertIn('offered_price', ctx.exception.message_dict)

    def test_only_counteroffers_carry_a_price(self):
        for kind in (OpportunityInteraction.Type.NOTA, OpportunityInteraction.Type.SISTEMA):
            with self.subTest(kind=kind), self.assertRaises(ValidationError) as ctx:
                self.interaction(interaction_type=kind, offered_price=Decimal('1000')).full_clean()
            self.assertIn('offered_price', ctx.exception.message_dict)

    def test_database_rejects_price_rules_even_without_clean(self):
        bad = [
            {'interaction_type': OpportunityInteraction.Type.CONTRAOFERTA, 'offered_price': None},
            {'interaction_type': OpportunityInteraction.Type.CONTRAOFERTA,
             'offered_price': Decimal('0')},
            {'interaction_type': OpportunityInteraction.Type.NOTA, 'offered_price': Decimal('5')},
        ]
        for data in bad:
            with self.subTest(**data), transaction.atomic(), self.assertRaises(IntegrityError):
                self.interaction(**data).save()

    def test_notes_are_required(self):
        for notes in ('', '   '):
            with self.subTest(notes=notes), self.assertRaises(ValidationError) as ctx:
                self.interaction(notes=notes).full_clean()
            self.assertIn('notes', ctx.exception.message_dict)

    def test_only_system_entries_may_have_no_author(self):
        for kind in (OpportunityInteraction.Type.NOTA, OpportunityInteraction.Type.CONTRAOFERTA):
            price = Decimal('1000') if kind == OpportunityInteraction.Type.CONTRAOFERTA else None
            with self.subTest(kind=kind):
                entry = self.interaction(interaction_type=kind, author=None, offered_price=price)
                with self.assertRaises(ValidationError) as ctx:
                    entry.full_clean()
                self.assertIn('author', ctx.exception.message_dict)
                with transaction.atomic(), self.assertRaises(IntegrityError):
                    entry.save()

    def test_visit_must_belong_to_the_same_opportunity(self):
        own_visit = self.visit_for(self.opp)
        self.interaction(visit=own_visit).full_clean()
        with self.assertRaises(ValidationError) as ctx:
            self.interaction(visit=self.visit_for(self.other_opp)).full_clean()
        self.assertIn('visit', ctx.exception.message_dict)

    def test_entry_cannot_be_modified(self):
        entry = self.interaction()
        entry.save()
        entry.notes = 'Cambio retroactivo'
        with self.assertRaises(ValidationError):
            entry.save()
        with self.assertRaises(ValidationError):
            OpportunityInteraction.objects.update(notes='Cambio retroactivo')
        entry.refresh_from_db()
        self.assertEqual(entry.notes, 'Llamó el cliente')

    def test_entry_cannot_be_deleted(self):
        entry = self.interaction()
        entry.save()
        with self.assertRaises(ValidationError):
            entry.delete()
        with self.assertRaises(ValidationError):
            OpportunityInteraction.objects.all().delete()
        self.assertTrue(OpportunityInteraction.objects.filter(pk=entry.pk).exists())

    def test_entries_are_listed_in_chronological_order(self):
        first = self.interaction(notes='Primera')
        first.save()
        second = self.interaction(notes='Segunda')
        second.save()
        self.assertEqual(list(self.opp.interactions.values_list('notes', flat=True)),
                         ['Primera', 'Segunda'])

    def test_opportunity_with_interactions_cannot_be_deleted(self):
        # Sin visitas ni historial: solo la interaccion protege a la oportunidad.
        self.interaction(opportunity=self.other_opp).save()
        with self.assertRaises(ProtectedError):
            self.other_opp.delete()

    def test_visit_linked_to_an_interaction_cannot_be_deleted(self):
        visit = self.visit_for(self.opp)
        self.interaction(visit=visit).save()
        with self.assertRaises(ProtectedError):
            visit.delete()

    def test_counteroffer_does_not_change_the_public_price(self):
        self.interaction(interaction_type=OpportunityInteraction.Type.CONTRAOFERTA,
                         offered_price=Decimal('100000')).save()
        self.property.refresh_from_db()
        self.assertEqual(self.property.price, 150000)


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

    def legacy_client_user(self):
        # C-08 (DS-30): una base puede conservar el valor heredado 'cliente' aunque User.Role
        # ya solo tenga admin y asesor. Se escribe con update(), como lo dejaria una migracion.
        user = User.objects.create_user(
            username='cliente.heredado', email='cliente.heredado@urbanex.ec',
            password='Password123!', role='asesor',
        )
        User.objects.filter(pk=user.pk).update(role='cliente')
        user.refresh_from_db()
        return user


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

    def test_anonymous_cannot_open(self):
        # C-08: el cliente no tiene cuenta; quien no es interno llega como visitante anonimo.
        response = self.client.post(OPPORTUNITIES_URL, self.payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Opportunity.objects.exists())

    def test_user_without_internal_role_cannot_open(self):
        # DT-106: rama del 403 de IsInternalUser (sesion iniciada, rol no interno).
        response = self.open(self.legacy_client_user())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
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

    def test_anonymous_cannot_list(self):
        self.assertEqual(self.client.get(OPPORTUNITIES_URL).status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_user_without_internal_role_cannot_list(self):
        # DT-106: con sesion pero sin rol interno, 403 y ninguna oportunidad en la respuesta.
        self.client.force_authenticate(self.legacy_client_user())
        response = self.client.get(OPPORTUNITIES_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn('results', response.data)


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


# ---------------------------------------------------------------------------------------------
# Lote 4 (DS-50): HU-15 (WhatsApp) y HU-16 (formulario de interes) en la ficha publica P-07
# ---------------------------------------------------------------------------------------------

def whatsapp_url(property_id):
    return f'/api/opportunities/public/properties/{property_id}/whatsapp/'


def interest_url(property_id):
    return f'/api/opportunities/public/properties/{property_id}/interest/'


class PublicP07Mixin(OpportunityTestMixin):
    def setUp(self):
        super().setUp()
        cache.clear()  # Los throttles publicos guardan sus contadores en la cache
        self.client = APIClient()
        self.agent.phone = '099 765 4321'
        self.agent.save(update_fields=['phone'])


class WhatsAppContactApiTests(PublicP07Mixin, TestCase):
    '''HU-15 (RF-02, DS-50): numero del asesor para wa.me, o null para ocultar el boton.'''

    def test_returns_the_normalized_agent_number_without_plus(self):
        response = self.client.get(whatsapp_url(self.property.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'property': self.property.pk,
                                         'whatsapp_phone': '593997654321'})

    def test_e164_agent_phone_is_accepted(self):
        self.agent.phone = '+593 99 765 4321'
        self.agent.save(update_fields=['phone'])
        response = self.client.get(whatsapp_url(self.property.pk))
        self.assertEqual(response.data['whatsapp_phone'], '593997654321')

    def test_invalid_or_missing_agent_phone_hides_the_button(self):
        for phone in ('', '022345678', '+573001234567', 'sin telefono'):
            with self.subTest(phone=phone):
                self.agent.phone = phone
                self.agent.save(update_fields=['phone'])
                response = self.client.get(whatsapp_url(self.property.pk))
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsNone(response.data['whatsapp_phone'])

    def test_inactive_agent_hides_the_button(self):
        self.agent.is_active = False
        self.agent.save(update_fields=['is_active'])
        self.assertIsNone(self.client.get(whatsapp_url(self.property.pk)).data['whatsapp_phone'])

    def test_property_that_is_not_available_or_does_not_exist_returns_404(self):
        self.property.status = 'captacion'
        self.property.save(update_fields=['status'])
        for property_id in (self.property.pk, 999999):
            with self.subTest(property_id=property_id):
                response = self.client.get(whatsapp_url(property_id))
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_an_invalid_token_does_not_block_the_public_endpoint(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer token-vencido')
        self.assertEqual(self.client.get(whatsapp_url(self.property.pk)).status_code,
                         status.HTTP_200_OK)

    def test_requests_are_limited_per_ip(self):
        codes = [self.client.get(whatsapp_url(self.property.pk)).status_code for _ in range(31)]
        self.assertEqual(codes[29], status.HTTP_200_OK)
        self.assertEqual(codes[30], status.HTTP_429_TOO_MANY_REQUESTS)


class WebInterestApiTests(PublicP07Mixin, TestCase):
    '''HU-16 (RF-03, DS-50): interes del visitante sin cuenta desde la ficha publica.'''

    NEW_PHONE = '0981112233'

    def payload(self, **overrides):
        data = {'full_name': 'Carla Visitante', 'phone': self.NEW_PHONE, 'email': '',
                'email_opt_in': False, 'message': '¿Aceptan crédito hipotecario?',
                'privacy_accepted': True}
        data.update(overrides)
        return data

    def post(self, data, property_id=None):
        return self.client.post(interest_url(property_id or self.property.pk), data,
                                format='json')

    def test_new_visitor_creates_contact_opportunity_history_and_interaction(self):
        response = self.post(self.payload(email='carla@correo.ec', email_opt_in=True))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'detail': INTEREST_OK_MESSAGE})

        contact = Contact.objects.get(phone='+593981112233')
        self.assertEqual(contact.origin_channel, OriginChannel.CATALOGO_WEB)
        self.assertIsNotNone(contact.privacy_accepted_at)
        self.assertEqual((contact.email, contact.email_opt_in), ('carla@correo.ec', True))

        opportunity = Opportunity.objects.get(contact=contact)
        self.assertEqual(opportunity.status, Opportunity.Status.CONTACTO_INICIAL)
        self.assertEqual(opportunity.assigned_agent, self.agent)
        self.assertEqual(opportunity.origin_channel, OriginChannel.CATALOGO_WEB)

        opening = opportunity.status_history.get()
        self.assertEqual((opening.previous_status, opening.new_status, opening.changed_by),
                         ('', Opportunity.Status.CONTACTO_INICIAL, None))
        self.assertEqual(opening.reason, WEB_FORM_OPENING_REASON)

        interaction = opportunity.interactions.get()
        self.assertEqual(interaction.interaction_type, OpportunityInteraction.Type.SISTEMA)
        self.assertIsNone(interaction.author)
        self.assertEqual(interaction.notes,
                         f'{WEB_FORM_NOTE_PREFIX}¿Aceptan crédito hipotecario?')

    def test_empty_message_stores_the_default_note(self):
        for phone, message in (('0981112201', ''), ('0981112202', '   ')):
            with self.subTest(message=message):
                self.post(self.payload(phone=phone, message=message))
                interaction = OpportunityInteraction.objects.get(
                    opportunity__contact__phone=normalize_phone(phone))
                self.assertEqual(interaction.notes, WEB_FORM_EMPTY_NOTE)

    def test_message_is_optional_when_missing(self):
        data = self.payload()
        del data['message']
        self.assertEqual(self.post(data).status_code, status.HTTP_201_CREATED)
        self.assertEqual(OpportunityInteraction.objects.get().notes, WEB_FORM_EMPTY_NOTE)

    def test_existing_contact_is_reused_and_only_its_consent_is_renewed(self):
        old_consent = timezone.now() - timedelta(days=30)
        Contact.objects.filter(pk=self.contact.pk).update(
            email='ana@correo.ec', email_opt_in=False, privacy_accepted_at=old_consent,
        )
        response = self.post(self.payload(full_name='Otro Nombre', phone='0991234567',
                                          email='nuevo@correo.ec', email_opt_in=True))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)
        self.contact.refresh_from_db()
        self.assertEqual((self.contact.full_name, self.contact.email, self.contact.email_opt_in),
                         ('Ana Interesada', 'ana@correo.ec', False))
        self.assertGreater(self.contact.privacy_accepted_at, old_consent)
        self.assertEqual(self.contact.origin_channel, OriginChannel.MANUAL)

    def test_active_opportunity_is_reused_without_changing_state_or_agent(self):
        other_agent = User.objects.create_user(
            username='asesor.dos', email='asesor.dos@urbanex.ec', password='Password123!',
            role='asesor',
        )
        existing = self.opportunity(status=Opportunity.Status.VISITA_PROGRAMADA)
        Opportunity.objects.filter(pk=existing.pk).update(
            assigned_agent=other_agent, last_activity_at=timezone.now() - timedelta(days=5),
        )
        before = Opportunity.objects.get(pk=existing.pk).last_activity_at

        response = self.post(self.payload(phone='0991234567'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Opportunity.objects.count(), 1)
        existing.refresh_from_db()
        self.assertEqual(existing.status, Opportunity.Status.VISITA_PROGRAMADA)
        self.assertEqual(existing.assigned_agent, other_agent)
        self.assertGreater(existing.last_activity_at, before)
        self.assertFalse(existing.status_history.exists())
        self.assertEqual(existing.interactions.count(), 1)

    def test_terminal_opportunity_does_not_block_a_new_one(self):
        self.opportunity(status=Opportunity.Status.PERDIDA)
        self.post(self.payload(phone='0991234567'))
        self.assertEqual(Opportunity.objects.active().filter(contact=self.contact).count(), 1)

    def test_response_is_the_same_for_new_and_known_visitors(self):
        first = self.post(self.payload())
        again = self.post(self.payload(full_name='Otra persona'))
        self.assertEqual(first.data, again.data)
        self.assertEqual(set(first.data), {'detail'})
        self.assertEqual(Opportunity.objects.count(), 1)
        self.assertEqual(OpportunityInteraction.objects.count(), 2)

    def test_invalid_data_returns_400_and_saves_nothing(self):
        cases = [
            ({'privacy_accepted': False}, 'privacy_accepted'),
            ({'phone': '022345678'}, 'phone'),
            ({'phone': ''}, 'phone'),
            ({'full_name': '   '}, 'full_name'),
            ({'email': 'no-es-correo'}, 'email'),
            ({'email': '', 'email_opt_in': True}, 'email'),
            ({'message': 'x' * 1001}, 'message'),
        ]
        for overrides, field in cases:
            with self.subTest(field=field, overrides=overrides):
                cache.clear()
                response = self.post(self.payload(**overrides))
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        self.assertEqual(Contact.objects.count(), 1)  # Solo el del mixin
        self.assertFalse(Opportunity.objects.exists())
        self.assertFalse(OpportunityInteraction.objects.exists())

    def test_unavailable_property_or_inactive_agent_returns_404_and_saves_nothing(self):
        self.other_property.status = 'reservado'
        self.other_property.save(update_fields=['status'])
        self.assertEqual(self.post(self.payload(), self.other_property.pk).status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.post(self.payload(), 999999).status_code, status.HTTP_404_NOT_FOUND)

        self.agent.is_active = False
        self.agent.save(update_fields=['is_active'])
        self.assertEqual(self.post(self.payload()).status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Contact.objects.filter(phone='+593981112233').exists())
        self.assertFalse(Opportunity.objects.exists())

    def test_public_price_is_not_touched(self):
        self.post(self.payload())
        self.property.refresh_from_db()
        self.assertEqual(self.property.price, 150000)


class WebInterestThrottleTests(PublicP07Mixin, TestCase):
    '''HU-16: 3 por minuto y 10 por dia por IP (DS-50).'''

    def post(self, index):
        return self.client.post(interest_url(self.property.pk), {
            'full_name': 'Visitante', 'phone': f'09811122{index:02d}', 'privacy_accepted': True,
        }, format='json')

    def test_fourth_request_in_a_minute_is_rejected(self):
        codes = [self.post(i).status_code for i in range(4)]
        self.assertEqual(codes[:3], [status.HTTP_201_CREATED] * 3)
        self.assertEqual(codes[3], status.HTTP_429_TOO_MANY_REQUESTS)

    def test_eleventh_request_in_a_day_is_rejected(self):
        with mock.patch.object(WebInterestBurstThrottle, 'default_rate', '100/minute'):
            codes = [self.post(i).status_code for i in range(11)]
        self.assertEqual(codes[:10], [status.HTTP_201_CREATED] * 10)
        self.assertEqual(codes[10], status.HTTP_429_TOO_MANY_REQUESTS)

    def test_rate_can_be_configured_in_settings_without_code_changes(self):
        rest = {**settings.REST_FRAMEWORK,
                'DEFAULT_THROTTLE_RATES': {'opportunities_interest_burst': '1/minute'}}
        with override_settings(REST_FRAMEWORK=rest):
            codes = [self.post(i).status_code for i in range(2)]
        self.assertEqual(codes, [status.HTTP_201_CREATED, status.HTTP_429_TOO_MANY_REQUESTS])


# ---------------------------------------------------------------------------------------------
# Lote 4 (DS-50): HU-29 avanzar el estado y HU-30 interacciones, detalle I-06A
# ---------------------------------------------------------------------------------------------

def detail_url(opportunity_id):
    return f'{OPPORTUNITIES_URL}{opportunity_id}/'


def status_url(opportunity_id):
    return f'{OPPORTUNITIES_URL}{opportunity_id}/status/'


def interactions_url(opportunity_id):
    return f'{OPPORTUNITIES_URL}{opportunity_id}/interactions/'


class I06AMixin(OpportunityApiMixin):
    def setUp(self):
        super().setUp()
        self.opp = self.opportunity()
        self.client.force_authenticate(self.agent)

    def add_visit(self, opportunity=None, visit_status=Visit.Status.PROGRAMADA, days=1):
        opportunity = opportunity or self.opp
        start = timezone.now() + timedelta(days=days)
        return Visit.objects.create(
            opportunity=opportunity, property=opportunity.property, agent=self.agent,
            scheduled_start=start, scheduled_end=start + timedelta(hours=1), status=visit_status,
        )

    def set_status(self, value, opportunity=None):
        opportunity = opportunity or self.opp
        Opportunity.objects.filter(pk=opportunity.pk).update(status=value)
        opportunity.refresh_from_db()

    def advance(self, target, **extra):
        return self.client.post(status_url(self.opp.pk), {'status': target, **extra},
                                format='json')


class StatusAdvanceApiTests(I06AMixin, TestCase):
    '''HU-29 (RF-06, DS-50): un paso a la vez, con sus requisitos.'''

    def test_full_sequence_with_its_requirements(self):
        visit = self.add_visit()
        response = self.advance(Opportunity.Status.VISITA_PROGRAMADA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], Opportunity.Status.VISITA_PROGRAMADA)
        self.assertEqual(response.data['next_status'], Opportunity.Status.EN_NEGOCIACION)

        # Sin una visita REALIZADA no se negocia (RF-04).
        response = self.advance(Opportunity.Status.EN_NEGOCIACION)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
        Visit.objects.filter(pk=visit.pk).update(status=Visit.Status.REALIZADA)
        self.assertEqual(self.advance(Opportunity.Status.EN_NEGOCIACION).status_code,
                         status.HTTP_200_OK)

        response = self.advance(Opportunity.Status.PENDIENTE_CIERRE)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('agreed_final_price', response.data)
        response = self.advance(Opportunity.Status.PENDIENTE_CIERRE,
                                agreed_final_price='142500.00')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['next_status'])

        self.opp.refresh_from_db()
        self.assertEqual(self.opp.status, Opportunity.Status.PENDIENTE_CIERRE)
        self.assertEqual(self.opp.agreed_final_price, Decimal('142500.00'))
        history = list(self.opp.status_history.values_list(
            'previous_status', 'new_status', 'changed_by', 'reason'))
        self.assertEqual([row[:2] for row in history], [
            (Opportunity.Status.CONTACTO_INICIAL, Opportunity.Status.VISITA_PROGRAMADA),
            (Opportunity.Status.VISITA_PROGRAMADA, Opportunity.Status.EN_NEGOCIACION),
            (Opportunity.Status.EN_NEGOCIACION, Opportunity.Status.PENDIENTE_CIERRE),
        ])
        self.assertTrue(all(row[2] == self.agent.pk and row[3] for row in history))
        self.property.refresh_from_db()
        self.assertEqual(self.property.price, 150000)  # El precio publico no cambia

    def test_visita_programada_needs_a_programmed_or_completed_visit(self):
        self.assertEqual(self.advance(Opportunity.Status.VISITA_PROGRAMADA).status_code,
                         status.HTTP_400_BAD_REQUEST)
        for visit_status in (Visit.Status.CANCELADA, Visit.Status.NO_ASISTIDA):
            self.add_visit(visit_status=visit_status, days=-2)
        self.assertEqual(self.advance(Opportunity.Status.VISITA_PROGRAMADA).status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.add_visit(visit_status=Visit.Status.REALIZADA, days=-1)
        self.assertEqual(self.advance(Opportunity.Status.VISITA_PROGRAMADA).status_code,
                         status.HTTP_200_OK)

    def test_visit_of_another_opportunity_does_not_count(self):
        other = self.opportunity(property=self.other_property)
        self.add_visit(opportunity=other)
        self.assertEqual(self.advance(Opportunity.Status.VISITA_PROGRAMADA).status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_cannot_skip_steps_or_go_back(self):
        self.add_visit(visit_status=Visit.Status.REALIZADA, days=-1)
        for target in (Opportunity.Status.EN_NEGOCIACION, Opportunity.Status.PENDIENTE_CIERRE,
                       Opportunity.Status.CONTACTO_INICIAL, Opportunity.Status.PERDIDA,
                       Opportunity.Status.CIERRE):
            with self.subTest(target=target):
                response = self.advance(target, agreed_final_price='1000.00')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.set_status(Opportunity.Status.EN_NEGOCIACION)
        self.assertEqual(self.advance(Opportunity.Status.VISITA_PROGRAMADA).status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.opp.status_history.exists())

    def test_states_outside_the_cut_do_not_advance(self):
        for current in (Opportunity.Status.PENDIENTE_CIERRE, Opportunity.Status.LISTA_INTERESADOS,
                        Opportunity.Status.RESERVADA, Opportunity.Status.CIERRE,
                        Opportunity.Status.PERDIDA):
            with self.subTest(current=current):
                self.set_status(current)
                for target in Opportunity.Status.values:
                    self.assertEqual(self.advance(target).status_code,
                                     status.HTTP_400_BAD_REQUEST)

    def test_price_only_on_the_step_to_pendiente_cierre_and_positive(self):
        self.add_visit()
        response = self.advance(Opportunity.Status.VISITA_PROGRAMADA, agreed_final_price='5000')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('agreed_final_price', response.data)
        self.set_status(Opportunity.Status.EN_NEGOCIACION)
        for price in ('0', '-10', 'abc'):
            with self.subTest(price=price):
                response = self.advance(Opportunity.Status.PENDIENTE_CIERRE,
                                        agreed_final_price=price)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.opp.refresh_from_db()
        self.assertIsNone(self.opp.agreed_final_price)

    def test_unknown_status_is_rejected(self):
        self.assertEqual(self.advance('GANADA').status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_advance_any_opportunity(self):
        self.add_visit()
        self.client.force_authenticate(self.admin)
        response = self.advance(Opportunity.Status.VISITA_PROGRAMADA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.opp.status_history.get().changed_by, self.admin)

    def test_other_agent_gets_404_and_nothing_changes(self):
        self.add_visit()
        self.client.force_authenticate(self.other_agent)
        self.assertEqual(self.advance(Opportunity.Status.VISITA_PROGRAMADA).status_code,
                         status.HTTP_404_NOT_FOUND)
        self.opp.refresh_from_db()
        self.assertEqual(self.opp.status, Opportunity.Status.CONTACTO_INICIAL)

    def test_anonymous_and_non_internal_users_are_rejected(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.advance(Opportunity.Status.VISITA_PROGRAMADA).status_code,
                         status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.legacy_client_user())
        self.assertEqual(self.advance(Opportunity.Status.VISITA_PROGRAMADA).status_code,
                         status.HTTP_403_FORBIDDEN)


class InteractionApiTests(I06AMixin, TestCase):
    '''HU-30 (RF-06, DS-50): NOTA y CONTRAOFERTA del asesor asignado o del admin.'''

    def post(self, **data):
        return self.client.post(interactions_url(self.opp.pk), data, format='json')

    def test_agent_registers_a_note(self):
        before = self.opp.last_activity_at
        response = self.post(interaction_type='NOTA', notes='  Llamó para pedir planos  ')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['notes'], 'Llamó para pedir planos')
        self.assertEqual(response.data['author']['id'], self.agent.pk)
        self.assertIsNone(response.data['offered_price'])
        self.opp.refresh_from_db()
        self.assertGreater(self.opp.last_activity_at, before)

    def test_counteroffer_needs_a_positive_price_and_keeps_the_public_price(self):
        for price in (None, '0', '-1'):
            with self.subTest(price=price):
                response = self.post(interaction_type='CONTRAOFERTA', notes='Ofrece menos',
                                     offered_price=price)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('offered_price', response.data)
        response = self.post(interaction_type='CONTRAOFERTA', notes='Ofrece 140 mil',
                             offered_price='140000.00')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['offered_price'], '140000.00')
        self.property.refresh_from_db()
        self.opp.refresh_from_db()
        self.assertEqual(self.property.price, 150000)
        self.assertIsNone(self.opp.agreed_final_price)

    def test_note_cannot_carry_a_price(self):
        response = self.post(interaction_type='NOTA', notes='Nota', offered_price='100')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('offered_price', response.data)

    def test_system_type_and_empty_notes_are_rejected(self):
        cases = (({'interaction_type': 'SISTEMA', 'notes': 'Falso'}, 'interaction_type'),
                 ({'interaction_type': 'OTRO', 'notes': 'x'}, 'interaction_type'),
                 ({'interaction_type': 'NOTA', 'notes': '   '}, 'notes'),
                 ({'interaction_type': 'NOTA'}, 'notes'))
        for data, field in cases:
            with self.subTest(data=data):
                response = self.post(**data)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        self.assertFalse(OpportunityInteraction.objects.exists())

    def test_visit_must_belong_to_the_opportunity(self):
        other = self.opportunity(property=self.other_property)
        foreign = self.add_visit(opportunity=other)
        response = self.post(interaction_type='NOTA', notes='Sobre la visita', visit=foreign.pk)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('visit', response.data)
        own = self.add_visit(days=2)
        response = self.post(interaction_type='NOTA', notes='Sobre la visita', visit=own.pk)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['visit'], own.pk)

    def test_list_is_chronological_and_includes_system_entries(self):
        OpportunityInteraction.objects.create(
            opportunity=self.opp, interaction_type=OpportunityInteraction.Type.SISTEMA,
            notes=WEB_FORM_EMPTY_NOTE,
        )
        self.post(interaction_type='NOTA', notes='Segunda')
        response = self.client.get(interactions_url(self.opp.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([row['notes'] for row in response.data],
                         [WEB_FORM_EMPTY_NOTE, 'Segunda'])
        self.assertIsNone(response.data[0]['author'])

    def test_closed_opportunity_rejects_new_interactions_but_lost_one_accepts(self):
        self.set_status(Opportunity.Status.CIERRE)
        response = self.post(interaction_type='NOTA', notes='Después del cierre')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertFalse(OpportunityInteraction.objects.exists())
        self.set_status(Opportunity.Status.PERDIDA)
        self.assertEqual(self.post(interaction_type='NOTA', notes='Seguimiento').status_code,
                         status.HTTP_201_CREATED)

    def test_admin_can_register_and_other_agent_gets_404(self):
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.post(interaction_type='NOTA', notes='Del admin').status_code,
                         status.HTTP_201_CREATED)
        self.client.force_authenticate(self.other_agent)
        self.assertEqual(self.post(interaction_type='NOTA', notes='Ajena').status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.get(interactions_url(self.opp.pk)).status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertEqual(OpportunityInteraction.objects.count(), 1)


class OpportunityDetailApiTests(I06AMixin, TestCase):
    '''I-06A (DS-50): detalle de la oportunidad para el asesor asignado o el admin.'''

    def test_detail_has_next_status_history_interactions_and_visits(self):
        OpportunityStatusHistory.objects.create(
            opportunity=self.opp, new_status=self.opp.status, changed_by=None,
            reason=WEB_FORM_OPENING_REASON,
        )
        OpportunityInteraction.objects.create(
            opportunity=self.opp, interaction_type=OpportunityInteraction.Type.SISTEMA,
            notes=WEB_FORM_EMPTY_NOTE,
        )
        visit = self.add_visit()
        response = self.client.get(detail_url(self.opp.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['next_status'], Opportunity.Status.VISITA_PROGRAMADA)
        self.assertEqual(data['next_status_display'], 'Visita programada')
        self.assertIsNone(data['agreed_final_price'])
        self.assertIsNone(data['status_history'][0]['changed_by'])
        self.assertEqual(data['interactions'][0]['notes'], WEB_FORM_EMPTY_NOTE)
        self.assertEqual([row['id'] for row in data['visits']], [visit.pk])
        self.assertEqual(data['contact']['phone'], self.contact.phone)

    def test_other_agent_gets_404_and_admin_sees_it(self):
        self.client.force_authenticate(self.other_agent)
        self.assertEqual(self.client.get(detail_url(self.opp.pk)).status_code,
                         status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get(detail_url(self.opp.pk)).status_code,
                         status.HTTP_200_OK)

    def test_detail_says_why_the_next_step_is_blocked(self):
        data = self.client.get(detail_url(self.opp.pk)).data
        self.assertIn('visita programada o realizada', data['advance_blocked_reason'])
        self.assertTrue(data['accepts_interactions'])

        visit = self.add_visit()
        self.assertEqual(self.client.get(detail_url(self.opp.pk)).data['advance_blocked_reason'],
                         '')
        self.set_status(Opportunity.Status.VISITA_PROGRAMADA)
        data = self.client.get(detail_url(self.opp.pk)).data
        self.assertIn('visita realizada', data['advance_blocked_reason'])
        Visit.objects.filter(pk=visit.pk).update(status=Visit.Status.REALIZADA)
        self.assertEqual(self.client.get(detail_url(self.opp.pk)).data['advance_blocked_reason'],
                         '')

        self.set_status(Opportunity.Status.CIERRE)
        data = self.client.get(detail_url(self.opp.pk)).data
        self.assertEqual((data['next_status'], data['advance_blocked_reason']), (None, ''))
        self.assertFalse(data['accepts_interactions'])

    def test_list_filters_do_not_hide_the_detail(self):
        response = self.client.get(detail_url(self.opp.pk), {'status': 'PERDIDA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
