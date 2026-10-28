from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.documents.serializers import user_can_access_property
from apps.users.models import Property
from .engine import round_to_hundreds
from .models import Appraisal


def to_drf_error(error):
    return serializers.ValidationError(
        error.message_dict if hasattr(error, 'error_dict') else error.messages
    )


class AppraisalSerializer(serializers.ModelSerializer):
    '''Lectura del avaluo. Todos los campos son de solo lectura.'''
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    confidence_level_display = serializers.CharField(source='get_confidence_level_display', read_only=True)
    agent_name = serializers.SerializerMethodField()
    # Se guarda exacto; la interfaz lo muestra redondeado a cientos (DS-21, ajuste de Pablo).
    suggested_value_display = serializers.SerializerMethodField()
    engine_parameters_version = serializers.IntegerField(
        source='engine_parameters.version', read_only=True, allow_null=True, default=None,
    )

    class Meta:
        model = Appraisal
        fields = [
            'id', 'folio', 'property', 'agent', 'agent_name', 'status', 'status_display',
            'suggested_value', 'suggested_value_display', 'confidence_level',
            'confidence_level_display', 'is_manual_fallback', 'engine_parameters_version',
            'comparables_snapshot', 'ai_draft_justification',
            'calibrated_value', 'final_justification',
            'difference_amount', 'difference_percentage',
            'created_at', 'approved_at',
        ]
        read_only_fields = fields

    def get_agent_name(self, obj):
        user = obj.agent
        return f'{user.first_name} {user.last_name}'.strip() or user.username or user.email

    def get_suggested_value_display(self, obj):
        if obj.suggested_value is None:
            return None
        return f'{round_to_hundreds(obj.suggested_value):.2f}'


class AppraisalCreateSerializer(serializers.Serializer):
    '''
    HU-08: inicia un avaluo en borrador para una propiedad propia.
    Sin "comparables" es un registro manual; con la lista confirmada en I-11 (HU-04)
    calcula el motor (HU-06). El servidor vuelve a validar cada comparable.
    '''
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())
    # El maximo de 5 (HU-04) lo aplica el motor con su propio mensaje.
    comparables = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(), many=True, required=False,
    )

    def validate_property(self, property_obj):
        if not user_can_access_property(self.context['request'].user, property_obj):
            raise serializers.ValidationError('No tienes permiso sobre esta propiedad.')
        return property_obj

    def create(self, validated_data):
        try:
            return Appraisal.create_draft(agent=self.context['request'].user, **validated_data)
        except DjangoValidationError as error:
            raise to_drf_error(error)

    def to_representation(self, instance):
        return AppraisalSerializer(instance, context=self.context).data


class AppraisalCalibrateSerializer(serializers.Serializer):
    '''Calibracion HITL (PATCH). Solo sobre un borrador.'''
    calibrated_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal('0.01'), required=False,
    )
    final_justification = serializers.CharField(required=False, allow_blank=False, trim_whitespace=True)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError('Indique calibrated_value o final_justification.')
        return attrs

    def update(self, instance, validated_data):
        try:
            return instance.calibrate(**validated_data)
        except DjangoValidationError as error:
            raise to_drf_error(error)

    def to_representation(self, instance):
        return AppraisalSerializer(instance, context=self.context).data
