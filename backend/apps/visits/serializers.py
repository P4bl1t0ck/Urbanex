from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from apps.appraisals.serializers import to_drf_error
from .models import ECUADOR_TZ, AgentAvailability, AvailabilityException, Visit
from .services import MAX_CANCEL_REASON_LENGTH, client_can_cancel, client_cancel_deadline


def agent_display_name(user):
    return user.get_full_name() or user.username


class AgentScopedSerializer(serializers.ModelSerializer):
    '''
    El asesor de la franja lo decide la vista (resolve_target_agent) y llega en el contexto
    'agent'; en una edicion es el de la instancia y no se cambia. validate() aplica clean() del
    modelo sobre los valores finales (incluidos los de un PATCH parcial).
    '''
    agent_name = serializers.SerializerMethodField()

    def get_agent_name(self, obj):
        return agent_display_name(obj.agent)

    def validate(self, attrs):
        model = self.Meta.model
        if self.instance is not None:
            values = {field.attname: getattr(self.instance, field.attname)
                      for field in model._meta.concrete_fields}
            candidate = model(**values)
        else:
            candidate = model(agent=self.context['agent'])
        for name, value in attrs.items():
            setattr(candidate, name, value)
        try:
            candidate.clean()
        except DjangoValidationError as error:
            raise to_drf_error(error)
        return attrs


class AvailabilitySerializer(AgentScopedSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = AgentAvailability
        fields = ['id', 'agent', 'agent_name', 'day_of_week', 'day_name', 'start_time',
                  'end_time', 'slot_duration_minutes']
        read_only_fields = ['agent']


class AgendaVisitSerializer(serializers.ModelSerializer):
    '''
    Visita en la agenda del asesor (HU-24, I-08): propiedad, cliente, fecha y hora.
    Datos del cliente como en Oportunidades: nombre, telefono y correo opcional (si cumple la
    LOPDP es una pregunta abierta para el tutor). Nunca incluye cancellation_token.

    Lote 3 (DS-39):
    - needs_whatsapp_confirmation: no se envio confirmacion por correo (HU-20);
    - followup_agent_name: asesor de la oportunidad si no es el de la visita;
    - can_record_outcome: Programada y ya empezo (HU-25); el permiso lo revisa el endpoint.
    '''
    scheduled_start = serializers.SerializerMethodField()
    scheduled_end = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    property = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    needs_whatsapp_confirmation = serializers.SerializerMethodField()
    followup_agent_name = serializers.SerializerMethodField()
    can_record_outcome = serializers.SerializerMethodField()
    outcome_recorded_at = serializers.SerializerMethodField()
    outcome_recorded_by_name = serializers.SerializerMethodField()
    # HU-21 y HU-23 (DS-52): Programada y antes de su inicio; el permiso lo revisa el endpoint.
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = ['id', 'scheduled_start', 'scheduled_end', 'status', 'status_display',
                  'property', 'client', 'opportunity', 'needs_whatsapp_confirmation',
                  'followup_agent_name', 'can_record_outcome', 'outcome_notes',
                  'outcome_recorded_at', 'outcome_recorded_by_name', 'can_cancel']
        read_only_fields = fields

    def get_can_cancel(self, obj):
        now = self.context.get('now') or timezone.now()
        return obj.status == Visit.Status.PROGRAMADA and now < obj.scheduled_start

    def get_needs_whatsapp_confirmation(self, obj):
        return obj.status == Visit.Status.PROGRAMADA and not obj.confirmation_email

    def get_followup_agent_name(self, obj):
        followup = obj.opportunity.assigned_agent
        if followup is None or followup.pk == obj.agent_id:
            return None
        return agent_display_name(followup)

    def get_can_record_outcome(self, obj):
        now = self.context.get('now') or timezone.now()
        return (obj.status == Visit.Status.PROGRAMADA and obj.outcome_recorded_at is None
                and obj.scheduled_start <= now)

    def get_outcome_recorded_at(self, obj):
        if obj.outcome_recorded_at is None:
            return None
        return obj.outcome_recorded_at.astimezone(ECUADOR_TZ).isoformat()

    def get_outcome_recorded_by_name(self, obj):
        user = obj.outcome_recorded_by
        return agent_display_name(user) if user else None

    def get_scheduled_start(self, obj):
        return obj.scheduled_start.astimezone(ECUADOR_TZ).isoformat()

    def get_scheduled_end(self, obj):
        return obj.scheduled_end.astimezone(ECUADOR_TZ).isoformat()

    def get_property(self, obj):
        return {'id': obj.property_id, 'title': obj.property.title,
                'location': obj.property.location}

    def get_client(self, obj):
        contact = obj.opportunity.contact
        return {'full_name': contact.full_name, 'phone': contact.phone, 'email': contact.email}


class VisitRequestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    '''
    Entrada de HU-19 (P-07). Solo forma: las reglas (celular DS-28, LOPDP, correo) las aplica
    services.validate_request_data(). Una hora sin zona se toma como hora de Ecuador.
    '''
    start = serializers.DateTimeField(default_timezone=ECUADOR_TZ)
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=300)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=40)
    email = serializers.CharField(required=False, allow_blank=True, max_length=254)
    email_opt_in = serializers.BooleanField(required=False, default=False)
    privacy_accepted = serializers.BooleanField(required=False, default=False)


class OutcomeSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    '''Entrada de HU-25; las reglas las aplica services.record_outcome().'''
    status = serializers.CharField()
    outcome_notes = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class CancelVisitSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    '''Entrada de HU-21 desde la agenda; las reglas las aplica services.cancel_visit().'''
    reason = serializers.CharField(required=False, allow_blank=True, default='',
                                   max_length=MAX_CANCEL_REASON_LENGTH)


def public_agent(user):
    '''Datos del asesor en P-08: nombre, apellido y telefono (decision de Pablo, 2026-11-09).'''
    return {'first_name': user.first_name, 'last_name': user.last_name, 'phone': user.phone}


class PublicVisitSerializer(serializers.ModelSerializer):
    '''
    P-08 (HU-20), publico por token: propiedad, fecha y hora, estado y asesor(es). Sin datos del
    cliente, sin observaciones y sin el token.
    '''
    scheduled_start = serializers.SerializerMethodField()
    scheduled_end = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    property = serializers.SerializerMethodField()
    visit_agent = serializers.SerializerMethodField()
    followup_agent = serializers.SerializerMethodField()
    # HU-21 (DS-52): el cliente cancela hasta 1 hora antes del inicio.
    can_cancel = serializers.SerializerMethodField()
    cancel_until = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = ['scheduled_start', 'scheduled_end', 'status', 'status_display', 'property',
                  'visit_agent', 'followup_agent', 'can_cancel', 'cancel_until']
        read_only_fields = fields

    def get_can_cancel(self, obj):
        return client_can_cancel(obj, now=self.context.get('now'))

    def get_cancel_until(self, obj):
        return client_cancel_deadline(obj).astimezone(ECUADOR_TZ).isoformat()

    def get_scheduled_start(self, obj):
        return obj.scheduled_start.astimezone(ECUADOR_TZ).isoformat()

    def get_scheduled_end(self, obj):
        return obj.scheduled_end.astimezone(ECUADOR_TZ).isoformat()

    def get_property(self, obj):
        return {'id': obj.property_id, 'title': obj.property.title,
                'location': obj.property.location}

    def get_visit_agent(self, obj):
        return public_agent(obj.agent)

    def get_followup_agent(self, obj):
        followup = obj.opportunity.assigned_agent
        if followup is None or followup.pk == obj.agent_id:
            return None
        return public_agent(followup)


class AvailabilityExceptionSerializer(AgentScopedSerializer):
    is_full_day = serializers.BooleanField(read_only=True)

    class Meta:
        model = AvailabilityException
        fields = ['id', 'agent', 'agent_name', 'exception_date', 'start_time', 'end_time',
                  'is_full_day', 'reason']
        read_only_fields = ['agent']
