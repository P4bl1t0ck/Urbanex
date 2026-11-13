import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.opportunities.models import (
    SYSTEM_REASON_CLIENT_PORTAL,
    OpportunityStatusHistory,
    OriginChannel,
    Opportunity,
)
from apps.opportunities.services import assignable_agents, change_status, get_or_create_contact
from apps.opportunities.validators import normalize_phone
from .models import ECUADOR_TZ, AgentAvailability, AvailabilityException, Visit

logger = logging.getLogger(__name__)
User = get_user_model()

'''
Servicios de agendamiento (RF-09).

resolve_target_agent(): a nombre de quien se crea una franja o excepcion (HU-22, RF-09):
- el asesor, solo a su nombre (si pide otro asesor: 403);
- el admin elige un asesor activo (si falta o no es valido: 400).

free_slots(): base comun de HU-18 (franjas libres para el cliente) y de HU-19 (validar que la
franja pedida sigue libre dentro de la transaccion). Aplica las reglas semanales y las
excepciones (HU-22), y resta las visitas programadas y la antelacion minima (HU-18).

Lote 3 (DS-39):
- request_visit(): HU-19, solicitud del cliente sin cuenta desde P-07.
- send_visit_notifications(): HU-20, correos despues del commit.
- public_visit_by_token(): HU-20, P-08 de solo lectura hasta la hora de inicio.
- record_outcome(): HU-25, resultado de la visita en la agenda I-08.
'''


def default_lead_time():
    return timedelta(minutes=settings.VISIT_MIN_LEAD_TIME_MINUTES)


def resolve_target_agent(user, agent_id):
    if user.role == 'admin':
        if agent_id in (None, ''):
            raise ValidationError({'agent': 'Elija el asesor.'})
        if not str(agent_id).isdigit():
            raise ValidationError({'agent': 'Debe ser un id numérico.'})
        agent = assignable_agents().filter(pk=agent_id).first()
        if agent is None:
            raise ValidationError({'agent': 'Debe ser un asesor activo.'})
        return agent
    if agent_id not in (None, '') and str(agent_id) != str(user.pk):
        raise PermissionDenied('Solo el administrador gestiona la disponibilidad de otro asesor.')
    return user


@dataclass(frozen=True)
class Slot:
    start: datetime  # Con zona horaria de Ecuador
    end: datetime


def local_datetime(day, moment):
    # Ecuador no tiene horario de verano: combinar fecha y hora de pared es exacto.
    return datetime.combine(day, moment, tzinfo=ECUADOR_TZ)


def free_slots(agent, date_from, date_to, *, now=None, lead_time=None):
    '''
    Franjas libres del asesor entre date_from y date_to (fechas de Ecuador, ambas incluidas).
    Cada regla semanal se parte en visitas de slot_duration_minutes desde su hora de inicio;
    lo que sobra al final de la regla no forma una franja. Se excluyen:
    - las fechas con excepcion de dia completo;
    - las franjas que se cruzan con una excepcion por horas;
    - las franjas que se cruzan con una visita PROGRAMADA del asesor (en cualquier propiedad);
    - las franjas que empiezan antes de now + lead_time (por defecto, la antelacion de settings).
    Se calcula en cada llamada, sin cache: refleja las visitas en tiempo real (HU-18).
    '''
    now = now or timezone.now()
    earliest_start = now + (default_lead_time() if lead_time is None else lead_time)
    rules_by_weekday = defaultdict(list)
    for rule in AgentAvailability.objects.filter(agent=agent):
        rules_by_weekday[rule.day_of_week].append(rule)

    blocked_days = set()
    blocked_ranges = defaultdict(list)
    exceptions = AvailabilityException.objects.filter(
        agent=agent, exception_date__gte=date_from, exception_date__lte=date_to,
    )
    for exception in exceptions:
        if exception.is_full_day:
            blocked_days.add(exception.exception_date)
        else:
            blocked_ranges[exception.exception_date].append((
                local_datetime(exception.exception_date, exception.start_time),
                local_datetime(exception.exception_date, exception.end_time),
            ))

    busy_visits = list(Visit.objects.filter(
        agent=agent,
        status=Visit.Status.PROGRAMADA,
        scheduled_start__lt=local_datetime(date_to + timedelta(days=1), time.min),
        scheduled_end__gt=local_datetime(date_from, time.min),
    ).values_list('scheduled_start', 'scheduled_end'))

    slots = []
    day = date_from
    while day <= date_to:
        if day not in blocked_days:
            for rule in rules_by_weekday[day.weekday()]:
                step = timedelta(minutes=rule.slot_duration_minutes)
                start = local_datetime(day, rule.start_time)
                limit = local_datetime(day, rule.end_time)
                while start + step <= limit:
                    end = start + step
                    crosses_exception = any(
                        start < blocked_end and blocked_start < end
                        for blocked_start, blocked_end in blocked_ranges[day]
                    )
                    crosses_visit = any(
                        start < visit_end and visit_start < end
                        for visit_start, visit_end in busy_visits
                    )
                    if start >= earliest_start and not crosses_exception and not crosses_visit:
                        slots.append(Slot(start=start, end=end))
                    start = end
        day += timedelta(days=1)
    return sorted(slots, key=lambda slot: slot.start)


