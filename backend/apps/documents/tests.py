import shutil
import tempfile
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.users.models import Property
from .models import Document

User = get_user_model()


def pdf(name='contrato.pdf', size=1024):
    return SimpleUploadedFile(name, b'%PDF' + b'0' * size, content_type='application/pdf')


class DocumentModelTests(TestCase):
    def setUp(self):
        # Los archivos de prueba van a una carpeta temporal, no a private_media/
        self.tmp_dir = tempfile.mkdtemp()
        patcher = mock.patch.object(
            Document._meta.get_field('file'), 'storage', FileSystemStorage(location=self.tmp_dir)
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(shutil.rmtree, self.tmp_dir, ignore_errors=True)

        self.asesor = User.objects.create_user(username='asesor', email='a@urbanex.ec',
                                               password='x', role='asesor')
        self.admin = User.objects.create_user(username='admin', email='ad@urbanex.ec',
                                              password='x', role='admin')
        self.property = Property.objects.create(
            title='Depto La Carolina', description='-', price=100000, area_m2=80,
            location='La Carolina', agent=self.asesor,
        )

    def upload(self, **overrides):
        data = {
            'property': self.property,
            'doc_type': Document.DocType.CORRETAJE,
            'file': pdf(),
            'uploaded_by': self.asesor,
            'issue_date': timezone.localdate(),
            'expiration_date': timezone.localdate() + timedelta(days=365),
            'is_critical': True,
        }
        data.update(overrides)
        return Document.upload_new_version(**data)

    def test_new_upload_creates_next_version_and_retires_previous(self):
        first = self.upload()
        second = self.upload()

        first.refresh_from_db()
        self.assertEqual((first.version, first.is_current_version), (1, False))
        self.assertEqual((second.version, second.is_current_version), (2, True))
        self.assertEqual(Document.objects.filter(property=self.property).count(), 2)

    def test_versions_are_counted_per_doc_type(self):
        self.upload()
        escritura = self.upload(doc_type=Document.DocType.ESCRITURA)
        self.assertEqual(escritura.version, 1)

    def test_documents_cannot_be_deleted(self):
        document = self.upload()
        with self.assertRaises(ValidationError):
            document.delete()
        with self.assertRaises(ValidationError):
            Document.objects.all().delete()
        self.assertTrue(Document.objects.filter(pk=document.pk).exists())

    def test_file_and_metadata_are_immutable(self):
        document = self.upload()
        document.expiration_date = timezone.localdate() + timedelta(days=999)
        with self.assertRaises(ValidationError):
            document.save()
        with self.assertRaises(ValidationError):
            Document.objects.filter(pk=document.pk).update(version=99)

    def test_rejects_files_over_20mb_and_invalid_types(self):
        with self.assertRaises(ValidationError):
            self.upload(file=pdf(size=20 * 1024 * 1024 + 1))
        with self.assertRaises(ValidationError):
            self.upload(file=SimpleUploadedFile('x.docx', b'abc', content_type='application/msword'))
        self.assertFalse(Document.objects.exists())

    def test_failed_upload_keeps_previous_version_current(self):
        first = self.upload()
        with self.assertRaises(ValidationError):
            self.upload(expiration_date=timezone.localdate() - timedelta(days=1))
        first.refresh_from_db()
        self.assertTrue(first.is_current_version)

    def test_only_admin_can_validate(self):
        document = self.upload()
        with self.assertRaises(ValidationError):
            document.validate_document(admin=self.asesor, approved=True)

        document.validate_document(admin=self.admin, approved=True)
        document.refresh_from_db()
        self.assertEqual(document.validation_status, Document.ValidationStatus.APROBADO)
        self.assertEqual(document.validated_by, self.admin)
        self.assertIsNotNone(document.validated_at)

    def test_rejection_requires_reason(self):
        document = self.upload()
        with self.assertRaises(ValidationError):
            document.validate_document(admin=self.admin, approved=False, reason='  ')
        document.validate_document(admin=self.admin, approved=False, reason='Firma ilegible')
        document.refresh_from_db()
        self.assertEqual(document.validation_status, Document.ValidationStatus.RECHAZADO)

    def test_old_versions_cannot_be_validated(self):
        first = self.upload()
        self.upload()
        first.refresh_from_db()
        with self.assertRaises(ValidationError):
            first.validate_document(admin=self.admin, approved=True)

    def test_expiring_soon_uses_30_day_window(self):
        soon = self.upload(expiration_date=timezone.localdate() + timedelta(days=30))
        self.upload(doc_type=Document.DocType.ESCRITURA,
                    expiration_date=timezone.localdate() + timedelta(days=31))
        self.assertTrue(soon.is_expiring_soon)
        self.assertEqual(list(Document.objects.expiring_soon()), [soon])


class DocumentApiTests(TestCase):
    '''HU-03: carga y consulta del expediente vía API, con permisos por propiedad.'''

    def setUp(self):
        from rest_framework.test import APIClient

        self.tmp_dir = tempfile.mkdtemp()
        patcher = mock.patch.object(
            Document._meta.get_field('file'), 'storage', FileSystemStorage(location=self.tmp_dir)
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(shutil.rmtree, self.tmp_dir, ignore_errors=True)

        self.owner = User.objects.create_user(username='owner', email='o@urbanex.ec',
                                              password='x', role='asesor')
        self.other = User.objects.create_user(username='other', email='x@urbanex.ec',
                                              password='x', role='asesor')
        self.admin = User.objects.create_user(username='boss', email='b@urbanex.ec',
                                              password='x', role='admin')
        self.property = Property.objects.create(
            title='Casa Cumbayá', description='-', price=200000, area_m2=150,
            location='Cumbayá', agent=self.owner,
        )
        self.client = APIClient()
        self.url = '/api/documents/'

    def payload(self, **overrides):
        today = timezone.localdate()
        data = {
            'property': self.property.id,
            'doc_type': 'CORRETAJE',
            'file': pdf(),
            'issue_date': today.isoformat(),
            'expiration_date': (today + timedelta(days=365)).isoformat(),
            'is_critical': 'true',
        }
        data.update(overrides)
        return data

    def test_requires_authentication(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)

    def test_owner_uploads_and_new_upload_creates_version_2(self):
        self.client.force_authenticate(self.owner)
        first = self.client.post(self.url, self.payload(), format='multipart')
        second = self.client.post(self.url, self.payload(), format='multipart')

        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(second.data['version'], 2)
        self.assertEqual(second.data['mime_type'], 'application/pdf')
        self.assertEqual(second.data['validation_status'], 'PENDIENTE')
        self.assertNotIn('file', second.data)  # La ruta privada nunca se expone

        listed = self.client.get(self.url, {'property': self.property.id})
        self.assertEqual([d['version'] for d in listed.data], [2])
        all_versions = self.client.get(self.url, {'property': self.property.id, 'all_versions': '1'})
        self.assertEqual(len(all_versions.data), 2)

    def test_other_agent_cannot_upload_or_see_documents(self):
        self.client.force_authenticate(self.owner)
        doc_id = self.client.post(self.url, self.payload(), format='multipart').data['id']

        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.post(self.url, self.payload(), format='multipart').status_code, 400)
        self.assertEqual(self.client.get(self.url).data, [])
        self.assertEqual(self.client.get(f'{self.url}{doc_id}/').status_code, 404)
        self.assertEqual(self.client.get(f'{self.url}{doc_id}/file/').status_code, 404)

    def test_admin_can_access_any_expediente(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, self.payload(), format='multipart')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(len(self.client.get(self.url).data), 1)

    def test_rejects_spoofed_content_type(self):
        self.client.force_authenticate(self.owner)
        fake = SimpleUploadedFile('virus.pdf', b'MZ\x90\x00 not a pdf', content_type='application/pdf')
        response = self.client.post(self.url, self.payload(file=fake), format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('file', response.data)

    def test_rejects_file_over_20mb(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.url, self.payload(file=pdf(size=20 * 1024 * 1024 + 1)),
                                    format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('file', response.data)

    def test_rejects_expiration_before_issue(self):
        self.client.force_authenticate(self.owner)
        today = timezone.localdate()
        response = self.client.post(self.url, self.payload(
            issue_date=today.isoformat(),
            expiration_date=(today - timedelta(days=1)).isoformat(),
        ), format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('expiration_date', response.data)

    def test_documents_cannot_be_updated_or_deleted_via_api(self):
        self.client.force_authenticate(self.owner)
        doc_id = self.client.post(self.url, self.payload(), format='multipart').data['id']
        self.assertEqual(self.client.patch(f'{self.url}{doc_id}/', {'version': 9}).status_code, 405)
        self.assertEqual(self.client.delete(f'{self.url}{doc_id}/').status_code, 405)

    def test_owner_can_download_file(self):
        self.client.force_authenticate(self.owner)
        doc_id = self.client.post(self.url, self.payload(), format='multipart').data['id']
        response = self.client.get(f'{self.url}{doc_id}/file/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b''.join(response.streaming_content).startswith(b'%PDF'))
        response.close()
