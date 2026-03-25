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


class TicketFilterAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="AdminPass123!",
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_staff=True,
        )

        self.employee_user = User.objects.create_user(
            username="employeeuser",
            email="employee@example.com",
            password="EmployeePass123!",
            full_name="Employee User",
            role=UserRole.EMPLOYEE,
        )

        self.second_employee = User.objects.create_user(
            username="secondemployee",
            email="secondemployee@example.com",
            password="EmployeePass456!",
            full_name="Second Employee",
            role=UserRole.EMPLOYEE,
        )

        self.client_obj = Client.objects.create(
            name="Acme Corp",
            contact_email="contact@acme.com",
            phone="01012345678",
            address="Cairo, Egypt",
        )

        self.second_client = Client.objects.create(
            name="Beta Corp",
            contact_email="contact@beta.com",
            phone="01087654321",
            address="Alexandria, Egypt",
        )

        self.project_one = Project.objects.create(
            name="TicketMate Project",
            client=self.client_obj,
            project_type="SOFTWARE_SUPPORT",
            project_owner=self.admin_user,
        )

        self.project_two = Project.objects.create(
            name="Support Portal",
            client=self.second_client,
            project_type="SOFTWARE_SUPPORT",
            project_owner=self.admin_user,
        )

        self.ticket_one = Ticket.objects.create(
            title="Login Bug",
            description="Users cannot log in.",
            ticket_type=TicketType.PROBLEM,
            priority=TicketPriority.HIGH,
            status=TicketStatus.TODO,
            project=self.project_one,
            created_by=self.admin_user,
            assigned_to=self.employee_user,
        )

        self.ticket_two = Ticket.objects.create(
            title="Dashboard Inquiry",
            description="Question about dashboard usage.",
            ticket_type=TicketType.INQUIRY,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.IN_PROGRESS,
            project=self.project_one,
            created_by=self.admin_user,
            assigned_to=self.second_employee,
        )

        self.ticket_three = Ticket.objects.create(
            title="New Feature Request",
            description="Request to add export button.",
            ticket_type=TicketType.NEW_REQUEST,
            priority=TicketPriority.CRITICAL,
            status=TicketStatus.RESOLVED,
            project=self.project_two,
            created_by=self.admin_user,
            assigned_to=self.employee_user,
        )

        self.list_url = reverse("tickets:ticket-list")

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_filter_tickets_by_status(self):
        self.authenticate(self.admin_user)

        response = self.client.get(self.list_url, {"status": TicketStatus.TODO})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Login Bug")

    def test_filter_tickets_by_priority(self):
        self.authenticate(self.admin_user)

        response = self.client.get(self.list_url, {"priority": TicketPriority.CRITICAL})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "New Feature Request")

    def test_filter_tickets_by_project(self):
        self.authenticate(self.admin_user)

        response = self.client.get(self.list_url, {"project": self.project_one.pk})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        returned_titles = [ticket["title"] for ticket in response.data]
        self.assertIn("Login Bug", returned_titles)
        self.assertIn("Dashboard Inquiry", returned_titles)

    def test_filter_tickets_by_assigned_user(self):
        self.authenticate(self.admin_user)

        response = self.client.get(self.list_url, {"assigned_to": self.employee_user.pk})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        returned_titles = [ticket["title"] for ticket in response.data]
        self.assertIn("Login Bug", returned_titles)
        self.assertIn("New Feature Request", returned_titles)

    def test_search_tickets_by_title(self):
        self.authenticate(self.admin_user)

        response = self.client.get(self.list_url, {"search": "login"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Login Bug")

    def test_filter_combination_status_and_priority(self):
        self.authenticate(self.admin_user)

        response = self.client.get(
            self.list_url,
            {
                "status": TicketStatus.RESOLVED,
                "priority": TicketPriority.CRITICAL,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "New Feature Request")

    def test_filter_returns_empty_list_when_no_match(self):
        self.authenticate(self.admin_user)

        response = self.client.get(
            self.list_url,
            {
                "status": TicketStatus.CLOSED,
                "priority": TicketPriority.LOW,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_unauthenticated_user_cannot_filter_tickets(self):
        response = self.client.get(self.list_url, {"status": TicketStatus.TODO})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)