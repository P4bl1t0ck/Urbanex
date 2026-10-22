from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.users.models import Property
from .models import MAX_FILE_SIZE_BYTES, Document

# Firmas binarias (magic bytes). El content_type lo envia el navegador y se puede
# falsificar, por eso el tipo real se deduce de los primeros bytes del archivo.
FILE_SIGNATURES = (
    (b'%PDF', 'application/pdf'),
    (b'\xff\xd8\xff', 'image/jpeg'),
    (b'\x89PNG\r\n\x1a\n', 'image/png'),
)


def detect_mime_type(uploaded_file):
    header = uploaded_file.read(12)
    uploaded_file.seek(0)
    for signature, mime_type in FILE_SIGNATURES:
        if header.startswith(signature):
            return mime_type
    if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return 'image/webp'
    return None


def user_can_access_property(user, property_obj):
    # El asesor solo accede al expediente de sus propiedades; el Admin a todos (RF-10).
    return user.role == 'admin' or property_obj.agent_id == user.id


class DocumentSerializer(serializers.ModelSerializer):
    '''Lectura del expediente. Nunca expone la ruta ni la URL del archivo privado.'''
    doc_type_display = serializers.CharField(source='get_doc_type_display', read_only=True)
    validation_status_display = serializers.CharField(source='get_validation_status_display', read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    days_to_expiration = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'property', 'doc_type', 'doc_type_display', 'is_critical',
            'original_filename', 'file_size_bytes', 'mime_type',
            'version', 'is_current_version', 'issue_date', 'expiration_date',
            'is_expired', 'is_expiring_soon', 'days_to_expiration',
            'validation_status', 'validation_status_display', 'rejection_reason',
            'uploaded_by', 'uploaded_by_name', 'validated_by', 'validated_at', 'created_at',
        ]
        read_only_fields = fields

    def get_uploaded_by_name(self, obj):
        user = obj.uploaded_by
        return f'{user.first_name} {user.last_name}'.strip() or user.username or user.email


class DocumentUploadSerializer(serializers.Serializer):
    '''HU-03: carga de un documento. Cada carga crea una nueva version (nunca sobrescribe).'''
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())
    doc_type = serializers.ChoiceField(choices=Document.DocType.choices)
    file = serializers.FileField()
    issue_date = serializers.DateField()
    expiration_date = serializers.DateField()
    is_critical = serializers.BooleanField(default=False)

    def validate_property(self, property_obj):
        if not user_can_access_property(self.context['request'].user, property_obj):
            raise serializers.ValidationError('No tienes permiso sobre el expediente de esta propiedad.')
        return property_obj

    def validate_file(self, uploaded_file):
        if uploaded_file.size > MAX_FILE_SIZE_BYTES:
            raise serializers.ValidationError('El archivo supera el máximo permitido de 20 MB.')
        mime_type = detect_mime_type(uploaded_file)
        if mime_type is None:
            raise serializers.ValidationError('Solo se admiten archivos PDF o imágenes (JPG, PNG, WEBP).')
        self._detected_mime_type = mime_type
        return uploaded_file

    def validate(self, attrs):
        if attrs['expiration_date'] < attrs['issue_date']:
            raise serializers.ValidationError(
                {'expiration_date': 'La fecha de vigencia no puede ser anterior a la de emisión.'}
            )
        return attrs

    def create(self, validated_data):
        try:
            return Document.upload_new_version(
                uploaded_by=self.context['request'].user,
                mime_type=self._detected_mime_type,
                **validated_data,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                error.message_dict if hasattr(error, 'error_dict') else error.messages
            )

    def to_representation(self, instance):
        return DocumentSerializer(instance, context=self.context).data
