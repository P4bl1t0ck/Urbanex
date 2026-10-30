from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.users.models import Property
from .models import Contact, OriginChannel, Opportunity, OpportunityStatusHistory
from .validators import normalize_phone

'''
Apertura de oportunidades (RF-05). open_manual_opportunity() es la unica via de HU-27 (I-07).
get_or_create_contact() la podran reutilizar HU-15 y HU-16 (RF-02, RF-03) con su propio canal.

Reglas del corte (DS-28):
- Solo usuarios internos (admin o asesor). El asesor queda como responsable (RF-08: la
  oportunidad manual se asigna a quien la registra); el admin elige un asesor activo.
- Solo sobre propiedades disponibles.
- El interesado acepto la politica de privacidad (LOPDP): se guarda la fecha y hora.
- Si el telefono ya existe, se reutiliza el contacto sin modificar su nombre ni su correo.
- Una sola oportunidad activa por contacto e inmueble: si ya hay una, OpportunityConflict.
'''

User = get_user_model()

INTERNAL_ROLES = ('admin', 'asesor')
OPENABLE_PROPERTY_STATUSES = ('disponible',)


class OpportunityConflict(Exception):
    def __init__(self, existing):
        self.existing = existing
        super().__init__('El contacto ya tiene una oportunidad activa sobre este inmueble.')


def is_internal_user(user):
    return getattr(user, 'role', None) in INTERNAL_ROLES


def eligible_properties():
    return Property.objects.filter(status__in=OPENABLE_PROPERTY_STATUSES)


def assignable_agents():
    return User.objects.filter(role='asesor', is_active=True)


def resolve_assigned_agent(registered_by, assigned_agent):
    if registered_by.role == 'admin':
        if assigned_agent is None:
            raise ValidationError({'assigned_agent': 'Elija el asesor responsable de la oportunidad.'})
        if not assignable_agents().filter(pk=assigned_agent.pk).exists():
            raise ValidationError({'assigned_agent': 'El responsable debe ser un asesor activo.'})
        return assigned_agent
    if assigned_agent is not None and assigned_agent.pk != registered_by.pk:
        raise ValidationError({'assigned_agent': 'Solo el administrador elige el asesor responsable.'})
    return registered_by


def get_or_create_contact(*, phone, full_name, email, origin_channel, privacy_accepted_at):
    '''Devuelve (contacto, reutilizado). Llamar dentro de una transaccion.'''
    contact = Contact.objects.select_for_update().filter(phone=phone).first()
    if contact is None:
        contact = Contact(full_name=full_name, phone=phone, email=email,
                          origin_channel=origin_channel, privacy_accepted_at=privacy_accepted_at)
        contact.full_clean()
        try:
            with transaction.atomic():
                contact.save()
            return contact, False
        except IntegrityError:
            # Otro registro simultaneo creo el mismo telefono: se reutiliza.
            contact = Contact.objects.select_for_update().get(phone=phone)
    if contact.privacy_accepted_at is None and privacy_accepted_at is not None:
        # Completar el consentimiento no cambia los datos del contacto.
        contact.privacy_accepted_at = privacy_accepted_at
        contact.save(update_fields=['privacy_accepted_at'])
    return contact, True


def open_manual_opportunity(*, registered_by, property_obj, full_name, phone, email='',
                            privacy_accepted=False, assigned_agent=None):
    '''HU-27: devuelve (oportunidad, contacto_reutilizado).'''
    if not is_internal_user(registered_by):
        raise PermissionDenied('Solo los usuarios internos abren oportunidades.')

    errors = {}
    full_name = (full_name or '').strip()
    if not full_name:
        errors['full_name'] = 'Indique el nombre del interesado.'
    try:
        phone = normalize_phone(phone)
    except ValidationError as error:
        errors['phone'] = error.messages
    if not privacy_accepted:
        errors['privacy_accepted'] = (
            'Confirme que el interesado aceptó la política de privacidad (LOPDP).'
        )
    if property_obj.status not in OPENABLE_PROPERTY_STATUSES:
        errors['property'] = 'Solo se abren oportunidades sobre propiedades disponibles.'
    if errors:
        raise ValidationError(errors)
    agent = resolve_assigned_agent(registered_by, assigned_agent)

    now = timezone.now()
    with transaction.atomic():
        contact, reused = get_or_create_contact(
            phone=phone, full_name=full_name, email=(email or '').strip(),
            origin_channel=OriginChannel.MANUAL, privacy_accepted_at=now,
        )
        existing = Opportunity.objects.active().filter(contact=contact, property=property_obj).first()
        if existing:
            raise OpportunityConflict(existing)
        try:
            with transaction.atomic():
                opportunity = Opportunity.objects.create(
                    contact=contact, property=property_obj, assigned_agent=agent,
                    origin_channel=OriginChannel.MANUAL, last_activity_at=now,
                )
        except IntegrityError:
            # La restriccion de la BD gano una carrera con otra apertura simultanea.
            raise OpportunityConflict(
                Opportunity.objects.active().filter(contact=contact, property=property_obj).first()
            )
        OpportunityStatusHistory.objects.create(
            opportunity=opportunity, previous_status='', new_status=opportunity.status,
            changed_by=registered_by, reason='Apertura manual (HU-27).',
        )
    return opportunity, reused
