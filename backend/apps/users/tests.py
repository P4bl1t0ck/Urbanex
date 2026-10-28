import io
import os
import shutil
import tempfile
from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.appraisals.models import Appraisal
from apps.documents.models import Document
from apps.users.models import Property, PropertyImage
from apps.users.views import get_missing_publication_requirements
# Create your tests here.
User = get_user_model()

class UrbanexCoreTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Usuario Asesor para pruebas
        # User hereda de AbstractUser: username es obligatorio en create_user()
        self.agent = User.objects.create_user(
            username="asesor.test",
            email="asesor.test@urbanex.ec",
            password="Password123!",
            role="asesor"
        )
        
        # Usuario Cliente público para pruebas
        self.client_user = User.objects.create_user(
            username="cliente.test",
            email="cliente.test@urbanex.ec",
            password="Password123!",
            role="cliente"
        )
#El usuario y la contraseña definidas en una clase que usaremos en la prueba.

# TEST 1: Creación de propiedad por un asesor y estado inicial 'captacion'
    def test_create_property_as_agent(self):
        self.client.force_authenticate(user=self.agent)
        data = {
            "title": "Departamento de Prueba",
            "description": "Prueba unitaria de creación",
            "property_type": "departamento",
            "price": "100000.00",
            "area_m2": 75.5,
            "location": "Quito Norte"
        }
        response = self.client.post("/api/auth/properties/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "captacion")
        self.assertEqual(response.data["agent"], self.agent.id)

    # TEST 2: Publicación (HU-53): permisos + requisitos completos -> 'disponible'
    def test_publish_property_permission(self):
        property_obj = self._create_property("captacion")
        self._add_image(property_obj)
        self._add_corretaje(property_obj)  # PENDIENTE de validación: sí permite publicar
        self._add_approved_appraisal(property_obj)

        # Otro usuario (no dueño ni admin) no puede publicar
        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(f"/api/auth/properties/{property_obj.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.agent)
        response = self.client.post(f"/api/auth/properties/{property_obj.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        property_obj.refresh_from_db()
        self.assertEqual(property_obj.status, "disponible")

    # TEST DT-07: el catálogo público no expone propiedades en captación
    def _create_property(self, status_value):
        return Property.objects.create(
            agent=self.agent,
            title=f"Propiedad {status_value}",
            description="Catálogo público",
            property_type="casa",
            price=150000,
            area_m2=120,
            location="Cumbayá",
            status=status_value,
        )

    def test_anonymous_list_only_shows_public_statuses(self):
        captacion = self._create_property("captacion")
        disponible = self._create_property("disponible")
        reservado = self._create_property("reservador")  # errata DT-16
        vendido = self._create_property("vendido")

        response = self.client.get("/api/auth/properties/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data}
        self.assertEqual(ids, {disponible.id, reservado.id})
        self.assertNotIn(captacion.id, ids)
        self.assertNotIn(vendido.id, ids)

    def test_anonymous_cannot_read_captacion_detail(self):
        captacion = self._create_property("captacion")
        disponible = self._create_property("disponible")

        response = self.client.get(f"/api/auth/properties/{captacion.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(f"/api/auth/properties/{disponible.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_still_reads_captacion_detail(self):
        captacion = self._create_property("captacion")
        self.client.force_authenticate(user=self.agent)
        response = self.client.get(f"/api/auth/properties/{captacion.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # TEST DT-09: status no se cambia por POST/PATCH genéricos (solo por HU-53)
    def test_patch_cannot_change_status(self):
        property_obj = self._create_property("captacion")
        self.client.force_authenticate(user=self.agent)
        response = self.client.patch(
            f"/api/auth/properties/{property_obj.id}/", {"status": "disponible"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        property_obj.refresh_from_db()
        self.assertEqual(property_obj.status, "captacion")

    def test_create_ignores_status(self):
        self.client.force_authenticate(user=self.agent)
        data = {
            "title": "Intento de publicar al crear",
            "description": "DT-09",
            "property_type": "casa",
            "price": "120000.00",
            "area_m2": 90,
            "location": "Quito",
            "status": "disponible",
        }
        response = self.client.post("/api/auth/properties/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "captacion")
        self.assertEqual(Property.objects.get(pk=response.data["id"]).status, "captacion")

    # TEST HU-53 / DT-08: la publicación se rechaza si falta algún requisito
    def _add_image(self, property_obj):
        # Solo la ruta: la prueba no necesita escribir el archivo en media/
        return PropertyImage.objects.create(property=property_obj, image="properties/images/test.jpg")

    def _add_corretaje(self, property_obj, **overrides):
        if not hasattr(self, "_tmp_storage_dir"):
            # Los documentos de prueba van a una carpeta temporal, no a private_media/
            self._tmp_storage_dir = tempfile.mkdtemp()
            patcher = mock.patch.object(
                Document._meta.get_field("file"), "storage",
                FileSystemStorage(location=self._tmp_storage_dir),
            )
            patcher.start()
            self.addCleanup(patcher.stop)
            self.addCleanup(shutil.rmtree, self._tmp_storage_dir, ignore_errors=True)
        data = {
            "property": property_obj,
            "doc_type": Document.DocType.CORRETAJE,
            "file": SimpleUploadedFile("corretaje.pdf", b"%PDF" + b"0" * 64, content_type="application/pdf"),
            "uploaded_by": self.agent,
            "issue_date": timezone.localdate(),
            "expiration_date": timezone.localdate() + timedelta(days=365),
        }
        data.update(overrides)
        return Document.upload_new_version(**data)

    def _add_approved_appraisal(self, property_obj):
        appraisal = Appraisal.create_draft(property=property_obj, agent=self.agent)
        appraisal.calibrate(calibrated_value=Decimal("150000.00"), final_justification="Valor de mercado.")
        return appraisal.approve()

    def _publish_and_expect_rejection(self, property_obj, expected_code):
        self.client.force_authenticate(user=self.agent)
        response = self.client.post(f"/api/auth/properties/{property_obj.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        codes = [item["code"] for item in response.data["missing_requirements"]]
        self.assertEqual(codes, [expected_code])
        self.assertIn("detail", response.data)
        property_obj.refresh_from_db()
        self.assertEqual(property_obj.status, "captacion")

    def test_publish_rejected_without_image(self):
        property_obj = self._create_property("captacion")
        self._add_corretaje(property_obj)
        self._add_approved_appraisal(property_obj)
        self._publish_and_expect_rejection(property_obj, "image")

    def test_publish_rejected_without_corretaje(self):
        property_obj = self._create_property("captacion")
        self._add_image(property_obj)
        self._add_approved_appraisal(property_obj)
        self._publish_and_expect_rejection(property_obj, "brokerage_contract")

    def test_publish_rejected_with_expired_corretaje(self):
        property_obj = self._create_property("captacion")
        self._add_image(property_obj)
        today = timezone.localdate()
        self._add_corretaje(property_obj, issue_date=today - timedelta(days=400),
                            expiration_date=today - timedelta(days=1))
        self._add_approved_appraisal(property_obj)
        self._publish_and_expect_rejection(property_obj, "brokerage_contract")

    def test_publish_rejected_with_rejected_corretaje(self):
        property_obj = self._create_property("captacion")
        self._add_image(property_obj)
        document = self._add_corretaje(property_obj)
        admin = User.objects.create_user(username="admin.test", email="admin.test@urbanex.ec",
                                         password="Password123!", role="admin")
        document.validate_document(admin=admin, approved=False, reason="Firma ilegible.")
        self._add_approved_appraisal(property_obj)
        self._publish_and_expect_rejection(property_obj, "brokerage_contract")

    def test_publish_rejected_with_draft_appraisal_only(self):
        property_obj = self._create_property("captacion")
        self._add_image(property_obj)
        self._add_corretaje(property_obj)
        Appraisal.create_draft(property=property_obj, agent=self.agent)
        self._publish_and_expect_rejection(property_obj, "appraisal")

    def test_publish_rejected_lists_all_missing_requirements(self):
        property_obj = self._create_property("captacion")
        self.client.force_authenticate(user=self.agent)
        response = self.client.post(f"/api/auth/properties/{property_obj.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        codes = [item["code"] for item in response.data["missing_requirements"]]
        self.assertEqual(codes, ["image", "brokerage_contract", "appraisal"])

    def test_publish_only_from_captacion(self):
        property_obj = self._create_property("disponible")
        self.client.force_authenticate(user=self.agent)
        response = self.client.post(f"/api/auth/properties/{property_obj.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    # TEST DS-15: requisitos de publicación sin intentar publicar (pestaña Expediente)
    def _get_requirements(self, property_obj, user):
        self.client.force_authenticate(user=user)
        return self.client.get(f"/api/auth/properties/{property_obj.id}/publication-requirements/")

    def test_requirements_list_everything_missing(self):
        property_obj = self._create_property("captacion")
        response = self._get_requirements(property_obj, self.agent)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["can_publish"])
        codes = [item["code"] for item in response.data["missing_requirements"]]
        self.assertEqual(codes, ["image", "brokerage_contract", "appraisal"])
        # Consultar no cambia el estado
        property_obj.refresh_from_db()
        self.assertEqual(property_obj.status, "captacion")

    def test_requirements_complete_allows_publishing(self):
        property_obj = self._create_property("captacion")
        self._add_image(property_obj)
        self._add_corretaje(property_obj)
        self._add_approved_appraisal(property_obj)
        response = self._get_requirements(property_obj, self.agent)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["can_publish"])
        self.assertEqual(response.data["missing_requirements"], [])

    def test_requirements_match_publish_rejection(self):
        # El Expediente muestra exactamente lo mismo que respondería el 400 de publicar
        property_obj = self._create_property("captacion")
        self._add_image(property_obj)
        requirements = self._get_requirements(property_obj, self.agent).data["missing_requirements"]
        publish = self.client.post(f"/api/auth/properties/{property_obj.id}/publish/")
        self.assertEqual(publish.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(requirements, publish.data["missing_requirements"])

    def test_requirements_cannot_publish_outside_captacion(self):
        property_obj = self._create_property("disponible")
        self._add_image(property_obj)
        self._add_corretaje(property_obj)
        self._add_approved_appraisal(property_obj)
        response = self._get_requirements(property_obj, self.agent)
        self.assertEqual(response.data["status"], "disponible")
        self.assertFalse(response.data["can_publish"])

    def test_requirements_forbidden_for_non_owner(self):
        property_obj = self._create_property("captacion")
        response = self._get_requirements(property_obj, self.client_user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_requirements_require_authentication(self):
        property_obj = self._create_property("captacion")
        response = self.client.get(f"/api/auth/properties/{property_obj.id}/publication-requirements/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # TEST 3: Rechazo de autenticación con credenciales erróneas
    def test_login_failed_with_invalid_credentials(self):
        data = {
            "email": "asesor.test@urbanex.ec",
            "password": "PasswordIncorrecta"
        }
        response = self.client.post("/api/auth/login/", data, format="json")
        # LoginView responde 401 (no autenticado) y suma el intento fallido (RF-13)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.agent.refresh_from_db()
        self.assertEqual(self.agent.failed_attempts, 1)


# DT-14 / DS-17: comando setup_demo_data
DEMO_PASSWORD = "Demo-Urbanex-2026!"


class SetupDemoDataCommandTests(TestCase):
    def setUp(self):
        # Fotos y documentos van a carpetas temporales, no a media/ ni a private_media/
        media_dir = tempfile.mkdtemp()
        private_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media_dir, ignore_errors=True)
        self.addCleanup(shutil.rmtree, private_dir, ignore_errors=True)
        # El runner de pruebas fuerza DEBUG=False; el comando solo corre en desarrollo
        settings_override = override_settings(DEBUG=True, MEDIA_ROOT=media_dir)
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        patcher = mock.patch.object(
            Document._meta.get_field("file"), "storage",
            FileSystemStorage(location=private_dir),
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def _run(self, password=DEMO_PASSWORD):
        with mock.patch.dict(os.environ, {"DEMO_PASSWORD": password}):
            call_command("setup_demo_data", stdout=io.StringIO())

    def _missing_codes(self, title_fragment):
        property_obj = Property.objects.get(title__contains=title_fragment)
        return {item["code"] for item in get_missing_publication_requirements(property_obj)}

    def test_requires_demo_password(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CommandError):
                call_command("setup_demo_data", stdout=io.StringIO())
        self.assertFalse(User.objects.filter(email__endswith="@urbanex.test").exists())

    def test_refuses_to_run_without_debug(self):
        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError):
                self._run()
        self.assertFalse(Property.objects.exists())

    def test_creates_users_with_roles_and_password(self):
        self._run()
        admin = User.objects.get(email="admin.demo@urbanex.test")
        agent = User.objects.get(email="asesor.demo@urbanex.test")
        self.assertEqual(admin.role, "admin")
        self.assertTrue(admin.is_staff)
        self.assertFalse(admin.is_superuser)
        self.assertEqual(agent.role, "asesor")
        self.assertFalse(agent.is_staff)
        self.assertTrue(admin.check_password(DEMO_PASSWORD))
        self.assertTrue(agent.check_password(DEMO_PASSWORD))

    def test_properties_start_in_captacion_with_expected_requirements(self):
        self._run()
        agent = User.objects.get(email="asesor.demo@urbanex.test")
        properties = Property.objects.filter(agent=agent)
        self.assertEqual(properties.count(), 4)
        self.assertFalse(properties.exclude(status="captacion").exists())
        self.assertEqual(self._missing_codes("Cumbayá"), set())
        self.assertEqual(self._missing_codes("La Carolina"), {"appraisal"})
        self.assertEqual(self._missing_codes("La Mariscal"), {"brokerage_contract"})
        self.assertEqual(self._missing_codes("Tumbaco"), {"image", "brokerage_contract", "appraisal"})
        # Sin motor (DS-02): el avalúo demo no inventa un valor sugerido
        appraisal = Appraisal.objects.approved().get(property__title__contains="Cumbayá")
        self.assertIsNone(appraisal.suggested_value)

    def test_rerun_is_idempotent_and_updates_password(self):
        self._run()
        counts = (User.objects.count(), Property.objects.count(), PropertyImage.objects.count(),
                  Document.objects.count(), Appraisal.objects.count())
        self._run(password="Otra-Clave-Demo-2026!")
        self.assertEqual(
            counts,
            (User.objects.count(), Property.objects.count(), PropertyImage.objects.count(),
             Document.objects.count(), Appraisal.objects.count()),
        )
        agent = User.objects.get(email="asesor.demo@urbanex.test")
        self.assertTrue(agent.check_password("Otra-Clave-Demo-2026!"))

    def test_open_draft_is_not_approved_on_rerun(self):
        self._run()
        agent = User.objects.get(email="asesor.demo@urbanex.test")
        # El asesor empezó una reevaluación en I-12: el comando no debe aprobarla
        draft = Appraisal.create_draft(
            property=Property.objects.get(title__contains="Cumbayá"), agent=agent,
        )
        self._run()
        draft.refresh_from_db()
        self.assertEqual(draft.status, Appraisal.Status.BORRADOR)