import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

'''
Agendamiento de visitas (PROC-04, RF-09, RF-04). Lote 2: HU-22 (disponibilidad, I-09),
HU-18 (franjas libres, P-07) y HU-24 (agenda, I-08). HU-19 (solicitar visita) llega en el lote 3.

Horas: TIME_ZONE sigue en UTC (DT-01). Las horas de la disponibilidad son horas de pared de
Ecuador (America/Guayaquil, sin horario de verano); se convierten de forma explicita al calcular
franjas, igual que el filtro de fechas de HU-34.

Reglas de RF-09 y del Anexo 2 (HU-22), con las precisiones de Pablo (2026-11-06):
- Franjas por dia de la semana (0 = lunes ... 6 = domingo); no se admiten franjas de menos de
  30 minutos ni dos franjas que se crucen el mismo dia para el mismo asesor.
- Duracion de cada visita: 60 minutos por defecto, minimo 30.
- Las excepciones bloquean una fecha: sin horas, el dia completo; con horas, solo ese rango.
  No se registran excepciones con fecha pasada.
'''

ECUADOR_TZ = ZoneInfo('America/Guayaquil')
MIN_SLOT_MINUTES = 30
DEFAULT_SLOT_MINUTES = 60


def ecuador_today():
    return timezone.now().astimezone(ECUADOR_TZ).date()


def minutes_between(start, end):
    '''Minutos entre dos horas del mismo dia (time - time no existe en Python).'''
    day = datetime(2000, 1, 1)
    return int((datetime.combine(day, end) - datetime.combine(day, start)).total_seconds() // 60)


class Weekday(models.IntegerChoices):
    LUNES = 0, 'Lunes'
    MARTES = 1, 'Martes'
    MIERCOLES = 2, 'Miércoles'
    JUEVES = 3, 'Jueves'
    VIERNES = 4, 'Viernes'
    SABADO = 5, 'Sábado'
    DOMINGO = 6, 'Domingo'


class AgentAvailability(models.Model):
    '''Regla semanal de disponibilidad de un asesor (HU-22).'''
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Es configuracion del asesor, no historial
        related_name='availability_rules',
    )
    day_of_week = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.PositiveSmallIntegerField(
        default=DEFAULT_SLOT_MINUTES,
        validators=[MinValueValidator(MIN_SLOT_MINUTES), MaxValueValidator(24 * 60)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'disponibilidad semanal'
        verbose_name_plural = 'disponibilidad semanal'
        ordering = ['agent_id', 'day_of_week', 'start_time']
        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F('start_time')),
                name='availability_end_after_start',
            ),
            models.CheckConstraint(
                condition=Q(day_of_week__gte=0, day_of_week__lte=6),
                name='availability_valid_weekday',
            ),
            models.CheckConstraint(
                condition=Q(slot_duration_minutes__gte=MIN_SLOT_MINUTES),
                name='availability_min_slot_duration',
            ),
        ]
        indexes = [
            models.Index(fields=['agent', 'day_of_week'], name='avail_agent_day_idx'),
        ]

    def __str__(self):
        return (f'{self.agent} · {self.get_day_of_week_display()} '
                f'{self.start_time:%H:%M}-{self.end_time:%H:%M}')

    def clean(self):
        errors = {}
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                errors['end_time'] = 'La hora de fin debe ser posterior a la de inicio.'
            else:
                length = minutes_between(self.start_time, self.end_time)
                if length < MIN_SLOT_MINUTES:
                    errors['end_time'] = (
                        f'La franja debe durar al menos {MIN_SLOT_MINUTES} minutos.'
                    )
                elif self.slot_duration_minutes and self.slot_duration_minutes > length:
                    errors['slot_duration_minutes'] = (
                        'La duración de la visita no cabe en la franja.'
                    )
        if errors:
            raise ValidationError(errors)

        if self.agent_id is not None and self.day_of_week is not None:
            # Dos franjas se cruzan si una empieza antes de que termine la otra.
            overlapping = AgentAvailability.objects.filter(
                agent_id=self.agent_id,
                day_of_week=self.day_of_week,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError({
                    'start_time': 'La franja se cruza con otra del mismo día.',
                })


class AvailabilityException(models.Model):
    '''Bloqueo puntual de una fecha (HU-22): sin horas, el dia completo; con horas, ese rango.'''
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availability_exceptions',
    )
    exception_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'excepción de disponibilidad'
        verbose_name_plural = 'excepciones de disponibilidad'
        ordering = ['agent_id', 'exception_date', 'start_time']
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(start_time__isnull=True, end_time__isnull=True)
                    | Q(start_time__isnull=False, end_time__isnull=False,
                        end_time__gt=F('start_time'))
                ),
                name='exception_full_day_or_valid_range',
            ),
        ]
        indexes = [
            models.Index(fields=['agent', 'exception_date'], name='exc_agent_date_idx'),
        ]

    def __str__(self):
        if self.is_full_day:
            return f'{self.agent} · {self.exception_date} (día completo)'
        return f'{self.agent} · {self.exception_date} {self.start_time:%H:%M}-{self.end_time:%H:%M}'

    @property
    def is_full_day(self):
        return self.start_time is None and self.end_time is None

    def clean(self):
        errors = {}
        if (self.start_time is None) != (self.end_time is None):
            errors['end_time'] = (
                'Indique la hora de inicio y la de fin, o deje ambas vacías para el día completo.'
            )
        elif self.start_time is not None and self.end_time <= self.start_time:
            errors['end_time'] = 'La hora de fin debe ser posterior a la de inicio.'
        if self.exception_date is not None and self.exception_date < ecuador_today():
            errors['exception_date'] = 'No se registran excepciones en fechas pasadas.'
        if errors:
            raise ValidationError(errors)


