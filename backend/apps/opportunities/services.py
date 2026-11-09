from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.users.models import Property
from .models import (
    Contact,
    OriginChannel,
    Opportunity,
    OpportunityInteraction,
    OpportunityStatusHistory,
)
from .validators import normalize_phone

'''
Apertura de oportunidades (RF-05). open_manual_opportunity() es la unica via de HU-27 (I-07).
get_or_create_contact() la reutilizan HU-19 (apps.visits) y HU-16 (register_web_interest), con
el canal CATALOGO_WEB. change_status() escribe el historial de cada cambio de estado (RF-06).
agent_whatsapp_number() da el numero del asesor para el enlace wa.me de HU-15 (RF-02).

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


def get_or_create_contact(*, phone, full_name, email, origin_channel, privacy_accepted_at,
                          email_opt_in=False, refresh_privacy=False):
    '''
    Devuelve (contacto, reutilizado). Llamar dentro de una transaccion.
    email_opt_in solo se guarda en un contacto nuevo: el existente no cambia (DS-28, DS-39).
    refresh_privacy=True (HU-16, DS-50): una nueva aceptacion de la politica de privacidad
    reemplaza la fecha y hora guardadas; el nombre, el correo y el opt-in siguen sin cambios.
    '''
    contact = Contact.objects.select_for_update().filter(phone=phone).first()
    if contact is None:
        contact = Contact(full_name=full_name, phone=phone, email=email,
                          origin_channel=origin_channel, privacy_accepted_at=privacy_accepted_at,
                          email_opt_in=bool(email and email_opt_in))
        contact.full_clean()
        try:
            with transaction.atomic():
                contact.save()
            return contact, False
        except IntegrityError:
            # Otro registro simultaneo creo el mismo telefono: se reutiliza.
            contact = Contact.objects.select_for_update().get(phone=phone)
    if privacy_accepted_at is not None and (refresh_privacy or contact.privacy_accepted_at is None):
        # Completar o renovar el consentimiento no cambia los datos del contacto.
        contact.privacy_accepted_at = privacy_accepted_at
        contact.save(update_fields=['privacy_accepted_at'])
    return contact, True


def change_status(opportunity, new_status, *, changed_by, reason):
    '''
    Cambia el estado y deja la fila del historial (RF-06). Llamar dentro de una transaccion con
    la oportunidad bloqueada. changed_by=None: cambio del cliente desde el portal (DS-39).
    '''
    previous = opportunity.status
    now = timezone.now()
    opportunity.status = new_status
    opportunity.last_activity_at = now
    opportunity.save(update_fields=['status', 'last_activity_at'])
    OpportunityStatusHistory.objects.create(
        opportunity=opportunity, previous_status=previous, new_status=new_status,
        changed_by=changed_by, reason=reason,
    )
    return opportunity


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


# ---------------------------------------------------------------------------------------------
# Lote 4 (DS-50): HU-15 contacto por WhatsApp y HU-16 interes por formulario (P-07)
# ---------------------------------------------------------------------------------------------

WEB_FORM_OPENING_REASON = 'Interés desde el formulario web (HU-16).'
WEB_FORM_NOTE_PREFIX = 'Interés desde el formulario web: '
WEB_FORM_EMPTY_NOTE = 'Interés registrado desde el formulario web (sin mensaje)'
MAX_PUBLIC_MESSAGE_LENGTH = 1000


class InterestNotAccepted(Exception):
    '''La propiedad no tiene un asesor activo que atienda el interes (la vista responde 404).'''


def is_contactable_agent(agent):
    return agent is not None and agent.is_active and agent.role == 'asesor'


def agent_whatsapp_number(property_obj):
    '''
    HU-15 (RF-02, DS-50): numero del asesor captador para wa.me, solo digitos (593...), o None
    si la propiedad no esta Disponible, el asesor no esta activo o su telefono no es un celular
    de Ecuador valido con la regla de DS-28. Con None, el frontend oculta el boton.
    '''
    if property_obj.status not in OPENABLE_PROPERTY_STATUSES:
        return None
    agent = property_obj.agent
    if not is_contactable_agent(agent):
        return None
    try:
        return normalize_phone(agent.phone).lstrip('+')
    except ValidationError:
        return None


def validate_web_interest(*, full_name, phone, email, email_opt_in, message, privacy_accepted):
    '''Valida y normaliza el formulario de HU-16. Devuelve (nombre, celular, correo, mensaje).'''
    errors = {}
    full_name = (full_name or '').strip()
    if not full_name:
        errors['full_name'] = 'Indica tu nombre.'
    elif len(full_name) > 150:
        errors['full_name'] = 'El nombre no puede superar 150 caracteres.'
    try:
        phone = normalize_phone(phone)
    except ValidationError as error:
        errors['phone'] = error.messages
    email = (email or '').strip()
    if email:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = 'Ingresa un correo válido.'
    elif email_opt_in:
        errors['email'] = 'Para recibir novedades por correo, indica tu correo.'
    message = (message or '').strip()
    if len(message) > MAX_PUBLIC_MESSAGE_LENGTH:
        errors['message'] = f'El mensaje no puede superar {MAX_PUBLIC_MESSAGE_LENGTH} caracteres.'
    if not privacy_accepted:
        errors['privacy_accepted'] = 'Debes aceptar la política de privacidad (LOPDP).'
    if errors:
        raise ValidationError(errors)
    return full_name, phone, email, message


def register_web_interest(*, property_obj, full_name, phone, email='', email_opt_in=False,
                          message='', privacy_accepted=False):
    '''
    HU-16 (RF-03, DS-50): interes del visitante sin cuenta desde la ficha publica.
    Devuelve (oportunidad, creada).

    - La propiedad debe estar Disponible (la vista responde 404 si no lo esta) y tener un
      asesor captador activo; si no, InterestNotAccepted.
    - Contacto por telefono, canal CATALOGO_WEB: uno existente no cambia sus datos, pero la
      nueva aceptacion de la politica de privacidad reemplaza la fecha y hora (DS-50).
    - Oportunidad: la activa del contacto sobre el inmueble (conserva su estado y su asesor), o
      una nueva en CONTACTO_INICIAL con el asesor captador. Nunca se duplica (RF-03).
    - Siempre deja una interaccion SISTEMA sin autor con el mensaje, o el texto por defecto si
      vino vacio, y actualiza la ultima actividad de la oportunidad.
    '''
    full_name, phone, email, message = validate_web_interest(
        full_name=full_name, phone=phone, email=email, email_opt_in=email_opt_in,
        message=message, privacy_accepted=privacy_accepted,
    )
    agent = property_obj.agent
    if property_obj.status not in OPENABLE_PROPERTY_STATUSES or not is_contactable_agent(agent):
        raise InterestNotAccepted()

    now = timezone.now()
    with transaction.atomic():
        contact, _ = get_or_create_contact(
            phone=phone, full_name=full_name, email=email,
            origin_channel=OriginChannel.CATALOGO_WEB, privacy_accepted_at=now,
            email_opt_in=email_opt_in, refresh_privacy=True,
        )
        created = False
        opportunity = (Opportunity.objects.select_for_update().active()
                       .filter(contact=contact, property=property_obj).first())
        if opportunity is None:
            try:
                with transaction.atomic():
                    opportunity = Opportunity.objects.create(
                        contact=contact, property=property_obj, assigned_agent=agent,
                        origin_channel=OriginChannel.CATALOGO_WEB, last_activity_at=now,
                    )
            except IntegrityError:
                # Otra solicitud simultanea abrio la misma oportunidad: se reutiliza.
                opportunity = (Opportunity.objects.select_for_update().active()
                               .get(contact=contact, property=property_obj))
            else:
                created = True
                OpportunityStatusHistory.objects.create(
                    opportunity=opportunity, previous_status='', new_status=opportunity.status,
                    changed_by=None, reason=WEB_FORM_OPENING_REASON,
                )

        interaction = OpportunityInteraction(
            opportunity=opportunity, author=None,
            interaction_type=OpportunityInteraction.Type.SISTEMA,
            notes=f'{WEB_FORM_NOTE_PREFIX}{message}' if message else WEB_FORM_EMPTY_NOTE,
        )
        interaction.full_clean()
        interaction.save()
        if not created:
            opportunity.last_activity_at = now
            opportunity.save(update_fields=['last_activity_at'])
    return opportunity, created
