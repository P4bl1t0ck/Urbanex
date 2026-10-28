import builtins
import uuid
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone

from .engine import EngineError, Sample, compute, validate_params
from .services import find_candidates, subject_blocker

'''
Avaluo comercial (RF-11, HU-08). Modelo de apps.appraisals del Contexto Maestro §7,
ampliado con status y approved_at (decision del equipo para el flujo HITL).

Ciclo de vida: BORRADOR -> APROBADO.
- En BORRADOR solo cambian los campos de calibracion (calibrated_value, final_justification).
- approve() fija las diferencias, status y approved_at en un solo paso.
- Un avaluo APROBADO jamas se modifica ni se elimina; recalibrar = crear un avaluo nuevo
  (historial acumulativo, HU-50).

El motor de calculo (HU-04, HU-06) es el de DS-21 (D-04 resuelta provisionalmente): con 3 a 5
comparables confirmados el avaluo nace con valor sugerido; sin ellos, como registro manual de
confianza baja (degradacion de RF-11 / RNF-07, DS-02). HU-07 (borrador de IA) sigue pendiente.
'''

# Campos que se pueden tocar mientras el avaluo esta en BORRADOR. status, approved_at y
# las diferencias solo los cambia approve().
MUTABLE_FIELDS = {
    'calibrated_value',
    'final_justification',
    'status',
    'approved_at',
    'difference_amount',
    'difference_percentage',
}

CENTS = Decimal('0.01')


def generate_folio():
    return f'AV-{timezone.localdate():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}'


class AppraisalQuerySet(models.QuerySet):
    def delete(self):
        raise ValidationError('Los avalúos no se pueden eliminar.')

    def update(self, **kwargs):
        forbidden = set(kwargs) - MUTABLE_FIELDS
        if forbidden:
            raise ValidationError(
                f'Campos inmutables en el avalúo: {", ".join(sorted(forbidden))}.'
            )
        if self.filter(status=Appraisal.Status.APROBADO).exists():
            raise ValidationError('Un avalúo aprobado no se puede modificar.')
        return super().update(**kwargs)

    def approved(self):
        return self.filter(status=Appraisal.Status.APROBADO)


class EngineParameters(models.Model):
    '''
    Theta del motor (DS-21, capa 3). Cada version es inmutable: cambiar theta = crear una
    version nueva desde el admin. Solo una version esta activa; cada avaluo calculado guarda
    la version que uso (HU-08).
    '''
    version = models.PositiveIntegerField(unique=True, editable=False)
    parameters = models.JSONField()
    sources = models.JSONField(default=dict, blank=True)
    note = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,  # La version 1 la crea la migracion de datos.
        blank=True,
        related_name='engine_parameters',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-version']
        constraints = [
            models.UniqueConstraint(
                fields=['is_active'],
                condition=Q(is_active=True),
                name='engine_parameters_single_active',
            ),
        ]

    def __str__(self):
        return f'theta v{self.version}{" (activa)" if self.is_active else ""}'

    def clean(self):
        try:
            validate_params(self.parameters)
        except ValueError as error:
            raise ValidationError({'parameters': str(error)})

    def save(self, *args, **kwargs):
        if not self._state.adding:
            stored = EngineParameters.objects.filter(pk=self.pk).values().first()
            changed = {
                field.attname for field in self._meta.concrete_fields
                if stored and getattr(self, field.attname) != stored[field.attname]
            }
            if changed - {'is_active'}:
                raise ValidationError('Una versión de parámetros no se modifica: cree una nueva.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Las versiones de parámetros no se pueden eliminar.')

    @classmethod
    def active(cls):
        return cls.objects.filter(is_active=True).first()

    @classmethod
    def create_version(cls, *, parameters, created_by, sources=None, note='', activate=True):
        with transaction.atomic():
            last = cls.objects.select_for_update().order_by('-version').first()
            version = cls(
                version=(last.version if last else 0) + 1,
                parameters=parameters,
                sources=sources or {},
                note=note,
                created_by=created_by,
            )
            version.full_clean(exclude=['version'])
            version.save()
            if activate:
                version.activate()
        return version

    def activate(self):
        with transaction.atomic():
            EngineParameters.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
            self.is_active = True
            self.save(update_fields=['is_active'])
        return self


