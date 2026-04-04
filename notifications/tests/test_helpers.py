from django.contrib.auth import get_user_model
from django.test import TestCase

from clients.models import Client
from notifications.choices import NotificationType
from notifications.helpers import (
    create_new_message_notifications,
    create_ticket_assigned_notification,
    create_ticket_created_notifications,
    create_ticket_status_notification,
)
from notifications.models import Notification
from projects.models import Project
from ticket_messages.models import TicketMessage
from tickets.choices import TicketPriority, TicketStatus, TicketType
from tickets.models import Ticket
from users.choices import UserRole

User = get_user_model()


class NotificationHelperTests(TestCase):
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

        self.second_employee = User.objects.create_user(
            username="emp2",
            email="emp2@example.com",
            password="Emp22345!",
            full_name="Second Employee",
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
        self.project.team_members.add(self.employee_user, self.second_employee)

        self.ticket = Ticket.objects.create(
            title="Login Bug",
            description="Users cannot log in.",
            ticket_type=TicketType.PROBLEM,
            priority=TicketPriority.HIGH,
            status=TicketStatus.TODO,
            project=self.project,
            created_by=self.client_user,
        )

    def test_create_ticket_created_notifications_notifies_project_owner(self):
        notifications = create_ticket_created_notifications(self.ticket)

        self.assertEqual(len(notifications), 1)
        self.assertEqual(Notification.objects.count(), 1)

        notification = Notification.objects.first()
        self.assertEqual(notification.recipient, self.po_user)
        self.assertEqual(
            notification.notification_type,
            NotificationType.TICKET_CREATED,
        )

    def test_create_ticket_assigned_notification_notifies_assigned_employee(self):
        self.ticket.assigned_to = self.employee_user
        self.ticket.save()

        notification = create_ticket_assigned_notification(self.ticket)

        self.assertIsNotNone(notification)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.recipient, self.employee_user)
        self.assertEqual(
            notification.notification_type,
            NotificationType.TICKET_ASSIGNED,
        )

    def test_create_new_message_notifications_for_public_message(self):
        self.ticket.assigned_to = self.employee_user
        self.ticket.save()

        message = TicketMessage.objects.create(
            ticket=self.ticket,
            author=self.employee_user,
            body="Public update for the ticket.",
            is_internal=False,
        )

        notifications = create_new_message_notifications(message)

        self.assertEqual(len(notifications), 2)

        recipients = set(
            Notification.objects.values_list("recipient_id", flat=True)
        )
        self.assertIn(self.po_user.id, recipients)
        self.assertIn(self.client_user.id, recipients)

    def test_internal_message_does_not_notify_client_user(self):
        self.ticket.assigned_to = self.employee_user
        self.ticket.save()

        message = TicketMessage.objects.create(
            ticket=self.ticket,
            author=self.employee_user,
            body="Internal team-only note.",
            is_internal=True,
        )

        notifications = create_new_message_notifications(message)

        recipient_ids = {
            notification.recipient_id for notification in notifications if notification
        }

        self.assertIn(self.po_user.id, recipient_ids)
        self.assertNotIn(self.client_user.id, recipient_ids)

    def test_create_ticket_status_notification_for_resolved(self):
        self.ticket.assigned_to = self.employee_user
        self.ticket.status = TicketStatus.RESOLVED
        self.ticket.save()

        notifications = create_ticket_status_notification(self.ticket)

        self.assertEqual(len(notifications), 3)

        types = set(Notification.objects.values_list("notification_type", flat=True))
        self.assertEqual(types, {NotificationType.TICKET_RESOLVED})

    def test_create_ticket_status_notification_for_closed(self):
        self.ticket.assigned_to = self.employee_user
        self.ticket.status = TicketStatus.CLOSED
        self.ticket.save()

        notifications = create_ticket_status_notification(self.ticket)

        self.assertEqual(len(notifications), 3)

        types = set(Notification.objects.values_list("notification_type", flat=True))
        self.assertEqual(types, {NotificationType.TICKET_CLOSED})