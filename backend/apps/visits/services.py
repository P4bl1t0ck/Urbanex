from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, time, timedelta

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from apps.opportunities.services import assignable_agents
from .models import ECUADOR_TZ, AgentAvailability, AvailabilityException, Visit

'''
Servicios de agendamiento (RF-09).

resolve_target_agent(): a nombre de quien se crea una franja o excepcion (HU-22, RF-09):
- el asesor, solo a su nombre (si pide otro asesor: 403);
- el admin elige un asesor activo (si falta o no es valido: 400).

free_slots(): base comun de HU-18 (franjas libres para el cliente) y de HU-19 (lote 3: validar
que la franja pedida sigue libre dentro de la transaccion). Aplica las reglas semanales y las
excepciones (HU-22), y resta las visitas programadas y la antelacion minima (HU-18).
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