class Visit(models.Model):
    '''
    Visita presencial (RF-04; Contexto Maestro §7). Una visita PROGRAMADA ocupa la agenda de su
    asesor: free_slots() ya no ofrece esa franja (HU-18) y la agenda la muestra (HU-24).

    En el lote 2 las visitas solo se crean desde el admin de Django o con setup_visits_demo; la
    solicitud del cliente (HU-19, lote 3) las creara con free_slots() dentro de una transaccion
    y llevara la oportunidad a Visita Programada. Crear una visita aqui NO cambia el estado de
    la oportunidad.

    agent es el asesor de la visita y no cambia si despues se reasigna la propiedad
    (Contexto Maestro, RF-08: las visitas confirmadas no se transfieren).
    '''

    class Status(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', 'Programada'
        REALIZADA = 'REALIZADA', 'Realizada'
        NO_ASISTIDA = 'NO_ASISTIDA', 'No asistida'
        CANCELADA = 'CANCELADA', 'Cancelada'

    opportunity = models.ForeignKey(
        'opportunities.Opportunity',
        on_delete=models.PROTECT,  # La visita es parte del seguimiento comercial
        related_name='visits',
    )
    property = models.ForeignKey(
        'users.Property',
        on_delete=models.PROTECT,
        related_name='visits',
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='visits',
    )
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PROGRAMADA)
    # Enlace de cancelacion del cliente (HU-20 y HU-21): nunca se expone en endpoints publicos.
    cancellation_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    outcome_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'visita'
        verbose_name_plural = 'visitas'
        ordering = ['scheduled_start']
        constraints = [
            models.CheckConstraint(
                condition=Q(scheduled_end__gt=F('scheduled_start')),
                name='visit_end_after_start',
            ),
        ]
        indexes = [
            models.Index(fields=['agent', 'status', 'scheduled_start'], name='visit_agent_status_idx'),
            models.Index(fields=['scheduled_start'], name='visit_start_idx'),
        ]

    def __str__(self):
        start = timezone.localtime(self.scheduled_start, ECUADOR_TZ) if self.scheduled_start else None
        return f'Visita #{self.pk} · {self.property} · {start:%Y-%m-%d %H:%M}' if start else 'Visita'

    def clean(self):
        errors = {}
        if self.scheduled_start and self.scheduled_end and self.scheduled_end <= self.scheduled_start:
            errors['scheduled_end'] = 'La hora de fin debe ser posterior a la de inicio.'
        if self.opportunity_id and self.property_id and self.opportunity.property_id != self.property_id:
            errors['property'] = 'La propiedad debe ser la misma de la oportunidad.'
        if self.agent_id and getattr(self.agent, 'role', None) != 'asesor':
            errors['agent'] = 'La visita la atiende un asesor.'
        if self._state.adding and self.opportunity_id and not self.opportunity.is_active:
            errors['opportunity'] = 'No se programan visitas en una oportunidad cerrada o perdida.'
        if errors:
            raise ValidationError(errors)

        if self.status == self.Status.PROGRAMADA and self.agent_id:
            # La agenda del asesor no admite dos visitas programadas que se crucen (RF-09).
            # En PostgreSQL falta la restriccion de exclusion para las carreras (DT-143, HU-19).
            overlapping = Visit.objects.filter(
                agent_id=self.agent_id,
                status=self.Status.PROGRAMADA,
                scheduled_start__lt=self.scheduled_end,
                scheduled_end__gt=self.scheduled_start,
            ).exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError({
                    'scheduled_start': 'El asesor ya tiene una visita programada en ese horario.',
                })
