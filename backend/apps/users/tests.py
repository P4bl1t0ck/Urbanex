from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import Property
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

    # TEST 2: Permiso de publicación de propiedad (cambio a 'disponible')
    def test_publish_property_permission(self):
        property_obj = Property.objects.create(
            agent=self.agent,
            title="Casa en captación",
            description="Para publicar",
            property_type="casa",
            price=150000,
            area_m2=120,
            location="Cumbayá",
            status="captacion"
        )
        
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