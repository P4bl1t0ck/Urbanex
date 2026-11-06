from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.appraisals.serializers import to_drf_error
from .models import AgentAvailability, AvailabilityException


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


class AvailabilityExceptionSerializer(AgentScopedSerializer):
    is_full_day = serializers.BooleanField(read_only=True)

    class Meta:
        model = AvailabilityException
        fields = ['id', 'agent', 'agent_name', 'exception_date', 'start_time', 'end_time',
                  'is_full_day', 'reason']
        read_only_fields = ['agent']