# ---------------------------------------------------------------------------------------------
# HU-19: solicitud de visita del cliente sin cuenta (P-07, RF-04, DS-39)
# ---------------------------------------------------------------------------------------------

SCHEDULABLE_PROPERTY_STATUSES = ('disponible',)


class SlotUnavailable(Exception):
    '''La franja pedida no es (o ya no es) una de las que free_slots() ofrece.'''


class VisitAlreadyScheduled(Exception):
    '''La oportunidad del contacto sobre este inmueble ya tiene una visita Programada (409).'''


def is_schedulable_agent(agent):
    return agent is not None and agent.is_active and agent.role == 'asesor'


def validate_request_data(*, full_name, phone, email, email_opt_in, privacy_accepted):
    '''Valida y normaliza los datos del formulario de P-07. Devuelve (nombre, celular, correo).'''
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
        errors['email'] = 'Para recibir la confirmación por correo, indica tu correo.'
    if not privacy_accepted:
        errors['privacy_accepted'] = 'Debes aceptar la política de privacidad (LOPDP).'
    if errors:
        raise ValidationError(errors)
    return full_name, phone, email


def request_visit(*, property_obj, start, full_name, phone, email='', email_opt_in=False,
                  privacy_accepted=False):
    '''
    HU-19. Registra la visita del cliente en la franja elegida y devuelve la visita.

    - La propiedad debe estar Disponible (la vista responde 404 si no lo esta).
    - La franja debe ser exactamente una de free_slots() del asesor de la propiedad, recalculada
      dentro de la transaccion con el asesor bloqueado (DS-39 punto 3). Si no: SlotUnavailable.
    - Contacto: get_or_create_contact() con canal CATALOGO_WEB; uno existente no se modifica.
    - Oportunidad: la activa del contacto sobre el inmueble, o una nueva con el asesor de la
      propiedad. Si ya tiene una visita Programada: VisitAlreadyScheduled (409).
    - La visita la atiende el asesor de la propiedad aunque la oportunidad tenga otro asesor
      asignado; P-08 y la agenda muestran a los dos (DS-39).
    - CONTACTO_INICIAL -> VISITA_PROGRAMADA; si ya esta en otro estado, no cambia.
    - Los correos (HU-20) salen despues del commit: un fallo del correo no revierte la visita.
    '''
    full_name, phone, email = validate_request_data(
        full_name=full_name, phone=phone, email=email, email_opt_in=email_opt_in,
        privacy_accepted=privacy_accepted,
    )
    if timezone.is_naive(start):
        start = start.replace(tzinfo=ECUADOR_TZ)
    agent = property_obj.agent
    if property_obj.status not in SCHEDULABLE_PROPERTY_STATUSES or not is_schedulable_agent(agent):
        raise SlotUnavailable()

    now = timezone.now()
    with transaction.atomic():
        # Serializa las solicitudes sobre el mismo asesor (PostgreSQL); SQLite ya serializa las
        # escrituras. La restriccion de exclusion en PostgreSQL queda para DT-143.
        User.objects.select_for_update().filter(pk=agent.pk).first()
        day = start.astimezone(ECUADOR_TZ).date()
        slot = next((s for s in free_slots(agent, day, day, now=now) if s.start == start), None)
        if slot is None:
            raise SlotUnavailable()

        contact, _ = get_or_create_contact(
            phone=phone, full_name=full_name, email=email,
            origin_channel=OriginChannel.CATALOGO_WEB, privacy_accepted_at=now,
            email_opt_in=email_opt_in,
        )
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
                OpportunityStatusHistory.objects.create(
                    opportunity=opportunity, previous_status='', new_status=opportunity.status,
                    changed_by=None, reason=SYSTEM_REASON_CLIENT_PORTAL,
                )
        if opportunity.visits.filter(status=Visit.Status.PROGRAMADA).exists():
            raise VisitAlreadyScheduled()

        visit = Visit(
            opportunity=opportunity, property=property_obj, agent=agent,
            scheduled_start=slot.start, scheduled_end=slot.end,
            confirmation_email=email if email_opt_in else '',
        )
        visit.full_clean()
        visit.save()
        if opportunity.status == Opportunity.Status.CONTACTO_INICIAL:
            change_status(opportunity, Opportunity.Status.VISITA_PROGRAMADA, changed_by=None,
                          reason=SYSTEM_REASON_CLIENT_PORTAL)
        visit_id = visit.pk
        transaction.on_commit(lambda: send_visit_notifications(visit_id))
    return visit


