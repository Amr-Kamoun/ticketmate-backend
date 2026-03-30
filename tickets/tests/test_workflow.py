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


class TicketWorkflowAPITestCase(APITestCase):
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

        self.project = Project.objects.create(
            name="TicketMate Project",
            client=self.client_obj,
            project_type="SOFTWARE_SUPPORT",
            project_owner=self.admin_user,
        )

        self.project.team_members.add(self.employee_user, self.second_employee)

        self.ticket = Ticket.objects.create(
            title="Login Bug",
            description="Users cannot log in.",
            ticket_type=TicketType.PROBLEM,
            priority=TicketPriority.HIGH,
            status=TicketStatus.TODO,
            project=self.project,
            created_by=self.admin_user,
            assigned_to=self.employee_user,
        )

        self.other_ticket = Ticket.objects.create(
            title="Dashboard Error",
            description="Dashboard is not loading.",
            ticket_type=TicketType.INQUIRY,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.TODO,
            project=self.project,
            created_by=self.admin_user,
        )

        self.assign_url = reverse(
            "tickets:ticket-assign", kwargs={"pk": self.ticket.pk}
        )
        self.status_url = reverse(
            "tickets:ticket-status-update", kwargs={"pk": self.ticket.pk}
        )
        self.link_url = reverse("tickets:ticket-link", kwargs={"pk": self.ticket.pk})

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_unauthenticated_user_cannot_assign_ticket(self):
        data = {"assigned_to": self.second_employee.pk}

        response = self.client.patch(self.assign_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assign_ticket_requires_assigned_to_field(self):
        self.authenticate(self.admin_user)

        response = self.client.patch(self.assign_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assigned_to", response.data)

    def test_valid_status_transition_todo_to_in_progress(self):
        self.authenticate(self.admin_user)

        data = {"status": TicketStatus.IN_PROGRESS}

        response = self.client.patch(self.status_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, TicketStatus.IN_PROGRESS)

    def test_valid_status_transition_in_progress_to_resolved(self):
        self.authenticate(self.admin_user)

        self.ticket.status = TicketStatus.IN_PROGRESS
        self.ticket.save()

        data = {"status": TicketStatus.RESOLVED}

        response = self.client.patch(self.status_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, TicketStatus.RESOLVED)

    def test_valid_status_transition_resolved_to_closed(self):
        self.authenticate(self.admin_user)

        self.ticket.status = TicketStatus.RESOLVED
        self.ticket.save()

        data = {"status": TicketStatus.CLOSED}

        response = self.client.patch(self.status_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, TicketStatus.CLOSED)

    def test_invalid_status_transition_todo_to_resolved(self):
        self.authenticate(self.admin_user)

        data = {"status": TicketStatus.RESOLVED}

        response = self.client.patch(self.status_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, TicketStatus.TODO)

    def test_status_update_requires_status_field(self):
        self.authenticate(self.admin_user)

        response = self.client.patch(self.status_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_closed_ticket_cannot_change_status(self):
        self.authenticate(self.admin_user)

        self.ticket.status = TicketStatus.CLOSED
        self.ticket.save()

        data = {"status": TicketStatus.RESOLVED}

        response = self.client.patch(self.status_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_user_can_link_ticket(self):
        self.authenticate(self.admin_user)

        data = {"linked_ticket": self.other_ticket.pk}

        response = self.client.patch(self.link_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.linked_ticket, self.other_ticket)

    def test_link_ticket_requires_linked_ticket_field(self):
        self.authenticate(self.admin_user)

        response = self.client.patch(self.link_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("linked_ticket", response.data)

    def test_ticket_cannot_be_linked_to_itself(self):
        self.authenticate(self.admin_user)

        data = {"linked_ticket": self.ticket.pk}

        response = self.client.patch(self.link_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.ticket.refresh_from_db()
        self.assertIsNone(self.ticket.linked_ticket)

    def test_closed_ticket_cannot_be_linked(self):
        self.authenticate(self.admin_user)

        self.ticket.status = TicketStatus.CLOSED
        self.ticket.save()

        data = {"linked_ticket": self.other_ticket.pk}

        response = self.client.patch(self.link_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_closed_ticket_cannot_be_assigned(self):
        self.authenticate(self.admin_user)

        self.ticket.status = TicketStatus.CLOSED
        self.ticket.save()

        data = {"assigned_to": self.second_employee.pk}

        response = self.client.patch(self.assign_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_user_can_assign_ticket(self):
        self.authenticate(self.admin_user)

        self.ticket.status = TicketStatus.TODO
        self.ticket.save()

        data = {"assigned_to": self.second_employee.pk}

        response = self.client.patch(self.assign_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.second_employee)
        self.assertEqual(self.ticket.status, TicketStatus.IN_PROGRESS)

    def test_assign_ticket_to_nonexistent_user_returns_400(self):
        self.authenticate(self.admin_user)

        data = {"assigned_to": 99999}

        response = self.client.patch(self.assign_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assigned_to", response.data)

    def test_assign_ticket_to_non_employee_returns_400(self):
        self.authenticate(self.admin_user)

        non_employee_user = User.objects.create_user(
            username="clientuser",
            email="client@example.com",
            password="ClientPass123!",
            full_name="Client User",
            role=UserRole.CLIENT,
        )

        data = {"assigned_to": non_employee_user.pk}

        response = self.client.patch(self.assign_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assigned_to", response.data)

    def test_assign_ticket_to_user_outside_project_team_returns_400(self):
        self.authenticate(self.admin_user)

        outside_employee = User.objects.create_user(
            username="outsideemployee",
            email="outside@example.com",
            password="OutsidePass123!",
            full_name="Outside Employee",
            role=UserRole.EMPLOYEE,
        )

        data = {"assigned_to": outside_employee.pk}

        response = self.client.patch(self.assign_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assigned_to", response.data)

    def test_assign_ticket_moves_status_from_todo_to_in_progress(self):
        self.authenticate(self.admin_user)

        self.ticket.status = TicketStatus.TODO
        self.ticket.assigned_to = None
        self.ticket.save()

        data = {"assigned_to": self.second_employee.pk}

        response = self.client.patch(self.assign_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.second_employee)
        self.assertEqual(self.ticket.status, TicketStatus.IN_PROGRESS)

    def test_resolved_sets_resolved_at(self):
        self.authenticate(self.admin_user)

        self.ticket.status = TicketStatus.IN_PROGRESS
        self.ticket.save()

        response = self.client.patch(
            self.status_url, {"status": TicketStatus.RESOLVED}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertIsNotNone(self.ticket.resolved_at)

    def test_closed_sets_closed_at(self):
        self.authenticate(self.admin_user)

        self.ticket.status = TicketStatus.RESOLVED
        self.ticket.save()

        response = self.client.patch(
            self.status_url, {"status": TicketStatus.CLOSED}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertIsNotNone(self.ticket.closed_at)
