from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clients.models import Client
from projects.models import Project
from tickets.choices import TicketPriority, TicketStatus, TicketType
from tickets.models import Ticket
from users.choices import UserRole

User = get_user_model()


class DashboardViewTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="Admin12345!",
            full_name="Admin User",
            role=UserRole.ADMIN,
        )

        self.employee_user = User.objects.create_user(
            username="emp1",
            email="emp1@example.com",
            password="Emp12345!",
            full_name="Employee User",
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
        self.project.team_members.add(self.employee_user)

        Ticket.objects.create(
            title="Login Bug",
            description="Users cannot log in.",
            ticket_type=TicketType.PROBLEM,
            priority=TicketPriority.HIGH,
            status=TicketStatus.TODO,
            project=self.project,
            created_by=self.admin_user,
            assigned_to=self.employee_user,
        )

        self.url = reverse("dashboard:dashboard-stats")

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_admin_can_access_dashboard_stats(self):
        self.authenticate(self.admin_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_tickets", response.data)
        self.assertIn("tickets_by_priority", response.data)
        self.assertIn("tickets_by_project", response.data)
        self.assertIn("tickets_by_status", response.data)
        self.assertIn("tickets_per_employee", response.data)
        self.assertIn("active_projects_count", response.data)
        self.assertIn("average_resolution_time_seconds", response.data)

    def test_non_admin_cannot_access_dashboard_stats(self):
        self.authenticate(self.employee_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access_dashboard_stats(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
