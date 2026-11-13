import builtins

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .validators import validate_normalized_phone

'''
Seguimiento de oportunidades (RF-05, RF-06): modelos del Contexto Maestro §7, que los ubicaba en
apps.crm; la app se llama apps.opportunities por DS-27.

Primer corte (DS-26 a DS-28): apertura manual (HU-27, I-07) y cartera con filtros (HU-34, I-06).
Opportunity ya tiene todos los campos de §7, como DS-03 en avaluos, aunque la maquina de estados
de RF-06 (HU-29, HU-31, HU-35) llega en un corte posterior.

Regla de RF-05: un contacto puede tener varias oportunidades, pero solo una activa por inmueble.
Activa = cualquier estado salvo CIERRE y PERDIDA (DS-28), incluidos LISTA_INTERESADOS y
PENDIENTE_COMISION. La garantiza una restriccion condicional de la BD (§12.4).
'''

# Estados que liberan la regla de una oportunidad activa por contacto e inmueble.
TERMINAL_STATUSES = ('CIERRE', 'PERDIDA')

# Motivo del historial cuando el cambio lo provoca el cliente sin cuenta (DS-39).
SYSTEM_REASON_CLIENT_PORTAL = 'Solicitud del cliente desde el portal'


class OriginChannel(models.TextChoices):
    CATALOGO_WEB = 'CATALOGO_WEB', 'Catálogo web'
    WHATSAPP = 'WHATSAPP', 'WhatsApp'
    MESSENGER = 'MESSENGER', 'Messenger'
    CAMPANA = 'CAMPANA', 'Campaña'
    INTERES_RESERVADA = 'INTERES_RESERVADA', 'Interés en reservada'
    MANUAL = 'MANUAL', 'Captación manual'


class Contact(models.Model):
    full_name = models.CharField(max_length=150)
    # Normalizado por normalize_phone(): +5939XXXXXXXX (HU-27, DS-28).
    phone = models.CharField(max_length=16, unique=True, validators=[validate_normalized_phone])
    email = models.EmailField(blank=True, default='')
    # RF-03: el canal de origen no lo editan los usuarios internos.
    origin_channel = models.CharField(max_length=20, choices=OriginChannel.choices, editable=False)
    # LOPDP: fecha y hora exactas en que el interesado acepto la politica de privacidad.
    privacy_accepted_at = models.DateTimeField(null=True, blank=True)
    email_opt_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'contacto'
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} ({self.phone})'


class OpportunityQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status__in=TERMINAL_STATUSES)


class Opportunity(models.Model):
    class Status(models.TextChoices):
        CONTACTO_INICIAL = 'CONTACTO_INICIAL', 'Contacto inicial'
        LISTA_INTERESADOS = 'LISTA_INTERESADOS', 'Lista de interesados'
        VISITA_PROGRAMADA = 'VISITA_PROGRAMADA', 'Visita programada'
        EN_NEGOCIACION = 'EN_NEGOCIACION', 'En negociación'
        RESERVADA = 'RESERVADA', 'Reservada'
        EVALUACION_DOCUMENTAL = 'EVALUACION_DOCUMENTAL', 'Evaluación documental'
        PENDIENTE_CIERRE = 'PENDIENTE_CIERRE', 'Pendiente de cierre'
        PENDIENTE_COMISION = 'PENDIENTE_COMISION', 'Pendiente de comisión'
        CIERRE = 'CIERRE', 'Cierre'
        PERDIDA = 'PERDIDA', 'Perdida'

    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name='opportunities')
    property = models.ForeignKey(
        'users.Property',
        on_delete=models.PROTECT,  # El seguimiento comercial no desaparece con la propiedad
        related_name='opportunities',
    )
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='assigned_opportunities',
    )
    origin_channel = models.CharField(max_length=20, choices=OriginChannel.choices, editable=False)
    status = models.CharField(max_length=25, choices=Status.choices, default=Status.CONTACTO_INICIAL)

    # Reserva, cierre y perdida (HU-29, HU-31, HU-35, RF-07): aun sin uso en este corte.
    reservation_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    agreed_final_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    admin_confirmed_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_adjustment_reason = models.TextField(blank=True, default='')
    loss_or_reversion_reason = models.TextField(blank=True, default='')

    # Ultimo cambio de estado o interaccion; lo usara el recordatorio de inactividad (RF-16).
    last_activity_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OpportunityQuerySet.as_manager()

    class Meta:
        verbose_name = 'oportunidad'
        verbose_name_plural = 'oportunidades'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['contact', 'property'],
                condition=~Q(status__in=TERMINAL_STATUSES),
                name='opportunity_single_active_per_contact_property',
            ),
        ]
        indexes = [
            models.Index(fields=['assigned_agent', 'status'], name='opp_agent_status_idx'),
            models.Index(fields=['status'], name='opp_status_idx'),
            models.Index(fields=['created_at'], name='opp_created_idx'),
        ]

    def __str__(self):
        return f'Oportunidad #{self.pk} ({self.get_status_display()}) - {self.contact}'

    @builtins.property  # 'property' es el nombre del FK en esta clase
    def is_active(self):
        return self.status not in TERMINAL_STATUSES


class StatusHistoryQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError('El historial de estados no se puede modificar.')

    def delete(self):
        raise ValidationError('El historial de estados no se puede eliminar.')


class OpportunityStatusHistory(models.Model):
    '''
    Historial inmutable de estados (RF-06, HU-29): usuario, fecha y hora de cada cambio, sin
    edicion retroactiva. La apertura queda como la primera fila, con previous_status vacio.

    changed_by es opcional (DS-39, HU-19): los cambios que provoca el cliente anonimo desde el
    portal no tienen usuario y llevan el motivo SYSTEM_REASON_CLIENT_PORTAL.
    '''
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.PROTECT,  # Una oportunidad con historial no se puede borrar
        related_name='status_history',
    )
    previous_status = models.CharField(
        max_length=25, choices=Opportunity.Status.choices, blank=True, default='',
    )
    new_status = models.CharField(max_length=25, choices=Opportunity.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='opportunity_status_changes',
        null=True,
        blank=True,
    )
    reason = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = StatusHistoryQuerySet.as_manager()

    class Meta:
        verbose_name = 'cambio de estado de oportunidad'
        verbose_name_plural = 'historial de estados de oportunidades'
        ordering = ['created_at', 'id']  # Orden cronologico (HU-33)

    def __str__(self):
        return f'#{self.opportunity_id}: {self.previous_status or "—"} -> {self.new_status}'

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError('El historial de estados no se puede modificar.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('El historial de estados no se puede eliminar.')


class InteractionQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError('El historial de interacciones no se puede modificar.')

    def delete(self):
        raise ValidationError('El historial de interacciones no se puede eliminar.')


class OpportunityInteraction(models.Model):
    '''
    Historial inmutable de interacciones y negociacion (RF-06, HU-30; Contexto Maestro §7).
    Las contraofertas no cambian el precio publico de la propiedad (RF-06).

    Reglas del lote 4 (DS-50, decision de Pablo, 2026-11-09):
    - Por la API, el asesor asignado o el admin solo registran NOTA o CONTRAOFERTA; SISTEMA lo
      escribe unicamente el backend.
    - offered_price es obligatorio y mayor que 0 solo en CONTRAOFERTA; en los demas tipos va vacio.
    - author vacio solo en SISTEMA: el interes que llega desde el formulario publico (HU-16) no
      tiene usuario y se guarda como "Interes desde el formulario web: ...".
    - visit es opcional, para enlazar la interaccion con una visita de la misma oportunidad.
    '''

    class Type(models.TextChoices):
        NOTA = 'NOTA', 'Nota'
        CONTRAOFERTA = 'CONTRAOFERTA', 'Contraoferta'
        SISTEMA = 'SISTEMA', 'Sistema'

    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.PROTECT,  # Una oportunidad con interacciones no se puede borrar
        related_name='interactions',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='opportunity_interactions',
        null=True,
        blank=True,
    )
    interaction_type = models.CharField(max_length=15, choices=Type.choices)
    offered_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField()
    visit = models.ForeignKey(
        'visits.Visit',
        on_delete=models.PROTECT,
        related_name='interactions',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = InteractionQuerySet.as_manager()

    class Meta:
        verbose_name = 'interacción de oportunidad'
        verbose_name_plural = 'interacciones de oportunidades'
        ordering = ['created_at', 'id']  # Orden cronologico (HU-33)
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(interaction_type='CONTRAOFERTA', offered_price__isnull=False,
                      offered_price__gt=0)
                    | (~Q(interaction_type='CONTRAOFERTA') & Q(offered_price__isnull=True))
                ),
                name='interaction_offered_price_only_in_counteroffer',
            ),
            models.CheckConstraint(
                condition=Q(interaction_type='SISTEMA') | Q(author__isnull=False),
                name='interaction_author_required_unless_system',
            ),
        ]
        indexes = [
            models.Index(fields=['opportunity', 'created_at'], name='interaction_opp_created_idx'),
        ]

    def __str__(self):
        return f'#{self.opportunity_id}: {self.get_interaction_type_display()}'

    def clean(self):
        errors = {}
        if not (self.notes or '').strip():
            errors['notes'] = 'Las observaciones son obligatorias.'
        if self.interaction_type == self.Type.CONTRAOFERTA:
            if self.offered_price is None or self.offered_price <= 0:
                errors['offered_price'] = 'La contraoferta necesita un precio mayor que 0.'
        elif self.offered_price is not None:
            errors['offered_price'] = 'Solo una contraoferta lleva precio ofrecido.'
        if self.interaction_type != self.Type.SISTEMA and self.author_id is None:
            errors['author'] = 'La interacción la registra un usuario.'
        if (self.visit_id is not None and self.opportunity_id is not None
                and self.visit.opportunity_id != self.opportunity_id):
            errors['visit'] = 'La visita debe ser de la misma oportunidad.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError('El historial de interacciones no se puede modificar.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('El historial de interacciones no se puede eliminar.')
