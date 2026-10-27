import io
import os
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw

from apps.appraisals.models import Appraisal
from apps.documents.models import Document
from apps.users.models import Property, PropertyImage
from apps.users.views import get_missing_publication_requirements

'''
Datos de demostracion para desarrollo local (DT-14, decision DS-17).

- La contrasena se lee de la variable de entorno DEMO_PASSWORD; nunca se escribe en el codigo.
- Solo corre con DEBUG=True: crea avaluos y documentos que, por ser inmutables, no se pueden borrar.
- Todas las propiedades nacen en captacion. Los requisitos de HU-53 se cargan con los mismos
  metodos de dominio que usa la API (upload_new_version, create_draft/calibrate/approve), asi que
  ninguna propiedad se publica aqui: publicar se valida desde la interfaz.
- Es idempotente: si se vuelve a ejecutar, actualiza los usuarios y solo agrega lo que falte.
'''

User = get_user_model()

ADMIN_EMAIL = 'admin.demo@urbanex.test'
AGENT_EMAIL = 'asesor.demo@urbanex.test'

# Cada propiedad cubre un caso de las validaciones V-xx de Project_Progress.md.
# Las coordenadas son aproximadas (centro del sector).
DEMO_PROPERTIES = [
    {
        'title': '[DEMO] Casa en Cumbayá - lista para publicar',
        'description': 'Casa de dos plantas con jardín. Tiene foto, corretaje vigente y avalúo aprobado.',
        'property_type': 'casa',
        'price': Decimal('285000.00'),
        'area_m2': 240.0,
        'bedrooms': 4,
        'bathrooms': 3,
        'parking_spaces': 2,
        'location': 'Cumbayá, Quito',
        'latitude': Decimal('-0.200600'),
        'longitude': Decimal('-78.431600'),
        'requirements': {'image', 'brokerage_contract', 'appraisal'},
        'color': (37, 99, 235),
    },
    {
        'title': '[DEMO] Departamento en La Carolina - sin avalúo',
        'description': 'Departamento cerca del parque La Carolina. Tiene foto y corretaje; falta el avalúo (I-12).',
        'property_type': 'departamento',
        'price': Decimal('148000.00'),
        'area_m2': 95.0,
        'bedrooms': 2,
        'bathrooms': 2,
        'parking_spaces': 1,
        'location': 'La Carolina, Quito',
        'latitude': Decimal('-0.185700'),
        'longitude': Decimal('-78.483600'),
        'requirements': {'image', 'brokerage_contract'},
        'color': (22, 163, 74),
    },
    {
        'title': '[DEMO] Local en La Mariscal - sin corretaje',
        'description': 'Local comercial a pie de calle. Tiene foto y avalúo aprobado; falta el contrato de corretaje.',
        'property_type': 'local',
        'price': Decimal('120000.00'),
        'area_m2': 80.0,
        'bedrooms': 0,
        'bathrooms': 1,
        'parking_spaces': 0,
        'location': 'La Mariscal, Quito',
        'latitude': Decimal('-0.203300'),
        'longitude': Decimal('-78.492000'),
        'requirements': {'image', 'appraisal'},
        'color': (217, 119, 6),
    },
    {
        'title': '[DEMO] Terreno en Tumbaco - sin requisitos',
        'description': 'Terreno plano con servicios básicos. Sin foto, sin corretaje y sin avalúo.',
        'property_type': 'terreno',
        'price': Decimal('90000.00'),
        'area_m2': 600.0,
        'bedrooms': 0,
        'bathrooms': 0,
        'parking_spaces': 0,
        'location': 'Tumbaco, Quito',
        'latitude': Decimal('-0.211700'),
        'longitude': Decimal('-78.403300'),
        'requirements': set(),
        'color': (100, 116, 139),
    },
]

# PDF minimo valido de una pagina; el expediente detecta el tipo por los bytes iniciales.
DEMO_PDF = (
    b'%PDF-1.4\n'
    b'1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n'
    b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n'
    b'3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]>>endobj\n'
    b'trailer<</Root 1 0 R>>\n'
    b'%%EOF\n'
)


