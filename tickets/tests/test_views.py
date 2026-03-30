from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clients.models import Client
from projects.models import Project
from tickets.choices import TicketPriority, TicketStatus, TicketType
from tickets.models import Ticket
from users.models import UserRole

User = get_user_model()


class TicketAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="AdminPass123!",
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_staff=True,
        )

        self.normal_user = User.objects.create_user(
            username="normaluser",
            email="user@example.com",
            password="UserPass123!",
            full_name="Normal User",
            role=UserRole.EMPLOYEE,
        )

        self.client_obj = Client.objects.create(
            name="Acme Corp",
            contact_email="contact@acme.com",
            phone="01012345678",
            address="Cairo, Egypt",
        )

        self.project = Project.objects.create(
            name="TicketMate Project",
            client=self.client_obj,
            project_type="SOFTWARE_SUPPORT",
            project_owner=self.admin_user,
        )

        self.ticket = Ticket.objects.create(
            title="Login Bug",
            description="Users cannot log in.",
            ticket_type=TicketType.PROBLEM,
            priority=TicketPriority.HIGH,
            status=TicketStatus.TODO,
            project=self.project,
            created_by=self.admin_user,
            assigned_to=self.normal_user,
        )

        self.list_url = reverse("tickets:ticket-list")
        self.create_url = reverse("tickets:ticket-create")
        self.detail_url = reverse(
            "tickets:ticket-detail", kwargs={"pk": self.ticket.pk}
        )

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_authenticated_user_can_list_tickets(self):
        self.authenticate(self.admin_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_authenticated_user_can_retrieve_ticket(self):
        self.authenticate(self.admin_user)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Login Bug")

    def test_authenticated_user_can_update_ticket(self):
        self.authenticate(self.admin_user)

        data = {
            "title": "Updated Login Bug",
            "description": "Updated description.",
            "ticket_type": TicketType.PROBLEM,
            "priority": TicketPriority.CRITICAL,
            "status": TicketStatus.TODO,
            "project": self.project.pk,
            "assigned_to": self.normal_user.pk,
        }

        response = self.client.put(self.detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.title, "Updated Login Bug")
        self.assertEqual(self.ticket.priority, TicketPriority.CRITICAL)

    def test_authenticated_user_can_delete_ticket(self):
        self.authenticate(self.admin_user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ticket.objects.filter(pk=self.ticket.pk).exists())

    def test_unauthenticated_user_cannot_list_tickets(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_create_ticket(self):
        data = {
            "title": "Blocked Ticket",
            "description": "Should not be created.",
            "ticket_type": TicketType.PROBLEM,
            "priority": TicketPriority.LOW,
            "status": TicketStatus.TODO,
            "project": self.project.pk,
        }

        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_closed_ticket_cannot_be_updated(self):
        self.authenticate(self.admin_user)

        self.ticket.status = TicketStatus.CLOSED
        self.ticket.save()

        data = {
            "title": "Updated Closed Ticket",
            "description": "This should fail.",
            "ticket_type": TicketType.PROBLEM,
            "priority": TicketPriority.HIGH,
            "status": TicketStatus.CLOSED,
            "project": self.project.pk,
            "assigned_to": self.normal_user.pk,
        }

        response = self.client.put(self.detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_unrelated_user_cannot_create_ticket_for_project(self):
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="OtherPass123!",
            full_name="Other User",
            role=UserRole.CLIENT,
        )

        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        data = {
            "title": "Unauthorized Ticket",
            "description": "Should not be allowed.",
            "ticket_type": TicketType.PROBLEM,
            "priority": TicketPriority.HIGH,
            "status": TicketStatus.TODO,
            "project": self.project.pk,
        }

        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
