import hashlib
import importlib
import io
import os
import shutil
import tempfile
from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest import mock
from resend.exceptions import ResendError

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.apps import apps as django_apps
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.utils import timezone
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status
from apps.appraisals.models import Appraisal
from apps.documents.models import Document
from apps.users.models import Property, PropertyImage, UserActivationToken
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
            role="asesor"
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

    def test_login_accepts_email_with_different_casing(self):
        self.agent.set_password("Login-test-2026!")
        self.agent.save(update_fields=["password"])

        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "  ASESOR.TEST@URBANEX.EC  ",
                "password": "Login-test-2026!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_locks_account_after_five_failed_attempts(self):
        for _ in range(5):
            response = self.client.post(
                "/api/auth/login/",
                {
                    "email": self.agent.email,
                    "password": "PasswordIncorrecta",
                },
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.agent.refresh_from_db()
        self.assertEqual(self.agent.failed_attempts, 5)
        self.assertTrue(self.agent.is_locked)

        response = self.client.post(
            "/api/auth/login/",
            {"email": self.agent.email, "password": "AnyPassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def _run(self, password=DEMO_PASSWORD, *, stdout=None):
        with mock.patch.dict(os.environ, {"DEMO_PASSWORD": password}):
            call_command("setup_demo_data", stdout=stdout or io.StringIO())

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
        # El seeder usa el flujo manual y no fija un valor sugerido del motor.
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

    def test_rerun_does_not_reactivate_deactivated_demo_agent(self):
        self._run()
        agent = User.objects.get(email="asesor.demo@urbanex.test")
        agent.is_active = False
        agent.deactivation_reason = "Fin de prueba"
        agent.is_locked = True
        agent.failed_attempts = 4
        agent.save(
            update_fields=[
                "is_active",
                "deactivation_reason",
                "is_locked",
                "failed_attempts",
            ]
        )

        output = io.StringIO()
        self._run(stdout=output)

        agent.refresh_from_db()
        self.assertFalse(agent.is_active)
        self.assertEqual(agent.deactivation_reason, "Fin de prueba")
        self.assertTrue(agent.is_locked)
        self.assertEqual(agent.failed_attempts, 4)
        self.assertIn("sigue inactivo", output.getvalue())

@override_settings(EMAIL_PROVIDER="console")
class UserManagementApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="manager.test",
            email="manager@urbanex.test",
            password="Admin-test-2026!",
            role="admin",
            is_staff=True,
        )
        self.advisor = User.objects.create_user(
            username="advisor.test",
            email="advisor@urbanex.test",
            password="Advisor-test-2026!",
            role="asesor",
        )

    def create_property_for_advisor(self):
        return Property.objects.create(
            agent=self.advisor,
            title="Propiedad del asesor",
            description="Registro de prueba",
            property_type="casa",
            price=150000,
            area_m2=120,
            location="Quito",
        )

    def test_django_superuser_is_also_an_application_admin(self):
        superuser = User.objects.create_superuser(
            username="root.test",
            email="root@urbanex.test",
            password="Secure-Root-2026!",
        )

        User.objects.filter(pk=superuser.pk).update(role="cliente")
        legacy_advisor = User.objects.create_user(
            username="legacy.client",
            email="legacy.client@urbanex.test",
            password="test-password-for-migration",
            role="asesor",
        )
        User.objects.filter(pk=legacy_advisor.pk).update(role="cliente")

        migration = importlib.import_module(
            "apps.users.migrations."
            "0007_user_deactivation_reason_user_phone_alter_user_email_and_more"
        )
        migration.migrate_legacy_roles(
            django_apps,
            SimpleNamespace(connection=connection),
        )

        self.assertTrue(superuser.is_superuser)
        superuser.refresh_from_db()
        self.assertEqual(superuser.role, "admin")
        self.assertTrue(superuser.is_active)
        legacy_advisor.refresh_from_db()
        self.assertEqual(legacy_advisor.role, "asesor")
        self.assertFalse(legacy_advisor.is_active)
        self.assertEqual(
            legacy_advisor.deactivation_reason,
            "rol cliente eliminado (C-08)",
        )

    def test_only_admin_can_list_users(self):
        response = self.client.get("/api/auth/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.advisor)
        response = self.client.get("/api/auth/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_users_without_password_data(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get("/api/auth/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertNotIn("password", response.data[0])

    def test_admin_creates_inactive_user_and_sends_activation_email(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/auth/users/",
            {
                "email": "new.advisor@urbanex.test",
                "first_name": "Nuevo",
                "last_name": "Asesor",
                "phone": "0991234567",
                "role": "asesor",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(email="new.advisor@urbanex.test")
        self.assertFalse(created_user.is_active)
        self.assertFalse(created_user.has_usable_password())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("activate", mail.outbox[0].body)

    def test_admin_normalizes_local_ecuadorian_mobile_phone(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/auth/users/",
            {
                "email": "formatted.phone@urbanex.test",
                "phone": "(09) 9123-4567",
                "role": "asesor",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["phone"], "0991234567")
        self.assertEqual(
            User.objects.get(email="formatted.phone@urbanex.test").phone,
            "0991234567",
        )

    def test_admin_rejects_non_local_or_invalid_phone_numbers(self):
        self.client.force_authenticate(user=self.admin)

        for index, phone in enumerate(
            ("1234567890", "09912345ab", "+593991234567", "09912345678")
        ):
            with self.subTest(phone=phone):
                response = self.client.post(
                    "/api/auth/users/",
                    {
                        "email": f"invalid.phone.{index}@urbanex.test",
                        "phone": phone,
                        "role": "asesor",
                    },
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("phone", response.data)

    def test_admin_creation_normalizes_email(self):
        self.client.force_authenticate(user=self.admin)

        with self.settings(EMAIL_PROVIDER="console"):
            response = self.client.post(
                "/api/auth/users/",
                {
                    "email": "  New.Advisor@Urbanex.Test  ",
                    "first_name": "Nuevo",
                    "role": "asesor",
                },
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "new.advisor@urbanex.test")
        self.assertTrue(
            User.objects.filter(email="new.advisor@urbanex.test").exists()
        )

    def test_admin_can_send_activation_email_with_resend(self):
        self.client.force_authenticate(user=self.admin)

        with (
            self.settings(
                EMAIL_PROVIDER="resend",
                RESEND_API_KEY="re_test_key",
                DEFAULT_FROM_EMAIL="Urbanex <no-reply@urbanex.test>",
            ),
            mock.patch("apps.users.serializers.resend.Emails.send") as send_email,
        ):
            response = self.client.post(
                "/api/auth/users/",
                {
                    "email": "resend.advisor@urbanex.test",
                    "first_name": "Nuevo",
                    "role": "asesor",
                },
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        params = send_email.call_args.args[0]
        self.assertEqual(params["from"], "Urbanex <no-reply@urbanex.test>")
        self.assertEqual(params["to"], ["resend.advisor@urbanex.test"])
        self.assertEqual(params["subject"], "Activa tu cuenta de Urbanex")
        self.assertIn("/activate#", params["text"])

    def test_resend_failure_returns_gateway_error_and_rolls_back_user_creation(self):
        self.client.force_authenticate(user=self.admin)

        with (
            self.settings(
                EMAIL_PROVIDER="resend",
                RESEND_API_KEY="re_test_key",
                DEFAULT_FROM_EMAIL="Urbanex <no-reply@urbanex.test>",
            ),
            mock.patch(
                "apps.users.serializers.resend.Emails.send",
                side_effect=ResendError(
                    403,
                    "validation_error",
                    "The domain is not verified.",
                    "Verify the sending domain.",
                ),
            ),
        ):
            response = self.client.post(
                "/api/auth/users/",
                {"email": "rejected@urbanex.test", "role": "asesor"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("No se pudo enviar", response.data["detail"])
        self.assertFalse(User.objects.filter(email="rejected@urbanex.test").exists())

    def test_admin_rejects_duplicate_email(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/auth/users/",
            {"email": self.advisor.email, "role": "asesor"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.filter(email=self.advisor.email).count(), 1)

    def test_admin_rejects_duplicate_email_with_different_casing(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/auth/users/",
            {"email": "  ADVISOR@URBANEX.TEST  ", "role": "asesor"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            User.objects.filter(email__iexact=self.advisor.email).count(), 1
        )

    def test_admin_cannot_create_client_role(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/auth/users/",
            {"email": "client@urbanex.test", "role": "cliente"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="client@urbanex.test").exists())

    def test_user_delete_endpoint_is_not_available(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(f"/api/auth/users/{self.advisor.pk}/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(User.objects.filter(pk=self.advisor.pk).exists())
        self.advisor.refresh_from_db()
        self.assertTrue(self.advisor.is_active)

    def test_admin_edits_only_allowed_profile_fields(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/api/auth/users/{self.advisor.pk}/",
            {
                "first_name": "Nombre actualizado",
                "last_name": "Apellido actualizado",
                "phone": "0987654321",
                "role": "admin",
                "email": "changed@urbanex.test",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.advisor.refresh_from_db()
        self.assertEqual(self.advisor.email, "advisor@urbanex.test")

        response = self.client.patch(
            f"/api/auth/users/{self.advisor.pk}/",
            {
                "first_name": "Nombre actualizado",
                "last_name": "Apellido actualizado",
                "phone": "0987654321",
                "role": "admin",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.advisor.refresh_from_db()
        self.assertEqual(self.advisor.first_name, "Nombre actualizado")
        self.assertEqual(self.advisor.last_name, "Apellido actualizado")
        self.assertEqual(self.advisor.phone, "0987654321")
        self.assertEqual(self.advisor.role, "admin")

    def test_last_active_admin_cannot_be_demoted(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/api/auth/users/{self.admin.pk}/",
            {"role": "asesor"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.role, "admin")

    def test_admin_cannot_deactivate_self(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/auth/users/{self.admin.pk}/deactivate/",
            {"reason": "Prueba"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_deactivation_keeps_user_and_unassigns_properties(self):
        property_obj = self.create_property_for_advisor()
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/auth/users/{self.advisor.pk}/deactivate/",
            {"reason": "Fin de pruebas del asesor."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.advisor.refresh_from_db()
        property_obj.refresh_from_db()
        self.assertFalse(self.advisor.is_active)
        self.assertEqual(self.advisor.deactivation_reason, "Fin de pruebas del asesor.")
        self.assertIsNone(property_obj.agent_id)
        self.assertTrue(User.objects.filter(pk=self.advisor.pk).exists())

    def test_deactivation_requires_reason(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/auth/users/{self.advisor.pk}/deactivate/",
            {"reason": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.advisor.refresh_from_db()
        self.assertTrue(self.advisor.is_active)

    def test_activation_token_is_one_time_and_expires_after_24_hours(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post(
            "/api/auth/users/",
            {
                "email": "activation@urbanex.test",
                "first_name": "Activar",
                "last_name": "Cuenta",
                "role": "asesor",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        activation_token = mail.outbox[-1].body.rsplit("#", 1)[1].strip()
        self.assertIn(f"/activate#{activation_token}", mail.outbox[-1].body)

        self.client.force_authenticate(user=None)
        response = self.client.post(
            "/api/auth/users/activate/",
            {"token": activation_token, "password": "Safe-Pass-2026!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        activated_user = User.objects.get(email="activation@urbanex.test")
        self.assertTrue(activated_user.is_active)
        self.assertTrue(activated_user.check_password("Safe-Pass-2026!"))

        repeated_response = self.client.post(
            "/api/auth/users/activate/",
            {"token": activation_token, "password": "Another-Safe-2026!"},
            format="json",
        )
        self.assertEqual(repeated_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_activation_token_is_rejected(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post(
            "/api/auth/users/",
            {"email": "expired@urbanex.test", "role": "asesor"},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        activation_token = mail.outbox[-1].body.rsplit("#", 1)[1].strip()
        token_hash = hashlib.sha256(activation_token.encode("utf-8")).hexdigest()
        UserActivationToken.objects.filter(token_hash=token_hash).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )

        self.client.force_authenticate(user=None)
        response = self.client.post(
            "/api/auth/users/activate/",
            {"token": activation_token, "password": "Safe-Pass-2026!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.get(email="expired@urbanex.test").is_active)

    def test_admin_can_resend_activation_and_old_token_is_invalidated(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post(
            "/api/auth/users/",
            {"email": "resend@urbanex.test", "role": "asesor"},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="resend@urbanex.test")
        previous_token = mail.outbox[-1].body.rsplit("#", 1)[1].strip()

        response = self.client.post(
            f"/api/auth/users/{user.pk}/resend-activation/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_token = mail.outbox[-1].body.rsplit("#", 1)[1].strip()
        self.assertNotEqual(previous_token, new_token)

        self.client.force_authenticate(user=None)
        old_token_response = self.client.post(
            "/api/auth/users/activate/",
            {"token": previous_token, "password": "Safe-Pass-2026!"},
            format="json",
        )
        self.assertEqual(old_token_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deactivated_user_cannot_be_reactivated_by_resending_activation(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            "/api/auth/users/",
            {"email": "deactivated@urbanex.test", "role": "asesor"},
            format="json",
        )
        user = User.objects.get(email="deactivated@urbanex.test")
        user.deactivation_reason = "Baja administrativa."
        user.save(update_fields=["deactivation_reason"])

        response = self.client.post(
            f"/api/auth/users/{user.pk}/resend-activation/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_inactive_users_cannot_log_in(self):
        self.advisor.is_active = False
        self.advisor.save(update_fields=["is_active"])

        response = self.client.post(
            "/api/auth/login/",
            {"email": self.advisor.email, "password": "Advisor-test-2026!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