class Command(BaseCommand):
    help = 'Crea o actualiza usuarios y propiedades de demostracion (solo desarrollo, DT-14).'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('setup_demo_data solo se ejecuta en desarrollo (DEBUG=True).')

        password = os.environ.get('DEMO_PASSWORD', '')
        if not password:
            raise CommandError(
                'Define la variable de entorno DEMO_PASSWORD (por ejemplo, en backend/.env) '
                'con la contrasena de los usuarios demo.'
            )

        with transaction.atomic():
            admin = self._upsert_user(ADMIN_EMAIL, 'admin.demo', 'admin', password, is_staff=True)
            agent = self._upsert_user(AGENT_EMAIL, 'asesor.demo', 'asesor', password, is_staff=False)
            properties = [self._setup_property(spec, agent) for spec in DEMO_PROPERTIES]

        self.stdout.write(self.style.SUCCESS('Datos demo listos.'))
        self.stdout.write(f'  Admin:  {admin.email} (role=admin, is_staff=True)')
        self.stdout.write(f'  Asesor: {agent.email} (role=asesor)')
        self.stdout.write('  Contrasena: la de DEMO_PASSWORD.')
        for property_obj in properties:
            missing = [item['code'] for item in get_missing_publication_requirements(property_obj)]
            self.stdout.write(
                f'  #{property_obj.id} {property_obj.title} [{property_obj.status}] '
                f'falta: {", ".join(missing) or "nada"}'
            )

    # ---------- Usuarios ----------

    def _upsert_user(self, email, username, role, password, *, is_staff):
        # User.email aun no es unico (DT-13): si hay duplicados no se adivina cual usar.
        matches = User.objects.filter(email=email)
        if matches.count() > 1:
            raise CommandError(f'Hay mas de un usuario con el correo {email} (DT-13). Resuelvelo a mano.')

        user = matches.first()
        if user is None:
            if User.objects.filter(username=username).exists():
                raise CommandError(f'El username {username} ya existe con otro correo.')
            user = User(email=email, username=username)

        user.role = role
        user.is_staff = is_staff
        user.is_superuser = False
        user.is_active = True
        user.is_locked = False
        user.failed_attempts = 0
        try:
            password_validation.validate_password(password, user)
        except ValidationError as error:
            raise CommandError(f'DEMO_PASSWORD no es valida: {" ".join(error.messages)}')
        user.set_password(password)
        user.save()
        return user

    # ---------- Propiedades y requisitos de HU-53 ----------

    def _setup_property(self, spec, agent):
        fields = {
            key: value for key, value in spec.items()
            if key not in {'title', 'requirements', 'color'}
        }
        # status no se pasa: el modelo crea en captacion (DT-09, DS-17).
        property_obj, _ = Property.objects.get_or_create(
            title=spec['title'],
            agent=agent,
            defaults=fields,
        )

        if 'image' in spec['requirements'] and not property_obj.images.exists():
            PropertyImage.objects.create(
                property=property_obj,
                image=ContentFile(self._build_image(spec), name=f'demo_{property_obj.id}.png'),
                caption='Foto de demostración',
            )

        has_corretaje = Document.objects.current().filter(
            property=property_obj, doc_type=Document.DocType.CORRETAJE,
        ).exists()
        if 'brokerage_contract' in spec['requirements'] and not has_corretaje:
            today = timezone.localdate()
            Document.upload_new_version(
                property=property_obj,
                doc_type=Document.DocType.CORRETAJE,
                file=ContentFile(DEMO_PDF, name='corretaje_demo.pdf'),
                uploaded_by=agent,
                issue_date=today,
                expiration_date=today + timedelta(days=365),
                is_critical=True,
                mime_type='application/pdf',
            )

        if 'appraisal' in spec['requirements']:
            self._ensure_approved_appraisal(property_obj, agent)

        return property_obj

    def _ensure_approved_appraisal(self, property_obj, agent):
        appraisals = Appraisal.objects.filter(property=property_obj)
        if appraisals.approved().exists():
            return
        if appraisals.filter(status=Appraisal.Status.BORRADOR).exists():
            # No se aprueba un borrador que alguien empezo a calibrar en I-12.
            self.stdout.write(self.style.WARNING(
                f'  #{property_obj.id}: tiene un avalúo en borrador; no se aprueba automaticamente.'
            ))
            return
        # Sin motor (D-04): registro manual, sin valor sugerido (DS-02).
        appraisal = Appraisal.create_draft(property=property_obj, agent=agent)
        appraisal.calibrate(
            calibrated_value=property_obj.price,
            final_justification='Avalúo de demostración generado por setup_demo_data (DT-14).',
        )
        appraisal.approve()

    def _build_image(self, spec):
        image = Image.new('RGB', (800, 600), spec['color'])
        draw = ImageDraw.Draw(image)
        draw.text((40, 40), 'URBANEX DEMO', fill=(255, 255, 255))
        draw.text((40, 70), spec['location'], fill=(255, 255, 255))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