# ---------------------------------------------------------------------------------------------
# HU-20: confirmacion por correo y P-08 (DS-39)
# ---------------------------------------------------------------------------------------------

def display_name(user):
    return user.get_full_name() or user.username


def format_local(moment):
    return moment.astimezone(ECUADOR_TZ).strftime('%d/%m/%Y %H:%M')


def visit_link(visit):
    return f"{settings.FRONTEND_BASE_URL.rstrip('/')}/visits/{visit.cancellation_token}"


def notification_agents(visit):
    '''Asesor de la visita y, si es otro, el asesor de la oportunidad (DS-39).'''
    agents = [visit.agent]
    followup = visit.opportunity.assigned_agent
    if followup is not None and followup.pk != visit.agent_id:
        agents.append(followup)
    return agents


def send_visit_notifications(visit_id):
    '''
    Correos de HU-20, llamados con transaction.on_commit. Cada envio falla por separado y solo
    queda en el log: la visita ya esta registrada y el asesor puede confirmar por WhatsApp.
    - Al cliente: solo si dio correo y marco la casilla (confirmation_email), con el enlace a P-08.
    - Al asesor de la visita (y al de la oportunidad si es otro): siempre que tenga correo.
    '''
    visit = (Visit.objects.select_related('property', 'agent', 'opportunity__contact',
                                          'opportunity__assigned_agent')
             .filter(pk=visit_id).first())
    if visit is None:
        return
    when = format_local(visit.scheduled_start)
    contact = visit.opportunity.contact

    if visit.confirmation_email:
        body = (
            f'Hola {contact.full_name}:\n\n'
            f'Tu visita a "{visit.property.title}" ({visit.property.location}) quedó programada '
            f'para el {when} (hora de Ecuador).\n\n'
            f'Puedes ver los datos de tu visita y de tu asesor aquí:\n{visit_link(visit)}\n\n'
            'En ese mismo enlace puedes cancelarla hasta 1 hora antes. Para cambiar la hora, '
            'comunícate con tu asesor.\n\n'
            'Urbanex'
        )
        try:
            send_mail('Urbanex: tu visita quedó programada', body,
                      settings.DEFAULT_FROM_EMAIL, [visit.confirmation_email])
        except Exception:  # pylint: disable=broad-except
            logger.exception('No se pudo enviar la confirmación de la visita #%s.', visit.pk)

    channel = ('Se envió la confirmación por correo al cliente.' if visit.confirmation_email
               else 'El cliente no pidió confirmación por correo: confírmala por WhatsApp.')
    for agent in notification_agents(visit):
        if not agent.email:
            continue
        role = ('Atiendes esta visita.' if agent.pk == visit.agent_id
                else 'Eres el asesor de la oportunidad; la visita la atiende '
                     f'{display_name(visit.agent)}.')
        body = (
            f'Nueva visita solicitada desde el portal.\n\n'
            f'Propiedad: {visit.property.title} ({visit.property.location})\n'
            f'Fecha y hora: {when} (hora de Ecuador)\n'
            f'Cliente: {contact.full_name} · {contact.phone}\n\n'
            f'{role}\n{channel}\n\n'
            'Revisa tu agenda en Urbanex.'
        )
        try:
            send_mail('Urbanex: nueva visita programada', body,
                      settings.DEFAULT_FROM_EMAIL, [agent.email])
        except Exception:  # pylint: disable=broad-except
            logger.exception('No se pudo avisar al asesor %s de la visita #%s.',
                             agent.pk, visit.pk)


