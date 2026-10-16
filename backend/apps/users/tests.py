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
        self.agent = User.objects.create_user(
            email="asesor.test@urbanex.ec",
            password="Password123!",
            role="asesor"
        )
        
        # Usuario Cliente público para pruebas
        self.client_user = User.objects.create_user(
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

    # TEST 3: Rechazo de autenticación con credenciales erróneas
    def test_login_failed_with_invalid_credentials(self):
        data = {
            "email": "asesor.test@urbanex.ec",
            "password": "PasswordIncorrecta"
        }
        response = self.client.post("/api/auth/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)