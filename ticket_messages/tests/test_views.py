from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clients.models import Client
from projects.models import Project
from ticket_messages.models import TicketMessage
from tickets.choices import TicketPriority, TicketStatus, TicketType
from tickets.models import Ticket
from users.choices import UserRole

User = get_user_model()


class TicketMessageAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="Admin12345!",
            full_name="Admin User",
            role=UserRole.ADMIN,
        )

        self.po_user = User.objects.create_user(
            username="po1",
            email="po1@example.com",
            password="Po12345!",
            full_name="Project Owner",
            role=UserRole.PROJECT_OWNER,
        )

        self.employee_user = User.objects.create_user(
            username="emp1",
            email="emp1@example.com",
            password="Emp12345!",
            full_name="Employee User",
            role=UserRole.EMPLOYEE,
        )

        self.client_company = Client.objects.create(
            name="Acme Corp",
            contact_email="contact@acme.com",
            phone="01012345678",
            address="Cairo, Egypt",
        )

        self.client_user = User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="Client12345!",
            full_name="Client User",
            role=UserRole.CLIENT,
            client=self.client_company,
        )

        self.other_client_company = Client.objects.create(
            name="Beta Corp",
            contact_email="contact@beta.com",
            phone="01099999999",
            address="Alexandria, Egypt",
        )

        self.other_client_user = User.objects.create_user(
            username="client2",
            email="client2@example.com",
            password="Client22345!",
            full_name="Other Client User",
            role=UserRole.CLIENT,
            client=self.other_client_company,
        )

        self.project = Project.objects.create(
            name="TicketMate Project",
            client=self.client_company,
            project_type="SOFTWARE_SUPPORT",
            project_owner=self.po_user,
        )
        self.project.team_members.add(self.employee_user)

        self.ticket = Ticket.objects.create(
            title="Login Bug",
            description="Users cannot log in.",
            ticket_type=TicketType.PROBLEM,
            priority=TicketPriority.HIGH,
            status=TicketStatus.TODO,
            project=self.project,
            created_by=self.client_user,
        )

        self.public_message = TicketMessage.objects.create(
            ticket=self.ticket,
            author=self.employee_user,
            body="We are investigating this issue.",
            is_internal=False,
        )

        self.internal_message = TicketMessage.objects.create(
            ticket=self.ticket,
            author=self.employee_user,
            body="Internal debugging note.",
            is_internal=True,
        )

        self.url = reverse(
            "ticket_messages:ticket-message-list-create",
            kwargs={"ticket_id": self.ticket.pk},
        )

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_unauthenticated_user_cannot_list_messages(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_staff_user_can_list_all_messages(self):
        self.authenticate(self.employee_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_client_user_sees_only_public_messages(self):
        self.authenticate(self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["body"], "We are investigating this issue.")
        self.assertFalse(response.data[0]["is_internal"])

    def test_unrelated_user_cannot_list_messages(self):
        self.authenticate(self.other_client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authorized_user_can_create_public_message(self):
        self.authenticate(self.client_user)

        data = {
            "body": "Any updates on this ticket?",
            "is_internal": False,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TicketMessage.objects.filter(ticket=self.ticket).count(), 3)
        self.assertEqual(response.data["body"], "Any updates on this ticket?")
        self.assertEqual(response.data["author"], self.client_user.id)
        self.assertFalse(response.data["is_internal"])

    def test_client_user_cannot_create_internal_message(self):
        self.authenticate(self.client_user)

        data = {
            "body": "This should not be internal.",
            "is_internal": True,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_internal", response.data)

    def test_staff_user_can_create_internal_message(self):
        self.authenticate(self.employee_user)

        data = {
            "body": "Internal team note.",
            "is_internal": True,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.employee_user.id)
        self.assertTrue(response.data["is_internal"])

    def test_message_body_cannot_be_blank_or_whitespace(self):
        self.authenticate(self.employee_user)

        data = {
            "body": "   ",
            "is_internal": False,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("body", response.data)

    def test_request_cannot_spoof_author_or_ticket(self):
        self.authenticate(self.employee_user)

        other_ticket = Ticket.objects.create(
            title="Other Ticket",
            description="Another issue.",
            ticket_type=TicketType.INQUIRY,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.TODO,
            project=self.project,
            created_by=self.client_user,
        )

        data = {
            "ticket": other_ticket.id,
            "author": self.client_user.id,
            "body": "Spoof attempt.",
            "is_internal": False,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["ticket"], self.ticket.id)
        self.assertEqual(response.data["author"], self.employee_user.id)

    def test_project_owner_can_list_all_messages(self):
        self.authenticate(self.po_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_can_create_internal_message(self):
        self.authenticate(self.admin_user)

        data = {
            "body": "Admin internal note.",
            "is_internal": True,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.admin_user.id)
        self.assertTrue(response.data["is_internal"])