def public_visit_by_token(token, *, now=None):
    '''P-08: la visita del enlace, solo hasta su hora de inicio. Si no: None (la vista da 404).'''
    now = now or timezone.now()
    return (Visit.objects
            .select_related('property', 'agent', 'opportunity__assigned_agent')
            .filter(cancellation_token=token, scheduled_start__gt=now)
            .first())


# ---------------------------------------------------------------------------------------------
# Lotes 5 y 6 (DS-52): HU-21 cancelar una visita (P-08 para el cliente, I-08 para el asesor)
# ---------------------------------------------------------------------------------------------

MAX_CANCEL_REASON_LENGTH = 1000


def client_cancel_notice():
    '''El cliente cancela hasta 1 hora antes del inicio (decision de Pablo, 2026-11-13, DS-52).'''
    return timedelta(minutes=getattr(settings, 'VISIT_CLIENT_CANCEL_NOTICE_MINUTES', 60))


def client_cancel_deadline(visit):
    return visit.scheduled_start - client_cancel_notice()


def client_can_cancel(visit, *, now=None):
    now = now or timezone.now()
    return visit.status == Visit.Status.PROGRAMADA and now <= client_cancel_deadline(visit)


class VisitNotCancellable(Exception):
    '''La visita ya no esta Programada (cancelada o con resultado): 409.'''


def can_manage_visit(user, visit):
    '''HU-21 y HU-23: el asesor de la visita o el admin (igual que HU-25).'''
    return getattr(user, 'role', None) == 'admin' or visit.agent_id == user.pk


def record_visit_event(opportunity, visit, notes):
    '''Entrada SISTEMA en el historial de la oportunidad (HU-21, HU-23; se ve en HU-33).'''
    from apps.opportunities.models import OpportunityInteraction

    interaction = OpportunityInteraction(
        opportunity=opportunity, author=None, visit=visit, notes=notes,
        interaction_type=OpportunityInteraction.Type.SISTEMA,
    )
    interaction.full_clean()
    interaction.save()
    opportunity.last_activity_at = interaction.created_at
    opportunity.save(update_fields=['last_activity_at'])


