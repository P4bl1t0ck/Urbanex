from rest_framework import serializers

from .models import Contact, Opportunity, OpportunityInteraction, OpportunityStatusHistory
from .services import advance_blocker, assignable_agents, eligible_properties, next_status


def user_display_name(user):
    return user.get_full_name() or user.username or user.email


class ContactSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'full_name', 'phone', 'email']
        read_only_fields = fields


class OpportunitySerializer(serializers.ModelSerializer):
    '''Lectura de la cartera (HU-34, I-06). Todos los campos son de solo lectura.'''
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    origin_channel_display = serializers.CharField(source='get_origin_channel_display', read_only=True)
    contact = ContactSummarySerializer(read_only=True)
    property = serializers.SerializerMethodField()
    assigned_agent = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'id', 'status', 'status_display', 'origin_channel', 'origin_channel_display',
            'contact', 'property', 'assigned_agent', 'last_activity_at', 'created_at',
        ]
        read_only_fields = fields

    def get_property(self, obj):
        return {
            'id': obj.property_id,
            'title': obj.property.title,
            'sector': obj.property.location,
            'property_type': obj.property.property_type,
        }

    def get_assigned_agent(self, obj):
        return {'id': obj.assigned_agent_id, 'name': user_display_name(obj.assigned_agent)}


class OpportunityOpenSerializer(serializers.Serializer):
    '''Entrada de la apertura manual (HU-27, I-07). Las reglas de negocio estan en el servicio.'''
    full_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=32)
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    privacy_accepted = serializers.BooleanField(default=False)
    # Solo propiedades y asesores elegibles: un id ajeno o inexistente da el mismo error (DT-67).
    property = serializers.PrimaryKeyRelatedField(
        queryset=eligible_properties(),
        error_messages={'does_not_exist': 'Elija una propiedad disponible.'},
    )
    assigned_agent = serializers.PrimaryKeyRelatedField(
        queryset=assignable_agents(), required=False, allow_null=True, default=None,
        error_messages={'does_not_exist': 'El responsable debe ser un asesor activo.'},
    )


class EligiblePropertySerializer(serializers.Serializer):
    '''
    Propiedades para el selector de I-07: solo los datos publicos del catalogo (titulo, sector,
    tipo, precio y foto), nunca el asesor ni datos internos (DS-28, DT-39, SEC-03). El sector es
    `location` hasta que exista Property.zone (N-03).
    '''
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    sector = serializers.CharField(source='location', read_only=True)
    property_type = serializers.CharField(read_only=True)
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    photo = serializers.SerializerMethodField()

    def get_photo(self, obj):
        image = next(iter(obj.images.all()), None)
        if image is None or not image.image:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(image.image.url) if request else image.image.url


class WebInterestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    '''
    Entrada de HU-16 (P-07). Solo forma: las reglas (celular DS-28, LOPDP, correo, largo del
    mensaje) las aplica services.validate_web_interest().
    '''
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=300)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=40)
    email = serializers.CharField(required=False, allow_blank=True, max_length=254)
    email_opt_in = serializers.BooleanField(required=False, default=False)
    message = serializers.CharField(required=False, allow_blank=True, max_length=2000)
    privacy_accepted = serializers.BooleanField(required=False, default=False)


def user_summary(user):
    return {'id': user.pk, 'name': user_display_name(user)} if user else None


class StatusHistorySerializer(serializers.ModelSerializer):
    '''Historial de estados de I-06A. changed_by es null en los cambios del sistema o del portal.'''
    previous_status_display = serializers.SerializerMethodField()
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    changed_by = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityStatusHistory
        fields = ['id', 'previous_status', 'previous_status_display', 'new_status',
                  'new_status_display', 'changed_by', 'reason', 'created_at']
        read_only_fields = fields

    def get_previous_status_display(self, obj):
        return obj.get_previous_status_display() if obj.previous_status else ''

    def get_changed_by(self, obj):
        return user_summary(obj.changed_by)


class InteractionSerializer(serializers.ModelSerializer):
    '''Interacciones de I-06A (HU-30). author es null en las de tipo SISTEMA.'''
    interaction_type_display = serializers.CharField(source='get_interaction_type_display',
                                                     read_only=True)
    author = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityInteraction
        fields = ['id', 'interaction_type', 'interaction_type_display', 'notes', 'offered_price',
                  'visit', 'author', 'created_at']
        read_only_fields = fields

    def get_author(self, obj):
        return user_summary(obj.author)


class OpportunityDetailSerializer(OpportunitySerializer):
    '''
    Detalle de la oportunidad (I-06A, HU-29 y HU-30): datos de la cartera mas el precio final
    acordado, el siguiente estado permitido, el historial, las interacciones y las visitas.
    '''
    next_status = serializers.SerializerMethodField()
    next_status_display = serializers.SerializerMethodField()
    advance_blocked_reason = serializers.SerializerMethodField()
    accepts_interactions = serializers.SerializerMethodField()
    status_history = StatusHistorySerializer(many=True, read_only=True)
    interactions = InteractionSerializer(many=True, read_only=True)
    visits = serializers.SerializerMethodField()

    class Meta(OpportunitySerializer.Meta):
        fields = OpportunitySerializer.Meta.fields + [
            'agreed_final_price', 'next_status', 'next_status_display', 'advance_blocked_reason',
            'accepts_interactions', 'status_history', 'interactions', 'visits',
        ]
        read_only_fields = fields

    def get_next_status(self, obj):
        return next_status(obj)

    def get_advance_blocked_reason(self, obj):
        # Mismo criterio que la API (advance_status): el boton se deshabilita con este texto.
        return advance_blocker(obj) if next_status(obj) else ''

    def get_accepts_interactions(self, obj):
        return obj.status != Opportunity.Status.CIERRE

    def get_next_status_display(self, obj):
        target = next_status(obj)
        return Opportunity.Status(target).label if target else ''

    def get_visits(self, obj):
        return [
            {'id': visit.pk, 'scheduled_start': visit.scheduled_start,
             'scheduled_end': visit.scheduled_end, 'status': visit.status,
             'status_display': visit.get_status_display()}
            for visit in obj.visits.all()
        ]


class StatusChangeSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    '''Entrada de HU-29. Las reglas de la secuencia las aplica services.advance_status().'''
    status = serializers.ChoiceField(choices=Opportunity.Status.choices)
    agreed_final_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True, default=None,
    )


class InteractionCreateSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    '''Entrada de HU-30. Las reglas las aplican services.add_interaction() y el modelo.'''
    interaction_type = serializers.ChoiceField(choices=OpportunityInteraction.Type.choices)
    notes = serializers.CharField(allow_blank=True, max_length=2000, trim_whitespace=True)
    offered_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True, default=None,
    )
    visit = serializers.IntegerField(required=False, allow_null=True, default=None)


class AgentOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return user_display_name(obj)
