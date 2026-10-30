from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import SimpleTestCase, TestCase

from apps.users.models import Property
from .models import Contact, OriginChannel, Opportunity, OpportunityStatusHistory
from .validators import normalize_phone

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
