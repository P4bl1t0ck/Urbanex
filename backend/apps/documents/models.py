import builtins
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models, transaction
from django.db.models import Max, Q
from django.utils import timezone

'''
Expediente digital (RF-10, HU-03, HU-37).

Reglas de inmutabilidad (Contexto Maestro 7.4):
- Un documento JAMAS se elimina ni se sobrescribe su archivo, ruta o version.
- Subir un reemplazo crea una fila nueva con version = n + 1 y la anterior pasa a
  is_current_version = False, ambas cosas en la misma transaccion.
- La validacion del Administrador solo modifica validation_status, validated_by,
  validated_at y rejection_reason.
'''

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB (RF-10)
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/webp',
}
EXPIRATION_ALERT_DAYS = 30  # Alerta cuando faltan 30 dias o menos (RF-10 / RF-16)

# Campos que la validacion administrativa (HU-37) puede tocar. is_current_version
# solo lo cambia upload_new_version() al crear la siguiente version.
MUTABLE_FIELDS = {
    'validation_status',
    'validated_by',
    'validated_at',
    'rejection_reason',
    'is_current_version',
}

# Almacenamiento privado: fuera de MEDIA_ROOT para que Django no lo sirva por /media/.
# Se reemplazara por Supabase Storage + URLs firmadas (HU-38, Sprint 6).
private_storage = FileSystemStorage(location=settings.BASE_DIR / 'private_media')


def document_upload_path(instance, filename):
    # Nunca se usa el nombre que envia el usuario (RNF-04): solo se conserva la extension.
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'bin'
    return (
        f'documents/property_{instance.property_id}/{instance.doc_type.lower()}/'
        f'v{instance.version}_{uuid.uuid4().hex}.{extension}'
    )


class DocumentQuerySet(models.QuerySet):
    def delete(self):
        raise ValidationError('Los documentos del expediente no se pueden eliminar.')

    def update(self, **kwargs):
        forbidden = set(kwargs) - MUTABLE_FIELDS
        if forbidden:
            raise ValidationError(
                f'Campos inmutables en el expediente: {", ".join(sorted(forbidden))}.'
            )
        return super().update(**kwargs)

    def current(self):
        return self.filter(is_current_version=True)

    def expiring_soon(self, days=EXPIRATION_ALERT_DAYS):
        today = timezone.localdate()
        return self.current().filter(
            expiration_date__gte=today,
            expiration_date__lte=today + timedelta(days=days),
        )


class Document(models.Model):
    class DocType(models.TextChoices):
        CORRETAJE = 'CORRETAJE', 'Contrato de corretaje'
        CEDULA_CATASTRAL = 'CEDULA_CATASTRAL', 'Cédula catastral'
        ESCRITURA = 'ESCRITURA', 'Escrituras'
        GRAVAMENES = 'GRAVAMENES', 'Certificado de gravámenes'
        PREDIAL = 'PREDIAL', 'Comprobante predial / tributario'
        CERT_LABORAL = 'CERT_LABORAL', 'Certificado laboral'
        CERT_BANCARIO = 'CERT_BANCARIO', 'Certificado bancario'
        OTRO = 'OTRO', 'Otro'

    class ValidationStatus(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        APROBADO = 'APROBADO', 'Aprobado'
        RECHAZADO = 'RECHAZADO', 'Rechazado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # El modelo 7.4 incluye tambien opportunity (FK nullable). Se agregara cuando exista
    # apps.crm.Opportunity (HU-36, Sprint 7) junto con la regla de "exactamente uno".
    property = models.ForeignKey(
        'users.Property',
        on_delete=models.PROTECT,  # El expediente no puede desaparecer con la propiedad
        related_name='documents',
    )

    doc_type = models.CharField(max_length=30, choices=DocType.choices)
    is_critical = models.BooleanField(default=False)

    # file.name es el storage_path del modelo 7.4.
    file = models.FileField(upload_to=document_upload_path, storage=private_storage, max_length=500)
    original_filename = models.CharField(max_length=255)
    file_size_bytes = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)

    version = models.PositiveIntegerField(default=1)
    is_current_version = models.BooleanField(default=True)

    issue_date = models.DateField()
    expiration_date = models.DateField()

    validation_status = models.CharField(
        max_length=10,
        choices=ValidationStatus.choices,
        default=ValidationStatus.PENDIENTE,
    )
    rejection_reason = models.TextField(blank=True, default='')

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='uploaded_documents',
    )
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='validated_documents',
    )
    validated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = DocumentQuerySet.as_manager()

    class Meta:
        ordering = ['property', 'doc_type', '-version']
        constraints = [
            models.UniqueConstraint(
                fields=['property', 'doc_type', 'version'],
                name='document_unique_version_per_type',
            ),
            # Solo una version vigente por propiedad y tipo de documento.
            models.UniqueConstraint(
                fields=['property', 'doc_type'],
                condition=Q(is_current_version=True),
                name='document_single_current_version',
            ),
            models.CheckConstraint(
                condition=Q(expiration_date__gte=models.F('issue_date')),
                name='document_expiration_after_issue',
            ),
            models.CheckConstraint(
                condition=Q(file_size_bytes__lte=MAX_FILE_SIZE_BYTES),
                name='document_max_20mb',
            ),
            models.CheckConstraint(
                condition=~Q(validation_status='RECHAZADO') | ~Q(rejection_reason=''),
                name='document_rejection_requires_reason',
            ),
        ]
        indexes = [
            models.Index(fields=['property', 'is_current_version']),
            models.Index(fields=['validation_status']),
            models.Index(fields=['expiration_date']),
        ]

    def __str__(self):
        return f'{self.get_doc_type_display()} v{self.version} - {self.property}'

    # ---------- Reglas de negocio ----------

    @builtins.property  # 'property' es el nombre del FK en esta clase
    def is_expired(self):
        return self.expiration_date < timezone.localdate()

    @builtins.property
    def days_to_expiration(self):
        return (self.expiration_date - timezone.localdate()).days

    @builtins.property
    def is_expiring_soon(self):
        return 0 <= self.days_to_expiration <= EXPIRATION_ALERT_DAYS

    def clean(self):
        errors = {}
        if self.file_size_bytes and self.file_size_bytes > MAX_FILE_SIZE_BYTES:
            errors['file'] = 'El archivo supera el máximo permitido de 20 MB.'
        if self.mime_type and self.mime_type not in ALLOWED_MIME_TYPES:
            errors['mime_type'] = 'Solo se admiten archivos PDF o imágenes (JPG, PNG, WEBP).'
        if self.issue_date and self.expiration_date and self.expiration_date < self.issue_date:
            errors['expiration_date'] = 'La fecha de vigencia no puede ser anterior a la de emisión.'
        if self.validation_status == self.ValidationStatus.RECHAZADO and not self.rejection_reason.strip():
            errors['rejection_reason'] = 'Debe indicar el motivo del rechazo.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self._ensure_only_mutable_fields_changed()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Los documentos del expediente no se pueden eliminar.')

    def _ensure_only_mutable_fields_changed(self):
        stored = Document.objects.filter(pk=self.pk).values().first()
        if stored is None:
            return
        changed = {
            field.attname
            for field in self._meta.concrete_fields
            if getattr(self, field.attname) != stored[field.attname]
        }
        # validated_by se guarda como validated_by_id
        forbidden = {name for name in changed if name.removesuffix('_id') not in MUTABLE_FIELDS}
        if forbidden:
            raise ValidationError(
                f'Campos inmutables en el expediente: {", ".join(sorted(forbidden))}. '
                'Para reemplazar el archivo suba una nueva versión.'
            )

    @classmethod
    def upload_new_version(cls, *, property, doc_type, file, uploaded_by,
                           issue_date, expiration_date, is_critical=False, mime_type=None):
        '''
        Unica via para registrar documentos (HU-03 / HU-36). Crea la version n + 1 y
        retira la vigente en la misma transaccion. select_for_update evita que dos
        cargas simultaneas obtengan el mismo numero de version.
        '''
        with transaction.atomic():
            previous = cls.objects.select_for_update().filter(property=property, doc_type=doc_type)
            last_version = previous.aggregate(last=Max('version'))['last'] or 0

            document = cls(
                property=property,
                doc_type=doc_type,
                is_critical=is_critical,
                file=file,
                original_filename=getattr(file, 'name', '')[:255],
                file_size_bytes=file.size,
                mime_type=mime_type or getattr(file, 'content_type', '') or '',
                version=last_version + 1,
                is_current_version=True,
                issue_date=issue_date,
                expiration_date=expiration_date,
                uploaded_by=uploaded_by,
            )
            # Primero se retira la vigente para no violar document_single_current_version;
            # si la validacion falla, el atomic revierte este update.
            previous.filter(is_current_version=True).update(is_current_version=False)
            document.full_clean(exclude=['file'])
            document.save()
        return document

    def validate_document(self, *, admin, approved, reason=''):
        '''HU-37: solo el Administrador aprueba o rechaza.'''
        if getattr(admin, 'role', None) != 'admin':
            raise ValidationError('Solo el Administrador puede validar documentos.')
        if not self.is_current_version:
            raise ValidationError('Solo se puede validar la versión vigente del documento.')

        self.validation_status = (
            self.ValidationStatus.APROBADO if approved else self.ValidationStatus.RECHAZADO
        )
        self.rejection_reason = '' if approved else reason.strip()
        self.validated_by = admin
        self.validated_at = timezone.now()
        self.full_clean(exclude=['file'])
        self.save(update_fields=['validation_status', 'rejection_reason', 'validated_by', 'validated_at'])