def cancel_visit(*, visit_id, user=None, reason='', now=None):
    '''
    HU-21 (RF-04, DS-52). Cancela una visita Programada y la devuelve.
    - user=None: el cliente desde su enlace (P-08), hasta 1 hora antes del inicio.
    - user: el asesor de la visita o el admin desde la agenda (I-08), hasta la hora de inicio,
      con motivo obligatorio.
    - La franja queda libre (free_slots() solo resta las PROGRAMADAS).
    - Si era la unica visita activa y la oportunidad esta en Visita programada, vuelve a
      Contacto inicial (RF-04, DS-39).
    - Deja una entrada SISTEMA en el historial de la oportunidad.
    - Avisos despues del commit: al asesor si cancela el cliente; al cliente (si dio correo)
      si cancela el asesor.
    VisitNotCancellable si ya no esta Programada (409).
    '''
    by_client = user is None
    reason = (reason or '').strip()
    if not by_client:
        if not reason:
            raise ValidationError({'reason': 'Escribe el motivo de la cancelación.'})
        if len(reason) > MAX_CANCEL_REASON_LENGTH:
            raise ValidationError({'reason': (
                f'El motivo no puede superar {MAX_CANCEL_REASON_LENGTH} caracteres.'
            )})

    now = now or timezone.now()
    with transaction.atomic():
        visit = (Visit.objects.select_for_update().select_related('opportunity', 'agent')
                 .get(pk=visit_id))
        if not by_client and not can_manage_visit(user, visit):
            raise PermissionDenied('Solo el asesor de la visita o el administrador '
                                   'la cancelan.')
        if visit.status != Visit.Status.PROGRAMADA:
            raise VisitNotCancellable()
        if by_client and now > client_cancel_deadline(visit):
            minutes = int(client_cancel_notice().total_seconds() // 60)
            raise ValidationError({'detail': (
                f'La visita solo se cancela por el enlace hasta {minutes} minutos antes. '
                'Comunícate con tu asesor.'
            )})
        if not by_client and now >= visit.scheduled_start:
            raise ValidationError({'detail': (
                'La visita ya empezó: registra su resultado en lugar de cancelarla.'
            )})

        when = format_local(visit.scheduled_start)
        if by_client:
            visit.outcome_notes = 'Cancelada por el cliente desde su enlace (HU-21).'
            event = f'El cliente canceló desde su enlace la visita del {when}.'
        else:
            visit.outcome_notes = f'Cancelada por {display_name(user)}: {reason}'
            event = f'{display_name(user)} canceló la visita del {when}. Motivo: {reason}'
        visit.status = Visit.Status.CANCELADA
        visit.outcome_recorded_at = now
        visit.outcome_recorded_by = user
        visit.save(update_fields=['status', 'outcome_notes', 'outcome_recorded_at',
                                  'outcome_recorded_by'])

        opportunity = Opportunity.objects.select_for_update().get(pk=visit.opportunity_id)
        record_visit_event(opportunity, visit, event)
        still_scheduled = opportunity.visits.filter(status=Visit.Status.PROGRAMADA).exists()
        if opportunity.status == Opportunity.Status.VISITA_PROGRAMADA and not still_scheduled:
            change_status(
                opportunity, Opportunity.Status.CONTACTO_INICIAL, changed_by=user,
                reason=(SYSTEM_REASON_CLIENT_PORTAL if by_client else
                        f'Visita #{visit.pk} cancelada: no quedan visitas activas (RF-04).'),
            )
        visit_pk = visit.pk
        transaction.on_commit(lambda: send_cancellation_notifications(visit_pk, by_client))
    return visit


def send_cancellation_notifications(visit_id, by_client):
    '''Correos de HU-21 (consola en desarrollo). Cada envio falla por separado y solo se loguea.'''
    visit = (Visit.objects.select_related('property', 'agent', 'opportunity__contact',
                                          'opportunity__assigned_agent')
             .filter(pk=visit_id).first())
    if visit is None:
        return
    when = format_local(visit.scheduled_start)
    contact = visit.opportunity.contact
    if by_client:
        recipients = [agent.email for agent in notification_agents(visit) if agent.email]
        subject = 'Urbanex: el cliente canceló una visita'
        body = (
            f'El cliente canceló su visita desde el enlace.\n\n'
            f'Propiedad: {visit.property.title} ({visit.property.location})\n'
            f'Fecha y hora: {when} (hora de Ecuador)\n'
            f'Cliente: {contact.full_name} · {contact.phone}\n\n'
            'La franja quedó libre en tu agenda.'
        )
    else:
        recipients = [visit.confirmation_email] if visit.confirmation_email else []
        subject = 'Urbanex: tu visita fue cancelada'
        body = (
            f'Hola {contact.full_name}:\n\n'
            f'Tu visita a "{visit.property.title}" ({visit.property.location}) del {when} '
            '(hora de Ecuador) fue cancelada por tu asesor.\n\n'
            'Si quieres agendar otra, comunícate con tu asesor o elige una nueva hora en la '
            'ficha de la propiedad.\n\nUrbanex'
        )
    for recipient in recipients:
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient])
        except Exception:  # pylint: disable=broad-except
            logger.exception('No se pudo avisar la cancelación de la visita #%s.', visit.pk)


