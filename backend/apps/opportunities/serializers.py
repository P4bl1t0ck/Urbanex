from rest_framework import serializers

from .models import Contact, Opportunity
from .services import assignable_agents, eligible_properties


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


class AgentOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return user_display_name(obj)
