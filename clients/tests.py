from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clients.models import Client
from users.models import UserRole

User = get_user_model()


class ClientAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="AdminPass123!",
            full_name="Admin User",
            role=UserRole.ADMIN,
        )

        self.normal_user = User.objects.create_user(
            username="normaluser",
            email="user@example.com",
            password="UserPass123!",
            full_name="Normal User",
            role=UserRole.CLIENT,
        )

        self.client_obj = Client.objects.create(
            name="Acme Corp",
            contact_email="contact@acme.com",
            phone="01012345678",
            address="Cairo, Egypt",
        )

        self.list_url = reverse("clients:client-list")
        self.create_url = reverse("clients:client-create")
        self.detail_url = reverse(
            "clients:client-detail", kwargs={"pk": self.client_obj.pk}
        )

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_admin_can_list_clients(self):
        self.authenticate(self.admin_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_create_client(self):
        self.authenticate(self.admin_user)

        data = {
            "name": "New Client",
            "contact_email": "newclient@example.com",
            "phone": "01099999999",
            "address": "Alexandria, Egypt",
        }

        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 2)
        self.assertTrue(Client.objects.filter(name="New Client").exists())

    def test_admin_can_retrieve_client(self):
        self.authenticate(self.admin_user)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Acme Corp")

    def test_admin_can_update_client(self):
        self.authenticate(self.admin_user)

        data = {
            "name": "Updated Client",
            "contact_email": "updated@example.com",
            "phone": "01011111111",
            "address": "Port Said, Egypt",
        }

        response = self.client.put(self.detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.name, "Updated Client")
        self.assertEqual(self.client_obj.contact_email, "updated@example.com")

    def test_admin_can_delete_client(self):
        self.authenticate(self.admin_user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Client.objects.filter(pk=self.client_obj.pk).exists())

    def test_unauthenticated_user_cannot_list_clients(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_create_client(self):
        data = {
            "name": "Blocked Client",
            "contact_email": "blocked@example.com",
            "phone": "01000000000",
            "address": "Giza, Egypt",
        }

        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_cannot_create_client(self):
        self.authenticate(self.normal_user)

        data = {
            "name": "Blocked Client",
            "contact_email": "blocked@example.com",
            "phone": "01000000000",
            "address": "Giza, Egypt",
        }

        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_update_client(self):
        self.authenticate(self.normal_user)

        data = {
            "name": "Blocked Update",
            "contact_email": "blockedupdate@example.com",
            "phone": "01022222222",
            "address": "Mansoura, Egypt",
        }

        response = self.client.put(self.detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_delete_client(self):
        self.authenticate(self.normal_user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