# ---------------------------------------------------------------------------------------------
# HU-25: resultado de la visita (I-08, DS-39)
# ---------------------------------------------------------------------------------------------

OUTCOME_STATUSES = (Visit.Status.REALIZADA, Visit.Status.NO_ASISTIDA, Visit.Status.CANCELADA)
# Si la unica visita activa queda asi, la oportunidad vuelve a Contacto Inicial (DS-39 punto 1).
REVERTING_OUTCOMES = (Visit.Status.NO_ASISTIDA, Visit.Status.CANCELADA)


class OutcomeAlreadyRecorded(Exception):
    '''El resultado ya se registro: se registra una sola vez (409).'''


def can_record_outcome(user, visit):
    return getattr(user, 'role', None) == 'admin' or visit.agent_id == user.pk


def record_outcome(*, visit, user, outcome, notes, now=None):
    '''
    HU-25. Solo el asesor de la visita o el admin; solo despues de la hora de inicio; una sola
    vez; observacion obligatoria. No avanza la oportunidad a En Negociacion (HU-29).
    '''
    if not can_record_outcome(user, visit):
        raise PermissionDenied('Solo el asesor de la visita o el administrador registran el resultado.')
    errors = {}
    if outcome not in OUTCOME_STATUSES:
        errors['status'] = 'Elige Realizada, No asistida o Cancelada.'
    notes = (notes or '').strip()
    if not notes:
        errors['outcome_notes'] = 'Escribe la observación de la visita.'
    if errors:
        raise ValidationError(errors)

    now = now or timezone.now()
    with transaction.atomic():
        visit = Visit.objects.select_for_update().select_related('opportunity').get(pk=visit.pk)
        if visit.status != Visit.Status.PROGRAMADA or visit.outcome_recorded_at is not None:
            raise OutcomeAlreadyRecorded()
        if now < visit.scheduled_start:
            raise ValidationError({
                'status': 'El resultado se registra después de la hora de inicio de la visita.',
            })
        visit.status = outcome
        visit.outcome_notes = notes
        visit.outcome_recorded_at = now
        visit.outcome_recorded_by = user
        visit.save(update_fields=['status', 'outcome_notes', 'outcome_recorded_at',
                                  'outcome_recorded_by'])

        if outcome in REVERTING_OUTCOMES:
            opportunity = Opportunity.objects.select_for_update().get(pk=visit.opportunity_id)
            still_scheduled = opportunity.visits.filter(status=Visit.Status.PROGRAMADA).exists()
            if (opportunity.status == Opportunity.Status.VISITA_PROGRAMADA
                    and not still_scheduled):
                change_status(
                    opportunity, Opportunity.Status.CONTACTO_INICIAL, changed_by=user,
                    reason=(f'Visita #{visit.pk} {visit.get_status_display().lower()}: '
                            'no quedan visitas activas (RF-04).'),
                )
    return visit
