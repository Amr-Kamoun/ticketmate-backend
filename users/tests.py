from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User, UserRole


class UserAuthTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="Admin12345!",
            full_name="Admin User",
            role=UserRole.ADMIN,
        )

        self.client_user = User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="Client12345!",
            full_name="Client User",
            role=UserRole.CLIENT,
        )

        self.login_url = reverse("users:login")
        self.refresh_url = reverse("users:refresh")
        self.me_url = reverse("users:me")
        self.admin_only_url = reverse("users:admin-only")

    def test_user_role_is_saved_correctly(self):
        self.assertEqual(self.admin_user.role, UserRole.ADMIN)
        self.assertEqual(self.client_user.role, UserRole.CLIENT)

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "admin1",
                "password": "Admin12345!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_returns_new_access_token(self):
        login_response = self.client.post(
            self.login_url,
            {
                "username": "admin1",
                "password": "Admin12345!",
            },
            format="json",
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user_data(self):
        login_response = self.client.post(
            self.login_url,
            {
                "username": "client1",
                "password": "Client12345!",
            },
            format="json",
        )

        access_token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "client1")
        self.assertEqual(response.data["email"], "client1@example.com")
        self.assertEqual(response.data["role"], UserRole.CLIENT)

    def test_admin_only_allows_admin_user(self):
        login_response = self.client.post(
            self.login_url,
            {
                "username": "admin1",
                "password": "Admin12345!",
            },
            format="json",
        )

        access_token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get(self.admin_only_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Admin access granted")

    def test_admin_only_forbids_non_admin_user(self):
        login_response = self.client.post(
            self.login_url,
            {
                "username": "client1",
                "password": "Client12345!",
            },
            format="json",
        )

        access_token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get(self.admin_only_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )
