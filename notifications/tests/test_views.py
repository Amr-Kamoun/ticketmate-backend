from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clients.models import Client
from notifications.choices import NotificationType
from notifications.models import Notification
from projects.models import Project
from tickets.choices import TicketPriority, TicketStatus, TicketType
from tickets.models import Ticket
from users.choices import UserRole

User = get_user_model()


class NotificationViewAPITestCase(APITestCase):
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

        self.client_obj = Client.objects.create(
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
            client=self.client_obj,
        )

        self.project = Project.objects.create(
            name="TicketMate Project",
            client=self.client_obj,
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
            assigned_to=self.employee_user,
        )

        self.notification_one = Notification.objects.create(
            recipient=self.employee_user,
            ticket=self.ticket,
            notification_type=NotificationType.TICKET_ASSIGNED,
            message="You were assigned to ticket 'Login Bug'.",
        )

        self.notification_two = Notification.objects.create(
            recipient=self.employee_user,
            ticket=self.ticket,
            notification_type=NotificationType.NEW_MESSAGE,
            message="A new message was added to ticket 'Login Bug'.",
        )

        self.other_user_notification = Notification.objects.create(
            recipient=self.po_user,
            ticket=self.ticket,
            notification_type=NotificationType.TICKET_CREATED,
            message="A new ticket 'Login Bug' was created.",
        )

        self.list_url = reverse("notifications:notification-list")
        self.mark_read_url = reverse(
            "notifications:notification-mark-read",
            kwargs={"pk": self.notification_one.pk},
        )
        self.other_mark_read_url = reverse(
            "notifications:notification-mark-read",
            kwargs={"pk": self.other_user_notification.pk},
        )

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_authenticated_user_can_list_only_their_notifications(self):
        self.authenticate(self.employee_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        returned_ids = {item["id"] for item in response.data}
        self.assertIn(self.notification_one.id, returned_ids)
        self.assertIn(self.notification_two.id, returned_ids)
        self.assertNotIn(self.other_user_notification.id, returned_ids)

    def test_unauthenticated_user_cannot_list_notifications(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_mark_own_notification_as_read(self):
        self.authenticate(self.employee_user)

        response = self.client.patch(self.mark_read_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notification_one.refresh_from_db()
        self.assertTrue(self.notification_one.is_read)
        self.assertTrue(response.data["is_read"])

    def test_user_cannot_mark_another_users_notification_as_read(self):
        self.authenticate(self.employee_user)

        response = self.client.patch(self.other_mark_read_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.other_user_notification.refresh_from_db()
        self.assertFalse(self.other_user_notification.is_read)

    def test_unauthenticated_user_cannot_mark_notification_as_read(self):
        response = self.client.patch(self.mark_read_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
