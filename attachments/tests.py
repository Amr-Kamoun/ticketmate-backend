from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from attachments.models import Attachment
from clients.models import Client
from projects.models import Project
from ticket_messages.models import TicketMessage
from tickets.choices import TicketPriority, TicketStatus, TicketType
from tickets.models import Ticket
from users.models import UserRole

User = get_user_model()


class AttachmentUploadAPITestCase(APITestCase):
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

        self.ticket = Ticket.objects.create(
            title="Login Bug",
            description="Users cannot log in.",
            ticket_type=TicketType.PROBLEM,
            priority=TicketPriority.HIGH,
            status=TicketStatus.TODO,
            project=self.project,
            created_by=self.admin_user,
        )

        self.other_ticket = Ticket.objects.create(
            title="Another Ticket",
            description="Another issue.",
            ticket_type=TicketType.PROBLEM,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.TODO,
            project=self.project,
            created_by=self.admin_user,
        )

        self.message = TicketMessage.objects.create(
            ticket=self.ticket,
            author=self.admin_user,
            body="Initial message",
        )

        self.other_message = TicketMessage.objects.create(
            ticket=self.other_ticket,
            author=self.admin_user,
            body="Other ticket message",
        )

        self.upload_url = reverse(
            "attachments:attachment-upload",
            kwargs={"ticket_id": self.ticket.pk},
        )

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_authenticated_user_can_upload_attachment(self):
        self.authenticate(self.admin_user)

        file = SimpleUploadedFile(
            "test.txt",
            b"hello world",
            content_type="text/plain",
        )

        response = self.client.post(
            self.upload_url,
            {"file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attachment.objects.count(), 1)

        attachment = Attachment.objects.first()
        self.assertEqual(attachment.ticket, self.ticket)
        self.assertEqual(attachment.uploaded_by, self.admin_user)
        self.assertIsNone(attachment.message)

    def test_authenticated_user_can_upload_attachment_to_message(self):
        self.authenticate(self.admin_user)

        file = SimpleUploadedFile(
            "test.txt",
            b"hello world",
            content_type="text/plain",
        )

        response = self.client.post(
            self.upload_url,
            {"message": self.message.pk, "file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attachment.objects.count(), 1)

        attachment = Attachment.objects.first()
        self.assertEqual(attachment.ticket, self.ticket)
        self.assertEqual(attachment.message, self.message)
        self.assertEqual(attachment.uploaded_by, self.admin_user)

    def test_unauthenticated_user_cannot_upload_attachment(self):
        file = SimpleUploadedFile(
            "test.txt",
            b"hello world",
            content_type="text/plain",
        )

        response = self.client.post(
            self.upload_url,
            {"file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_file_type_is_rejected(self):
        self.authenticate(self.admin_user)

        file = SimpleUploadedFile(
            "malware.exe",
            b"fake-binary",
            content_type="application/octet-stream",
        )

        response = self.client.post(
            self.upload_url,
            {"file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)

    def test_authenticated_user_without_ticket_access_cannot_upload_attachment(self):
        unauthorized_user = User.objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="OutsiderPass123!",
            full_name="Outsider User",
            role=UserRole.EMPLOYEE,
        )

        self.authenticate(unauthorized_user)

        file = SimpleUploadedFile(
            "test.txt",
            b"hello world",
            content_type="text/plain",
        )

        response = self.client.post(
            self.upload_url,
            {"file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Attachment.objects.count(), 0)

    def test_cannot_upload_attachment_with_message_from_another_ticket(self):
        self.authenticate(self.admin_user)

        file = SimpleUploadedFile(
            "test.txt",
            b"hello world",
            content_type="text/plain",
        )

        response = self.client.post(
            self.upload_url,
            {"message": self.other_message.pk, "file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Attachment.objects.count(), 0)