class Appraisal(models.Model):
    class Status(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        APROBADO = 'APROBADO', 'Aprobado'

    class ConfidenceLevel(models.TextChoices):
        ALTO = 'ALTO', 'Alto'
        MEDIO = 'MEDIO', 'Medio'
        BAJO = 'BAJO', 'Bajo'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folio = models.CharField(max_length=30, unique=True, default=generate_folio, editable=False)

    property = models.ForeignKey(
        'users.Property',
        on_delete=models.PROTECT,  # El historial de avaluos no desaparece con la propiedad
        related_name='appraisals',
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='appraisals',
    )

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BORRADOR)

    # Resultado del motor (nullable: registro manual cuando no hay calculo).
    suggested_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    confidence_level = models.CharField(
        max_length=5,
        choices=ConfidenceLevel.choices,
        default=ConfidenceLevel.BAJO,
    )
    is_manual_fallback = models.BooleanField(default=True)
    comparables_snapshot = models.JSONField(default=list, blank=True)
    # Version de theta con la que se calculo (HU-08); nula en los registros manuales.
    engine_parameters = models.ForeignKey(
        EngineParameters,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='appraisals',
    )
    ai_draft_justification = models.TextField(blank=True, default='')

    # Calibracion HITL del asesor. calibrated_value es nullable solo durante el borrador.
    calibrated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    final_justification = models.TextField(blank=True, default='')

    # Fijadas por approve(); nulas si no hay valor sugerido del motor.
    difference_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    difference_percentage = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    objects = AppraisalQuerySet.as_manager()

    class Meta:
        ordering = ['property', '-created_at']
        constraints = [
            # Solo un borrador abierto por propiedad; los aprobados se acumulan.
            models.UniqueConstraint(
                fields=['property'],
                condition=Q(status='BORRADOR'),
                name='appraisal_single_open_draft',
            ),
            models.CheckConstraint(
                condition=~Q(status='APROBADO') | (
                    Q(calibrated_value__isnull=False)
                    & ~Q(final_justification='')
                    & Q(approved_at__isnull=False)
                ),
                name='appraisal_approved_requires_calibration',
            ),
            models.CheckConstraint(
                condition=Q(calibrated_value__isnull=True) | Q(calibrated_value__gt=0),
                name='appraisal_calibrated_value_positive',
            ),
        ]
        indexes = [
            models.Index(fields=['property', 'status']),
        ]

    def __str__(self):
        return f'{self.folio} ({self.get_status_display()}) - {self.property}'

    # ---------- Reglas de negocio ----------

    @builtins.property  # 'property' es el nombre del FK en esta clase
    def is_approved(self):
        return self.status == self.Status.APROBADO

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self._ensure_mutation_allowed()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Los avalúos no se pueden eliminar.')

    def _ensure_mutation_allowed(self):
        stored = Appraisal.objects.filter(pk=self.pk).values().first()
        if stored is None:
            return
        if stored['status'] == self.Status.APROBADO:
            raise ValidationError(
                'Un avalúo aprobado no se puede modificar. Para recalibrar cree un avalúo nuevo.'
            )
        changed = {
            field.attname
            for field in self._meta.concrete_fields
            if getattr(self, field.attname) != stored[field.attname]
        }
        forbidden = changed - MUTABLE_FIELDS
        if forbidden:
            raise ValidationError(
                f'Campos inmutables en el avalúo: {", ".join(sorted(forbidden))}.'
            )

    @classmethod
    def create_draft(cls, *, property, agent, comparables=None):
        '''
        Unica via para iniciar un avaluo (HU-08). Falla si ya hay un borrador abierto.
        - comparables=None: registro manual de confianza baja (DS-02, boton "Registro manual").
        - comparables=[Property, ...]: los confirmados por el asesor en I-11 (HU-04). El motor
          (HU-06, DS-21) calcula con 3 a 5; con 0 a 2 queda manual (C-02, opcion A) y guarda
          los encontrados como referencia. El resultado se escribe al crear, nunca despues.
        El borrador de IA (HU-07) sigue pendiente.
        '''
        if cls.objects.filter(property=property, status=cls.Status.BORRADOR).exists():
            raise ValidationError('La propiedad ya tiene un avalúo en borrador.')

        appraisal = cls(
            property=property,
            agent=agent,
            suggested_value=None,
            confidence_level=cls.ConfidenceLevel.BAJO,
            is_manual_fallback=True,
            comparables_snapshot=[],
            ai_draft_justification='',
        )
        if comparables is not None:
            appraisal._apply_engine(property, comparables)
        appraisal.full_clean()
        appraisal.save()
        return appraisal

    def _apply_engine(self, property_obj, comparables):
        parameters = EngineParameters.active()
        if parameters is None:
            raise ValidationError('No hay una versión activa de los parámetros del motor.')
        blocker = subject_blocker(property_obj)
        if blocker and comparables:
            raise ValidationError({'comparables': blocker})

        candidates = find_candidates(property_obj, parameters.parameters)
        valid_ids = {candidate.id for candidate, _ in candidates}
        invalid = [comparable.id for comparable in comparables if comparable.id not in valid_ids]
        if invalid:
            raise ValidationError({'comparables': (
                'No son comparables válidos (tipo, estado, antigüedad o zona): '
                + ', '.join(f'#{pk}' for pk in sorted(invalid)) + '.'
            )})
        try:
            result = compute(
                Sample.from_property(property_obj),
                [Sample.from_property(comparable) for comparable in comparables],
                parameters.parameters,
                params_version=parameters.version,
            )
        except EngineError as error:
            raise ValidationError({'comparables': str(error)})

        self.suggested_value = result.suggested_value
        self.confidence_level = result.confidence_level
        self.is_manual_fallback = result.is_manual_fallback
        self.comparables_snapshot = result.snapshot
        self.engine_parameters = None if result.is_manual_fallback else parameters

    def calibrate(self, *, calibrated_value=None, final_justification=None):
        '''Calibracion HITL: el asesor ajusta el valor y la justificacion del borrador.'''
        if self.is_approved:
            raise ValidationError('Un avalúo aprobado no se puede modificar.')
        update_fields = []
        if calibrated_value is not None:
            self.calibrated_value = calibrated_value
            update_fields.append('calibrated_value')
        if final_justification is not None:
            self.final_justification = final_justification.strip()
            update_fields.append('final_justification')
        if update_fields:
            self.full_clean()
            self.save(update_fields=update_fields)
        return self

    def approve(self):
        '''
        HU-08: congela el avaluo. select_for_update evita que dos aprobaciones
        simultaneas (o una calibracion concurrente) pisen el registro.
        '''
        with transaction.atomic():
            locked = Appraisal.objects.select_for_update().get(pk=self.pk)
            if locked.is_approved:
                raise ValidationError('El avalúo ya fue aprobado.')

            errors = {}
            if locked.calibrated_value is None:
                errors['calibrated_value'] = 'Debe indicar el valor calibrado antes de aprobar.'
            if not locked.final_justification.strip():
                errors['final_justification'] = 'Debe redactar la justificación antes de aprobar.'
            if errors:
                raise ValidationError(errors)

            if locked.suggested_value:
                difference = locked.calibrated_value - locked.suggested_value
                locked.difference_amount = difference.quantize(CENTS, rounding=ROUND_HALF_UP)
                locked.difference_percentage = (
                    difference / locked.suggested_value * 100
                ).quantize(CENTS, rounding=ROUND_HALF_UP)
            else:
                locked.difference_amount = None
                locked.difference_percentage = None

            locked.status = self.Status.APROBADO
            locked.approved_at = timezone.now()
            locked.save(update_fields=[
                'status', 'approved_at', 'difference_amount', 'difference_percentage',
            ])

        self.refresh_from_db()
        return self
