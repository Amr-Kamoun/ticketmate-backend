from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from clients.models import Client
from dashboard.helpers import get_dashboard_stats
from projects.models import Project
from tickets.choices import TicketPriority, TicketStatus, TicketType
from tickets.models import Ticket
from users.choices import UserRole

User = get_user_model()


class DashboardHelperTests(TestCase):
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

        self.project = Project.objects.create(
            name="TicketMate Project",
            client=self.client_obj,
            project_type="SOFTWARE_SUPPORT",
            project_owner=self.po_user,
        )
        self.project.team_members.add(self.employee_user)

        self.ticket_one = Ticket.objects.create(
            title="Login Bug",
            description="Users cannot log in.",
            ticket_type=TicketType.PROBLEM,
            priority=TicketPriority.HIGH,
            status=TicketStatus.TODO,
            project=self.project,
            created_by=self.admin_user,
            assigned_to=self.employee_user,
        )

        self.ticket_two = Ticket.objects.create(
            title="Export Feature",
            description="Add export functionality.",
            ticket_type=TicketType.NEW_REQUEST,
            priority=TicketPriority.CRITICAL,
            status=TicketStatus.RESOLVED,
            project=self.project,
            created_by=self.admin_user,
            assigned_to=self.employee_user,
            resolved_at=timezone.now(),
        )

        self.ticket_three = Ticket.objects.create(
            title="Dashboard Issue",
            description="Dashboard not loading.",
            ticket_type=TicketType.INQUIRY,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.CLOSED,
            project=self.project,
            created_by=self.admin_user,
            assigned_to=self.employee_user,
            resolved_at=timezone.now(),
            closed_at=timezone.now(),
        )

    def test_get_dashboard_stats_returns_expected_top_level_counts(self):
        stats = get_dashboard_stats()

        self.assertEqual(stats["total_tickets"], 3)
        self.assertEqual(stats["open_tickets"], 2)
        self.assertEqual(stats["resolved_tickets"], 1)
        self.assertEqual(stats["closed_tickets"], 1)
        self.assertEqual(stats["active_projects_count"], 1)

    def test_get_dashboard_stats_returns_tickets_by_priority(self):
        stats = get_dashboard_stats()

        priorities = {
            item["priority"]: item["count"] for item in stats["tickets_by_priority"]
        }
        self.assertEqual(priorities["HIGH"], 1)
        self.assertEqual(priorities["CRITICAL"], 1)
        self.assertEqual(priorities["MEDIUM"], 1)

    def test_get_dashboard_stats_returns_tickets_by_status(self):
        stats = get_dashboard_stats()

        statuses = {
            item["status"]: item["count"] for item in stats["tickets_by_status"]
        }
        self.assertEqual(statuses["TODO"], 1)
        self.assertEqual(statuses["RESOLVED"], 1)
        self.assertEqual(statuses["CLOSED"], 1)

    def test_get_dashboard_stats_returns_tickets_per_employee(self):
        stats = get_dashboard_stats()

        self.assertEqual(len(stats["tickets_per_employee"]), 1)
        self.assertEqual(
            stats["tickets_per_employee"][0]["assigned_to__id"], self.employee_user.id
        )
        self.assertEqual(stats["tickets_per_employee"][0]["count"], 3)

    def test_get_dashboard_stats_returns_average_resolution_time_seconds(self):
        stats = get_dashboard_stats()

        self.assertGreaterEqual(stats["average_resolution_time_seconds"], 0)
