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

from django.conf import settings
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
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from apps.appraisals.models import Appraisal
from apps.documents.models import Document
from apps.users.authentication import PasswordVersionRefreshToken
from apps.users.models import (
    PasswordResetToken,
    Property,
    PropertyImage,
    UserActivationToken,
)
from apps.users.serializers import PropertySerializer
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
        
        # Segundo asesor, no dueño de las propiedades de prueba (C-08: el cliente no tiene cuenta; DT-107)
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
        ids = {item["id"] for item in response.data["results"]}
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
        invalid_credentials_message = None
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
            invalid_credentials_message = response.data["detail"]

        self.agent.refresh_from_db()
        self.assertEqual(self.agent.failed_attempts, 5)
        self.assertTrue(self.agent.is_locked)

        response = self.client.post(
            "/api/auth/login/",
            {"email": self.agent.email, "password": "AnyPassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], invalid_credentials_message)
        self.agent.refresh_from_db()
        self.assertTrue(self.agent.is_locked)
        self.assertEqual(self.agent.failed_attempts, 5)

class PropertyWithdrawalApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.agent = User.objects.create_user(
            username="withdraw.owner", email="withdraw.owner@urbanex.test", password="Safe-Test-2026!", role="asesor",
        )
        cls.other = User.objects.create_user(
            username="withdraw.other", email="withdraw.other@urbanex.test", password="Safe-Test-2026!", role="asesor",
        )
        cls.admin_user = User.objects.create_user(
            username="withdraw.admin", email="withdraw.admin@urbanex.test", password="Safe-Test-2026!", role="admin",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.agent)
        self.property = Property.objects.create(
            title="Withdrawal test", property_type="casa", price="100000.00",
            area_m2=100, location="Quito", status="disponible", agent=self.agent,
        )
        self.url = f"/api/auth/properties/{self.property.pk}/"

    def test_withdraw_requires_reason_and_does_not_change_state_on_error(self):
        for payload in ({}, {"unavailability_reason": ""}, {"unavailability_reason": "   "}, {"unavailability_reason": None}):
            with self.subTest(payload=payload):
                response = self.client.post(self.url + "withdraw/", payload, format="json")
                self.assertEqual(response.status_code, 400, response.data)
                self.property.refresh_from_db()
                self.assertEqual(self.property.status, "disponible")
                self.assertIsNone(self.property.unavailability_reason)

    def test_only_available_or_reserved_can_be_withdrawn(self):
        for initial in ("captacion", "disponible", "reservador", "no_disponible", "vendido", "arrendado"):
            with self.subTest(initial=initial):
                self.property.status = initial
                self.property.save(update_fields=["status"])
                response = self.client.post(self.url + "withdraw/", {"unavailability_reason": "  Owner request  "}, format="json")
                allowed = initial in ("disponible", "reservador")
                self.assertEqual(response.status_code, 200 if allowed else 409, response.data)
                self.property.refresh_from_db()
                self.assertEqual(self.property.status, "no_disponible" if allowed else initial)
                if allowed:
                    self.assertEqual(self.property.unavailability_reason, "Owner request")

    def test_actions_require_owner_or_admin_and_authentication(self):
        for action, initial, payload in (
            ("withdraw", "disponible", {"unavailability_reason": "Owner request"}),
            ("reactivate", "no_disponible", {}),
        ):
            for actor, expected in ((None, 401), (self.other, 403), (self.admin_user, 200)):
                with self.subTest(action=action, actor=actor):
                    self.property.status = initial
                    self.property.save(update_fields=["status"])
                    self.client.force_authenticate(actor)
                    response = self.client.post(self.url + action + "/", payload, format="json")
                    self.assertEqual(response.status_code, expected, response.data)
                    self.property.refresh_from_db()
                    if expected != 200:
                        self.assertEqual(self.property.status, initial)

    def test_reactivation_only_from_unavailable_retains_reason_and_cannot_publish(self):
        for initial in ("captacion", "disponible", "reservador", "no_disponible", "vendido", "arrendado"):
            with self.subTest(initial=initial):
                self.property.status = initial
                self.property.unavailability_reason = "Owner request"
                self.property.save(update_fields=["status", "unavailability_reason"])
                response = self.client.post(self.url + "reactivate/", {"status": "disponible"}, format="json")
                self.assertEqual(response.status_code, 200 if initial == "no_disponible" else 409)
                self.property.refresh_from_db()
                self.assertEqual(self.property.status, "captacion" if initial == "no_disponible" else initial)
                self.assertEqual(self.property.unavailability_reason, "Owner request")

    def test_retirement_hides_catalog_and_reactivation_requires_publication_checks(self):
        anonymous = APIClient()
        self.assertEqual(anonymous.get(self.url).status_code, 200)
        self.assertEqual(self.client.post(self.url + "withdraw/", {"unavailability_reason": "Owner request"}, format="json").status_code, 200)
        self.assertEqual(anonymous.get(self.url).status_code, 404)
        self.assertNotIn(self.property.pk, [item["id"] for item in anonymous.get("/api/auth/properties/").data["results"]])
        self.assertEqual(self.client.post(self.url + "withdraw/", {"unavailability_reason": "Again"}, format="json").status_code, 409)
        self.assertEqual(self.client.post(self.url + "reactivate/", {}, format="json").status_code, 200)
        self.assertEqual(anonymous.get(self.url).status_code, 404)
        self.assertEqual(self.client.post(self.url + "reactivate/", {}, format="json").status_code, 409)
        response = self.client.post(self.url + "publish/", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual({item["code"] for item in response.data["missing_requirements"]}, {"image", "brokerage_contract", "appraisal"})
        self.property.refresh_from_db()
        self.assertEqual(self.property.status, "captacion")

    def test_reactivated_property_can_publish_with_current_requirements(self):
        PropertyImage.objects.create(property=self.property, image="properties/images/test.jpg")
        Document.objects.create(
            property=self.property, doc_type=Document.DocType.CORRETAJE,
            file="synthetic/corretaje.pdf", original_filename="corretaje.pdf",
            file_size_bytes=100, mime_type="application/pdf", uploaded_by=self.agent,
            issue_date=timezone.localdate(), expiration_date=timezone.localdate() + timedelta(days=1),
        )
        appraisal = Appraisal.create_draft(property=self.property, agent=self.agent)
        appraisal.calibrate(calibrated_value=Decimal("150000.00"), final_justification="Synthetic market value.")
        appraisal.approve()
        self.assertEqual(self.client.post(self.url + "withdraw/", {"unavailability_reason": "Owner request"}, format="json").status_code, 200)
        self.assertEqual(self.client.post(self.url + "reactivate/", {}, format="json").status_code, 200)
        response = self.client.post(self.url + "publish/", {}, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.property.refresh_from_db()
        self.assertEqual(self.property.status, "disponible")
        self.assertEqual(self.property.unavailability_reason, "Owner request")
        anonymous = APIClient()
        public_detail = anonymous.get(self.url)
        self.assertEqual(public_detail.status_code, 200)
        self.assertIsNone(public_detail.data["unavailability_reason"])
        public_list = anonymous.get("/api/auth/properties/")
        self.assertEqual(public_list.status_code, 200)
        public_property = next(item for item in public_list.data["results"] if item["id"] == self.property.pk)
        self.assertIsNone(public_property["unavailability_reason"])
        for actor in (self.agent, self.admin_user):
            with self.subTest(actor=actor):
                self.client.force_authenticate(actor)
                detail = self.client.get(self.url)
                self.assertEqual(detail.status_code, 200)
                self.assertEqual(detail.data["unavailability_reason"], "Owner request")

    def test_public_statuses_hide_reason_but_owner_keeps_it_in_lists(self):
        self.property.unavailability_reason = "Synthetic internal reason"
        anonymous = APIClient()
        for initial in ("disponible", "reservador"):
            with self.subTest(initial=initial):
                self.property.status = initial
                self.property.save(update_fields=["status", "unavailability_reason"])
                detail = anonymous.get(self.url)
                self.assertEqual(detail.status_code, 200)
                self.assertIsNone(detail.data["unavailability_reason"])
                public_list = anonymous.get("/api/auth/properties/")
                self.assertEqual(public_list.status_code, 200)
                public_property = next(item for item in public_list.data["results"] if item["id"] == self.property.pk)
                self.assertIsNone(public_property["unavailability_reason"])
                for path in ("/api/auth/properties/", "/api/auth/properties/mine/"):
                    internal_list = self.client.get(path)
                    self.assertEqual(internal_list.status_code, 200)
                    rows = internal_list.data["results"] if path == "/api/auth/properties/" else internal_list.data
                    internal_property = next(item for item in rows if item["id"] == self.property.pk)
                    self.assertEqual(internal_property["unavailability_reason"], "Synthetic internal reason")

    def test_serializer_without_request_hides_reason_without_changing_storage(self):
        self.property.unavailability_reason = "Synthetic internal reason"
        self.property.save(update_fields=["unavailability_reason"])
        self.assertIsNone(PropertySerializer(self.property).data["unavailability_reason"])
        self.property.refresh_from_db()
        self.assertEqual(self.property.unavailability_reason, "Synthetic internal reason")

    def test_patch_edits_published_property_without_changing_status(self):
        for initial in ("disponible", "reservador", "vendido", "arrendado", "no_disponible"):
            self.property.status = initial
            self.property.unavailability_reason = "Owner request"
            self.property.save(update_fields=["status", "unavailability_reason"])
            for forbidden in ("vendido", "arrendado", "disponible"):
                with self.subTest(initial=initial, forbidden=forbidden):
                    response = self.client.patch(self.url, {"title": "Edited title", "price": "120000.00", "status": forbidden}, format="json")
                    self.assertEqual(response.status_code, 200, response.data)
                    self.property.refresh_from_db()
                    self.assertEqual(self.property.status, initial)
                    self.assertEqual(self.property.price, Decimal("120000.00"))
                    self.assertEqual(self.property.title, "Edited title")

    def test_other_agent_cannot_edit_and_missing_property_returns_404(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.patch(self.url, {"price": "120000.00"}, format="json").status_code, 403)
        self.property.refresh_from_db()
        self.assertEqual(self.property.price, Decimal("100000.00"))
        for action in ("withdraw", "reactivate"):
            self.assertEqual(self.client.post(f"/api/auth/properties/999999/{action}/", {}, format="json").status_code, 404)

@override_settings(
    EMAIL_PROVIDER="console",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class PasswordResetAndRefreshApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="password-reset.test",
            email="password-reset@urbanex.test",
            password="Original-Safe-2026!",
            is_active=True,
        )

    def _request_password_reset(self):
        response = self.client.post(
            "/api/auth/password-reset/request/",
            {"email": self.user.email},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        raw_token = (
            mail.outbox[0].body.rsplit("#token=", 1)[1].splitlines()[0].strip()
        )
        return response, raw_token

    def test_password_reset_request_is_neutral_and_stores_only_token_hash(self):
        known_response, raw_token = self._request_password_reset()
        token_record = PasswordResetToken.objects.get(user=self.user)
        self.assertEqual(
            token_record.token_hash,
            hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
            mail.outbox[0].body,
        )
        self.assertNotEqual(token_record.token_hash, raw_token)
        self.assertAlmostEqual(
            (token_record.expires_at - token_record.created_at).total_seconds(),
            timedelta(hours=1).total_seconds(),
            delta=1,
        )
        self.assertIn("60 minutos", mail.outbox[0].body)

        mail.outbox.clear()
        unknown_response = self.client.post(
            "/api/auth/password-reset/request/",
            {"email": "unknown@urbanex.test"},
            format="json",
        )
        self.assertEqual(unknown_response.status_code, known_response.status_code)
        self.assertEqual(unknown_response.data, known_response.data)
        self.assertEqual(mail.outbox, [])

    def test_password_reset_changes_password_and_invalidates_previous_tokens(self):
        old_access = AccessToken.for_user(self.user)
        old_refresh = RefreshToken.for_user(self.user)
        old_issued_at = int((timezone.now() - timedelta(days=1)).timestamp())
        old_access["iat"] = old_issued_at
        old_refresh["iat"] = old_issued_at
        old_password_changed_at = self.user.password_changed_at
        _, raw_token = self._request_password_reset()

        response = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"token": raw_token, "password": "New-Safe-Urbanex-2026!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New-Safe-Urbanex-2026!"))
        self.assertGreater(self.user.password_changed_at, old_password_changed_at)
        self.assertTrue(
            PasswordResetToken.objects.get(user=self.user).is_used
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {old_access}")
        protected_response = self.client.get("/api/auth/users/")
        self.assertEqual(
            protected_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.client.credentials()
        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = str(old_refresh)
        csrf_response = self.client.get("/api/auth/csrf/")
        csrf_token = csrf_response.cookies["csrftoken"].value
        refresh_response = self.client.post(
            "/api/token/refresh/",
            {},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertNotIn("refresh", refresh_response.data)

        replay_response = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"token": raw_token, "password": "Another-Safe-2026!"},
            format="json",
        )
        self.assertEqual(replay_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_rejects_old_tokens_and_accepts_new_login_in_same_second(self):
        second = timezone.now().replace(microsecond=0)
        self.user.password_changed_at = second - timedelta(seconds=2)
        self.user.save(update_fields=["password_changed_at"])

        def login(password, instant):
            with mock.patch(
                "rest_framework_simplejwt.tokens.aware_utcnow", return_value=instant
            ):
                response = self.client.post(
                    "/api/auth/login/",
                    {"email": self.user.email, "password": password},
                    format="json",
                )
            self.assertEqual(response.status_code, 200, response.data)
            return (
                response.data["access"],
                response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value,
            )

        old_access, old_refresh = login(
            "Original-Safe-2026!", second + timedelta(microseconds=100000)
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {old_access}")
        self.assertEqual(self.client.get("/api/auth/properties/mine/").status_code, 200)
        self.client.credentials()
        _, raw_token = self._request_password_reset()
        changed_at = second + timedelta(microseconds=800000)
        with mock.patch("django.utils.timezone.now", return_value=changed_at):
            response = self.client.post(
                "/api/auth/password-reset/confirm/",
                {"token": raw_token, "password": "Same-Second-New-Safe-2026!"},
                format="json",
            )
        self.assertEqual(response.status_code, 200, response.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.password_changed_at, changed_at)
        self._assert_old_session_rejected(old_access, old_refresh)

        new_access, new_refresh = login(
            "Same-Second-New-Safe-2026!", second + timedelta(microseconds=900000)
        )
        self.assertEqual(AccessToken(old_access)["iat"], AccessToken(new_access)["iat"])
        self.assertEqual(RefreshToken(old_refresh)["iat"], RefreshToken(new_refresh)["iat"])
        client = APIClient(enforce_csrf_checks=True)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access}")
        self.assertEqual(client.get("/api/auth/properties/mine/").status_code, 200)
        client.credentials()
        client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = new_refresh
        client.get("/api/auth/csrf/")
        response = client.post(
            "/api/token/refresh/", {}, format="json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(response.status_code, 200, response.data)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        self.assertEqual(client.get("/api/auth/properties/mine/").status_code, 200)

    def test_legacy_tokens_in_ambiguous_second_are_rejected(self):
        self.user.password_changed_at = timezone.now().replace(microsecond=800000)
        self.user.save(update_fields=["password_changed_at"])
        access = AccessToken.for_user(self.user)
        refresh = RefreshToken.for_user(self.user)
        access["iat"] = refresh["iat"] = int(self.user.password_changed_at.timestamp())
        self._assert_old_session_rejected(str(access), str(refresh))

    def test_successful_password_reset_unlocks_account_and_allows_login(self):
        self.user.is_locked = True
        self.user.failed_attempts = 5
        self.user.save(update_fields=["is_locked", "failed_attempts"])
        _, raw_token = self._request_password_reset()
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_locked)
        self.assertEqual(self.user.failed_attempts, 5)

        response = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"token": raw_token, "password": "Recovered-Safe-Urbanex-2026!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_locked)
        self.assertEqual(self.user.failed_attempts, 0)
        login = self.client.post(
            "/api/auth/login/",
            {"email": self.user.email, "password": "Recovered-Safe-Urbanex-2026!"},
            format="json",
        )
        self.assertEqual(login.status_code, 200, login.data)

    def test_invalid_reset_does_not_unlock_or_clear_attempts(self):
        for token_state in ("invalid", "expired", "used"):
            with self.subTest(token_state=token_state):
                mail.outbox.clear()
                self.user.is_locked = True
                self.user.failed_attempts = 5
                self.user.save(update_fields=["is_locked", "failed_attempts"])
                _, raw_token = self._request_password_reset()
                record = PasswordResetToken.objects.get(
                    token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
                )
                if token_state == "expired":
                    record.expires_at = timezone.now() - timedelta(seconds=1)
                    record.save(update_fields=["expires_at"])
                elif token_state == "used":
                    record.is_used = True
                    record.save(update_fields=["is_used"])
                else:
                    raw_token += "-tampered"
                response = self.client.post(
                    "/api/auth/password-reset/confirm/",
                    {"token": raw_token, "password": "Recovered-Safe-Urbanex-2026!"},
                    format="json",
                )
                self.assertEqual(response.status_code, 400, response.data)
                self.user.refresh_from_db()
                self.assertTrue(self.user.is_locked)
                self.assertEqual(self.user.failed_attempts, 5)
                self.assertTrue(self.user.check_password("Original-Safe-2026!"))

    def test_password_reset_clears_attempts_before_account_is_locked(self):
        self.user.failed_attempts = 3
        self.user.save(update_fields=["failed_attempts"])
        _, raw_token = self._request_password_reset()
        response = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"token": raw_token, "password": "Recovered-Safe-Urbanex-2026!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_locked)
        self.assertEqual(self.user.failed_attempts, 0)

    def _old_session_tokens(self):
        self.user.password_changed_at = timezone.now() - timedelta(minutes=2)
        self.user.save(update_fields=["password_changed_at"])
        access = AccessToken.for_user(self.user)
        refresh = RefreshToken.for_user(self.user)
        issued_at = int((timezone.now() - timedelta(minutes=1)).timestamp())
        access["iat"] = issued_at
        refresh["iat"] = issued_at
        client = APIClient(enforce_csrf_checks=True)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(client.get("/api/auth/properties/mine/").status_code, 200)
        client.credentials()
        client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = str(refresh)
        client.get("/api/auth/csrf/")
        response = client.post(
            "/api/token/refresh/", {}, format="json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(response.status_code, 200)
        return str(access), str(refresh)

    def _assert_old_session_rejected(self, access, refresh):
        client = APIClient(enforce_csrf_checks=True)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(client.get("/api/auth/users/").status_code, 401)
        client.credentials()
        client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = refresh
        client.get("/api/auth/csrf/")
        response = client.post(
            "/api/token/refresh/", {}, format="json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("access", response.data)

    def test_manual_password_change_invalidates_access_and_refresh(self):
        tokens = self._old_session_tokens()
        previous_version = self.user.password_changed_at
        self.user.set_password("Manual-Safe-Urbanex-2026!")
        self.user.save(update_fields=["password"])
        self.user.refresh_from_db()
        self.assertGreater(self.user.password_changed_at, previous_version)
        self._assert_old_session_rejected(*tokens)

    def test_activation_invalidates_access_and_refresh(self):
        tokens = self._old_session_tokens()
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        raw_token = "synthetic-activation-token-hu46"
        UserActivationToken.objects.create(
            user=self.user,
            token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
        )
        response = self.client.post(
            "/api/auth/users/activate/",
            {"token": raw_token, "password": "Activated-Safe-Urbanex-2026!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.check_password("Activated-Safe-Urbanex-2026!"))
        self._assert_old_session_rejected(*tokens)

    def test_refresh_cookie_secure_flag_follows_debug(self):
        for debug in (True, False):
            with self.subTest(debug=debug), override_settings(DEBUG=debug):
                response = self.client.post(
                    "/api/auth/login/",
                    {"email": self.user.email, "password": "Original-Safe-2026!"},
                    format="json",
                )
                self.assertEqual(response.status_code, 200)
                cookie = response.cookies[settings.JWT_REFRESH_COOKIE_NAME]
                self.assertEqual(bool(cookie["secure"]), not debug)
                self.assertTrue(cookie["httponly"])
                self.assertEqual(cookie["samesite"], "Lax")

    def test_expired_password_reset_token_is_rejected(self):
        _, raw_token = self._request_password_reset()
        record = PasswordResetToken.objects.get(user=self.user)
        record.expires_at = timezone.now() - timedelta(seconds=1)
        record.save(update_fields=["expires_at"])

        response = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"token": raw_token, "password": "New-Safe-Urbanex-2026!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Original-Safe-2026!"))

    def test_refresh_requires_csrf_and_sets_no_refresh_token_in_response(self):
        client = APIClient(enforce_csrf_checks=True)
        refresh = PasswordVersionRefreshToken.for_user(self.user)
        client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = str(refresh)

        rejected_response = client.post(
            "/api/token/refresh/",
            {},
            format="json",
        )
        self.assertEqual(
            rejected_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        client.get("/api/auth/csrf/")
        csrf_token = client.cookies["csrftoken"].value
        response = client.post(
            "/api/token/refresh/",
            {},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_logout_requires_csrf_and_deletes_refresh_cookie(self):
        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/auth/csrf/")
        csrf_token = csrf_response.cookies["csrftoken"].value
        response = client.post(
            "/api/auth/logout/",
            {},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cookie = response.cookies[settings.JWT_REFRESH_COOKIE_NAME]
        self.assertEqual(cookie["max-age"], 0)
        self.assertEqual(cookie["path"], settings.JWT_REFRESH_COOKIE_PATH)

    def test_login_places_refresh_token_in_httponly_cookie(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": self.user.email,
                "password": "Original-Safe-2026!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        self.assertIn("csrftoken", response.cookies)
        cookie = response.cookies[settings.JWT_REFRESH_COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(cookie["path"], settings.JWT_REFRESH_COOKIE_PATH)


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


class PropertyOwnershipTests(TestCase):
    """DT-107: la regla de dueño se prueba con dos asesores (A dueño, B no dueño), sin rol cliente."""

    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username="asesor.a",
            email="asesor.a@urbanex.ec",
            password="Password123!",
            role="asesor",
        )
        self.other_agent = User.objects.create_user(
            username="asesor.b",
            email="asesor.b@urbanex.ec",
            password="Password123!",
            role="asesor",
        )
        self.property = Property.objects.create(
            agent=self.owner,
            title="Casa del asesor A",
            description="Captación de A",
            property_type="casa",
            price=150000,
            area_m2=120,
            location="Cumbayá",
            status="captacion",
        )
        self.detail_url = f"/api/auth/properties/{self.property.id}/"

    def test_owner_can_view_and_edit_his_property(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(self.detail_url, {"title": "Casa editada por A"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.property.refresh_from_db()
        self.assertEqual(self.property.title, "Casa editada por A")

    def test_non_owner_agent_cannot_edit_publish_or_read_requirements(self):
        # El GET de B sobre una captación de A sigue abierto: DT-39 / SEC-01, sin arreglar aquí.
        self.client.force_authenticate(user=self.other_agent)

        response = self.client.patch(self.detail_url, {"title": "Casa editada por B"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(f"{self.detail_url}publish/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f"{self.detail_url}publication-requirements/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.property.refresh_from_db()
        self.assertEqual(self.property.title, "Casa del asesor A")
        self.assertEqual(self.property.status, "captacion")


class AccountUnlockApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="unlock.admin",
            email="unlock.admin@urbanex.test",
            password="Admin-test-2026!",
            role="admin",
            is_staff=True,
        )
        self.advisor = User.objects.create_user(
            username="unlock.advisor",
            email="unlock.advisor@urbanex.test",
            password="Advisor-test-2026!",
            role="asesor",
        )

    def test_account_unlock_requires_authentication_and_admin_role(self):
        endpoint = f"/api/auth/users/{self.advisor.pk}/unlock/"

        anonymous_response = self.client.post(endpoint, {}, format="json")
        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.advisor)
        advisor_response = self.client.post(endpoint, {}, format="json")
        self.assertEqual(advisor_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_unlocks_account_and_resets_failed_attempts(self):
        self.advisor.is_locked = True
        self.advisor.failed_attempts = 5
        self.advisor.save(update_fields=["is_locked", "failed_attempts"])
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/auth/users/{self.advisor.pk}/unlock/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_locked"])
        self.assertEqual(response.data["failed_attempts"], 0)
        self.advisor.refresh_from_db()
        self.assertFalse(self.advisor.is_locked)
        self.assertEqual(self.advisor.failed_attempts, 0)

    def test_admin_cannot_unlock_an_account_that_is_not_locked(self):
        self.advisor.failed_attempts = 2
        self.advisor.save(update_fields=["failed_attempts"])
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/auth/users/{self.advisor.pk}/unlock/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.advisor.refresh_from_db()
        self.assertFalse(self.advisor.is_locked)
        self.assertEqual(self.advisor.failed_attempts, 2)

    def test_locked_and_invalid_credentials_use_the_same_login_response(self):
        self.advisor.is_locked = True
        self.advisor.failed_attempts = 5
        self.advisor.save(update_fields=["is_locked", "failed_attempts"])

        locked_response = self.client.post(
            "/api/auth/login/",
            {"email": self.advisor.email, "password": "Advisor-test-2026!"},
            format="json",
        )
        self.advisor.is_locked = False
        self.advisor.failed_attempts = 0
        self.advisor.save(update_fields=["is_locked", "failed_attempts"])
        invalid_response = self.client.post(
            "/api/auth/login/",
            {"email": self.advisor.email, "password": "Wrong-password"},
            format="json",
        )

        self.assertEqual(locked_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(locked_response.data["detail"], "Credenciales inválidas.")
        self.assertEqual(
            (locked_response.status_code, locked_response.data["detail"]),
            (invalid_response.status_code, invalid_response.data["detail"]),
        )
        self.advisor.refresh_from_db()
        self.assertEqual(self.advisor.failed_attempts, 1)


class PropertyCatalogApiTests(TestCase):
    """HU-10: filtros públicos combinables, entradas y paginación estable."""

    @classmethod
    def setUpTestData(cls):
        cls.house = cls.make_property(
            title="Casa norte", property_type="casa", price="150000.00",
            bedrooms=3, bathrooms=2, area_m2=120, location="Quito Norte",
        )
        cls.apartment = cls.make_property(
            title="Departamento centro", property_type="departamento", price="90000.00",
            bedrooms=2, bathrooms=1, area_m2=75, location="Quito Centro", status="reservador",
        )
        cls.land = cls.make_property(
            title="Terreno", property_type="terreno", price="50000.00",
            bedrooms=0, bathrooms=0, area_m2=200, location="Cuenca",
        )

    @classmethod
    def make_property(cls, **overrides):
        values = dict(title="Propiedad", description="Ejemplo", property_type="casa",
                      price="100000.00", bedrooms=2, bathrooms=1, area_m2=80,
                      location="Quito", status="disponible")
        values.update(overrides)
        return Property.objects.create(**values)

    def setUp(self):
        self.client = APIClient()

    def ids(self, params):
        response = self.client.get("/api/auth/properties/", params)
        self.assertEqual(response.status_code, 200, response.data)
        return {item["id"] for item in response.data["results"]}

    def test_each_filter_and_inclusive_boundaries(self):
        cases = [
            ({"property_type": "casa"}, {self.house.id}),
            ({"price_min": "90000.00"}, {self.house.id, self.apartment.id}),
            ({"price_max": "90000.00"}, {self.land.id, self.apartment.id}),
            ({"bedrooms": "3"}, {self.house.id}),
            ({"bathrooms": "2"}, {self.house.id}),
            ({"area_min": "120"}, {self.house.id, self.land.id}),
            ({"location": "quito"}, {self.house.id, self.apartment.id}),
            ({"location": "  Centro  "}, {self.apartment.id}),
        ]
        for params, expected in cases:
            with self.subTest(params=params):
                self.assertEqual(self.ids(params), expected)

    def test_filters_are_combined_with_and(self):
        self.assertEqual(self.ids({"property_type": "casa", "price_min": "150000",
                                  "price_max": "150000", "bedrooms": "3",
                                  "bathrooms": "2", "area_min": "120",
                                  "location": "Norte"}), {self.house.id})
        self.assertEqual(self.ids({"property_type": "casa", "price_max": "100000"}), set())

    def test_invalid_filters_return_field_errors(self):
        cases = [
            ("property_type", "villa"), ("price_min", "-1"),
            ("price_max", "texto"), ("price_max", "NaN"),
            ("price_min", "Infinity"), ("price_min", "10000000000"),
            ("price_min", "1.001"), ("bedrooms", "1.5"),
            ("bathrooms", "-1"), ("bedrooms", "2147483648"),
            ("area_min", "NaN"), ("area_min", "-0.01"),
            ("location", "x" * 501),
        ]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                response = self.client.get("/api/auth/properties/", {key: value})
                self.assertEqual(response.status_code, 400, response.data)
                self.assertIn(key, response.data)

    def test_reversed_price_range_is_rejected(self):
        response = self.client.get("/api/auth/properties/", {"price_min": "100", "price_max": "99"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("price_max", response.data)

    def test_empty_filters_are_ignored_and_zero_is_valid(self):
        self.assertEqual(self.ids({"location": "  ", "property_type": "", "price_min": "",
                                  "bedrooms": "0", "bathrooms": "0", "area_min": "0"}),
                         {self.house.id, self.apartment.id, self.land.id})

    def test_hidden_statuses_cannot_be_requested_via_filters(self):
        hidden_ids = set()
        for property_status in ("captacion", "no_disponible", "vendido", "arrendado"):
            hidden_ids.add(self.make_property(status=property_status).id)
        response = self.client.get("/api/auth/properties/", {"location": "Quito", "status": "captacion"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertFalse(hidden_ids & {item["id"] for item in response.data["results"]})
        self.assertIn(self.apartment.id, {item["id"] for item in response.data["results"]})

    def test_pagination_is_stable_and_preserves_filters(self):
        for index in range(22):
            self.make_property(title=f"Lote {index}", location="Sector paginado")
        # Empates de fecha deben desempatarse por id, sin omitir ni repetir resultados.
        Property.objects.filter(location="Sector paginado").update(created_at=timezone.now())
        first = self.client.get("/api/auth/properties/", {"location": "Sector paginado"})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.data["count"], 22)
        self.assertEqual(len(first.data["results"]), 20)
        self.assertIsNone(first.data["previous"])
        self.assertIn("location=Sector+paginado", first.data["next"])
        second = self.client.get(first.data["next"])
        self.assertEqual(second.status_code, 200)
        self.assertEqual(len(second.data["results"]), 2)
        self.assertIsNone(second.data["next"])
        actual = [item["id"] for item in first.data["results"] + second.data["results"]]
        expected = list(Property.objects.filter(location="Sector paginado").order_by("-pk")
                        .values_list("pk", flat=True))
        self.assertEqual(actual, expected)
        back = self.client.get(second.data["previous"])
        self.assertEqual(back.data["results"], first.data["results"])

    def test_invalid_and_out_of_range_pages(self):
        for page in ("0", "-1", "abc", "1.5", "999", "last"):
            with self.subTest(page=page):
                response = self.client.get("/api/auth/properties/", {"page": page})
                self.assertEqual(response.status_code, 404, response.data)

    def test_empty_catalog_has_paginated_response(self):
        Property.objects.all().delete()
        response = self.client.get("/api/auth/properties/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"count": 0, "next": None, "previous": None, "results": [],
                                       "price_distribution": {"min": None, "max": None, "total": 0, "bins": []}})

    def test_authenticated_list_keeps_existing_scope_and_supports_filters(self):
        agent = User.objects.create_user(username="catalog-agent", role="asesor")
        hidden = self.make_property(status="captacion", agent=agent, location="Sector interno")
        self.client.force_authenticate(user=agent)
        self.assertEqual(self.ids({"location": "Sector interno"}), {hidden.id})

    def test_parking_minimum_combines_with_other_filters(self):
        self.house.parking_spaces = 2
        self.house.save()
        self.apartment.parking_spaces = 1
        self.apartment.save()
        three = self.make_property(parking_spaces=3)
        four = self.make_property(parking_spaces=4)
        self.assertEqual(self.ids({"parking_spaces": "2"}), {self.house.id, three.id, four.id})
        self.assertEqual(self.ids({"parking_spaces": "1", "property_type": "departamento"}), {self.apartment.id})
        self.assertEqual(self.ids({"parking_spaces": "1"}), {self.house.id, self.apartment.id, three.id, four.id})
        self.assertEqual(self.ids({"parking_spaces": "0"}), {self.house.id, self.apartment.id, self.land.id, three.id, four.id})
        self.assertEqual(self.ids({"parking_spaces": "3"}), {three.id, four.id})
        self.assertEqual(self.ids({"parking_spaces": "4"}), {four.id})
        self.assertEqual(self.ids({"parking_spaces": ""}), {self.house.id, self.apartment.id, self.land.id, three.id, four.id})

    def test_legacy_zero_parking_is_unrestricted_and_distribution_matches(self):
        self.house.parking_spaces = 2
        self.house.save()
        self.apartment.parking_spaces = 1
        self.apartment.save()
        all_properties = self.client.get("/api/auth/properties/").data
        zero_parking = self.client.get("/api/auth/properties/", {"parking_spaces": "0"}).data
        self.assertEqual(all_properties["count"], 3)
        self.assertEqual(zero_parking["count"], 3)
        self.assertEqual(zero_parking["price_distribution"], all_properties["price_distribution"])

    def test_invalid_parking_minimum_returns_field_error(self):
        for value in ("-1", "1.5", "texto", "2147483648"):
            with self.subTest(value=value):
                response = self.client.get("/api/auth/properties/", {"parking_spaces": value})
                self.assertEqual(response.status_code, 400)
                self.assertIn("parking_spaces", response.data)

    def test_distribution_covers_all_pages_and_excludes_hidden_properties(self):
        for index in range(24):
            self.make_property(location="Histograma", price=Decimal("100.01") + index)
        self.make_property(location="Histograma", price="0.01", status="captacion")
        self.make_property(location="Histograma", price="999999.99", status="vendido")
        response = self.client.get("/api/auth/properties/", {"location": "Histograma", "page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 4)
        distribution = response.data["price_distribution"]
        self.assertEqual((distribution["min"], distribution["max"], distribution["total"]), ("100.01", "123.01", 24))
        self.assertEqual(sum(item["count"] for item in distribution["bins"]), 24)
        self.assertLessEqual(len(distribution["bins"]), 20)

    def test_distribution_ignores_only_price_and_preserves_other_filters(self):
        self.house.parking_spaces = 1
        self.house.save()
        self.apartment.parking_spaces = 1
        self.apartment.save()
        query = {"location": "Quito", "parking_spaces": "1", "bedrooms": "2"}
        first = self.client.get("/api/auth/properties/", query)
        restricted = self.client.get("/api/auth/properties/", {**query, "price_max": "100000"})
        self.assertEqual(first.data["count"], 2)
        self.assertEqual(restricted.data["count"], 1)
        self.assertEqual(first.data["price_distribution"], restricted.data["price_distribution"])
        self.assertEqual(restricted.data["price_distribution"]["min"], "90000.00")

    def test_distribution_handles_single_price_and_zero(self):
        Property.objects.all().delete()
        self.make_property(price="123.45")
        self.make_property(price="123.45", status="reservador")
        response = self.client.get("/api/auth/properties/")
        self.assertEqual(response.data["price_distribution"]["bins"], [{"min": "123.45", "max": "123.45", "count": 2}])
        self.make_property(price="0.00")
        response = self.client.get("/api/auth/properties/")
        self.assertEqual(response.data["price_distribution"]["min"], "0.00")
        self.assertEqual(sum(item["count"] for item in response.data["price_distribution"]["bins"]), 3)

    def test_distribution_cent_boundaries_count_each_property_once(self):
        Property.objects.all().delete()
        prices = [Decimal("10.00") + Decimal(index) / 100 for index in range(41)]
        for price in prices:
            self.make_property(price=price)
        distribution = self.client.get("/api/auth/properties/").data["price_distribution"]
        for item in distribution["bins"]:
            expected = sum(Decimal(item["min"]) <= price <= Decimal(item["max"]) for price in prices)
            self.assertEqual(item["count"], expected)
        self.assertEqual(sum(item["count"] for item in distribution["bins"]), len(prices))

    def test_distribution_respects_authenticated_scope_and_does_not_write_data(self):
        actor = User.objects.create_user(username="histogram-agent", email="histogram@example.test", role="asesor")
        self.make_property(price="0.01", status="captacion")
        before = list(Property.objects.order_by("pk").values())
        anonymous = self.client.get("/api/auth/properties/").data["price_distribution"]
        self.client.force_authenticate(user=actor)
        authenticated = self.client.get("/api/auth/properties/").data["price_distribution"]
        self.assertEqual(anonymous["min"], "50000.00")
        self.assertEqual(authenticated["min"], "0.01")
        self.assertEqual(list(Property.objects.order_by("pk").values()), before)

    def test_price_sort_is_global_stable_and_preserved_across_pages(self):
        for index in range(23):
            self.make_property(location="Orden", price=Decimal("100000") + index // 3)
        for sort, ordering in (("price_asc", ("price", "pk")), ("price_desc", ("-price", "-pk"))):
            with self.subTest(sort=sort):
                first = self.client.get("/api/auth/properties/", {"location": "Orden", "sort": sort})
                self.assertEqual(first.status_code, 200)
                self.assertEqual(len(first.data["results"]), 20)
                self.assertIn(f"sort={sort}", first.data["next"])
                second = self.client.get(first.data["next"])
                actual = [item["id"] for item in first.data["results"] + second.data["results"]]
                expected = list(Property.objects.filter(location="Orden").order_by(*ordering).values_list("pk", flat=True))
                self.assertEqual(actual, expected)
                self.assertEqual(len(set(actual)), 23)

    def test_sort_default_recent_and_invalid_sort_rejected(self):
        first = self.client.get("/api/auth/properties/")
        expected = list(Property.objects.order_by("-created_at", "-pk").values_list("pk", flat=True))
        self.assertEqual([row["id"] for row in first.data["results"]], expected)
        for sort in ("unknown", "price;DELETE", "1"):
            with self.subTest(sort=sort):
                response = self.client.get("/api/auth/properties/", {"sort": sort})
                self.assertEqual(response.status_code, 400)
                self.assertIn("sort", response.data)

    def test_sort_preserves_filter_scope_and_distribution(self):
        self.make_property(status="captacion", price="1")
        normal = self.client.get("/api/auth/properties/", {"location": "Quito"})
        for sort in ("price_asc", "price_desc"):
            response = self.client.get("/api/auth/properties/", {"location": "Quito", "sort": sort})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["count"], 2)
            self.assertEqual(response.data["price_distribution"], normal.data["price_distribution"])
            self.assertNotIn("captacion", {row["status"] for row in response.data["results"]})


class SetupCatalogDemoCommandTests(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user(username="catalog-existing", email="catalog-existing@example.test", role="asesor")
        User.objects.create_user(username="catalog-admin", email="catalog-admin@example.test", role="admin")
        self.existing = Property.objects.create(
            title="Propiedad previa", description="Conservar", price="148000",
            area_m2=95, location="La Carolina", status="disponible", agent=self.agent,
        )
        media_dir = tempfile.mkdtemp()
        private_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media_dir, ignore_errors=True)
        self.addCleanup(shutil.rmtree, private_dir, ignore_errors=True)
        setting_patch = override_settings(DEBUG=True, MEDIA_ROOT=media_dir)
        setting_patch.enable()
        self.addCleanup(setting_patch.disable)
        storage_patch = mock.patch.object(Document._meta.get_field("file"), "storage", FileSystemStorage(location=private_dir))
        storage_patch.start()
        self.addCleanup(storage_patch.stop)

    def run_command(self, **kwargs):
        output = io.StringIO()
        call_command("setup_catalog_demo", stdout=output, **kwargs)
        return output.getvalue()

    def test_publishes_with_requirements_and_preserves_users_and_existing_properties(self):
        users_before = list(User.objects.order_by("pk").values())
        property_before = Property.objects.get(pk=self.existing.pk).__dict__.copy()
        property_before.pop("_state")
        self.assertIn("24 creadas", self.run_command())
        examples = Property.objects.filter(title__startswith="[CAT-HU10]")
        self.assertEqual(examples.count(), 24)
        self.assertFalse(examples.exclude(status="disponible", agent=self.agent).exists())
        for prop in examples:
            self.assertEqual(get_missing_publication_requirements(prop), [])
        self.assertEqual(list(User.objects.order_by("pk").values()), users_before)
        self.existing.refresh_from_db()
        for key, value in property_before.items():
            self.assertEqual(getattr(self.existing, key), value, key)
        response = APIClient().get("/api/auth/properties/", {"location": "DEMO HU10"})
        self.assertEqual(response.data["count"], 24)
        self.assertEqual(len(response.data["results"]), 20)

    def test_rerun_preserves_example_edits_without_republishing(self):
        self.run_command(count=21)
        prop = Property.objects.filter(title__startswith="[CAT-HU10]").first()
        prop.status = "no_disponible"
        prop.unavailability_reason = "Prueba local"
        prop.price = Decimal("1.00")
        prop.save()
        before = list(Property.objects.order_by("pk").values())
        self.assertIn("0 creadas", self.run_command(count=21))
        self.assertEqual(list(Property.objects.order_by("pk").values()), before)

    def test_refuses_non_debug_or_non_sqlite(self):
        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError):
                self.run_command()
        with mock.patch("apps.users.management.commands.setup_catalog_demo.connection") as db:
            db.vendor = "postgresql"
            with self.assertRaises(CommandError):
                self.run_command()
        self.assertEqual(Property.objects.count(), 1)

    def test_requires_existing_active_unambiguous_agent(self):
        with self.assertRaises(CommandError):
            self.run_command(agent_id=999999)
        other = User.objects.create_user(username="catalog-other", email="catalog-other@example.test", role="asesor")
        with self.assertRaises(CommandError):
            self.run_command()
        other.is_active = False
        other.save()
        with self.assertRaises(CommandError):
            self.run_command(agent_id=other.pk)
        self.assertEqual(Property.objects.count(), 1)

    def test_bad_counts_do_not_write_data(self):
        for count in (0, 20, 61):
            with self.subTest(count=count), self.assertRaises(CommandError):
                self.run_command(count=count)
        self.assertEqual(Property.objects.count(), 1)

    def test_publication_failure_rolls_back_database(self):
        from rest_framework.response import Response
        with mock.patch("apps.users.management.commands.setup_catalog_demo.PropertyPublishView.as_view",
                        return_value=lambda *args, **kwargs: Response(status=400)):
            with self.assertRaises(CommandError):
                self.run_command(count=21)
        self.assertEqual(Property.objects.count(), 1)
        self.assertFalse(PropertyImage.objects.exists())
        self.assertFalse(Document.objects.exists())
        self.assertFalse(Appraisal.objects.exists())
