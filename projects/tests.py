from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clients.models import Client
from projects.models import Project, ProjectType
from users.models import UserRole

User = get_user_model()


class ProjectAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="Admin12345!",
            full_name="Admin One",
            role=UserRole.ADMIN,
        )

        self.po_user = User.objects.create_user(
            username="po1",
            email="po1@example.com",
            password="Po12345!",
            full_name="Project Owner One",
            role=UserRole.PROJECT_OWNER,
        )

        self.po_user_2 = User.objects.create_user(
            username="po2",
            email="po2@example.com",
            password="Po22345!",
            full_name="Project Owner Two",
            role=UserRole.PROJECT_OWNER,
        )

        self.employee_user = User.objects.create_user(
            username="emp1",
            email="emp1@example.com",
            password="Emp12345!",
            full_name="Employee One",
            role=UserRole.EMPLOYEE,
        )

        self.employee_user_2 = User.objects.create_user(
            username="emp2",
            email="emp2@example.com",
            password="Emp22345!",
            full_name="Employee Two",
            role=UserRole.EMPLOYEE,
        )

        self.client_user = User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="Client12345!",
            full_name="Client One",
            role=UserRole.CLIENT,
        )

        self.client_obj = Client.objects.create(
            name="Acme Corp",
            contact_email="contact@acme.com",
            phone="01012345678",
            address="Cairo, Egypt",
        )

        self.project = Project.objects.create(
            name="ERP Support Project",
            client=self.client_obj,
            project_type=ProjectType.SOFTWARE_SUPPORT,
            project_owner=self.po_user,
        )
        self.project.team_members.add(self.employee_user)

        self.list_create_url = reverse("projects:project-list-create")
        self.detail_url = reverse(
            "projects:project-detail", kwargs={"pk": self.project.pk}
        )
        self.assign_members_url = reverse(
            "projects:assign-members", kwargs={"pk": self.project.pk}
        )
        self.my_projects_url = reverse("projects:my-projects")

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_admin_can_create_project(self):
        self.authenticate(self.admin_user)
        data = {
            "name": "New Project",
            "client": self.client_obj.id,
            "project_type": ProjectType.ORACLE_SUPPORT,
            "project_owner": self.po_user.id,
            "team_members": [self.employee_user.id],
        }

        response = self.client.post(self.list_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(name="New Project").exists())

    def test_project_owner_can_create_project_for_self(self):
        self.authenticate(self.po_user)
        data = {
            "name": "PO Project",
            "client": self.client_obj.id,
            "project_type": ProjectType.OPEN_SOURCE_SUPPORT,
            "project_owner": self.po_user.id,
            "team_members": [self.employee_user.id],
        }

        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_project_owner_cannot_create_project_for_another_po(self):
        self.authenticate(self.po_user)
        data = {
            "name": "Invalid PO Project",
            "client": self.client_obj.id,
            "project_type": ProjectType.SOFTWARE_SUPPORT,
            "project_owner": self.po_user_2.id,
            "team_members": [self.employee_user.id],
        }

        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_create_project(self):
        self.authenticate(self.employee_user)
        data = {
            "name": "Employee Project",
            "client": self.client_obj.id,
            "project_type": ProjectType.SOFTWARE_SUPPORT,
            "project_owner": self.po_user.id,
            "team_members": [self.employee_user.id],
        }

        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_cannot_create_project(self):
        self.authenticate(self.client_user)
        data = {
            "name": "Client Project",
            "client": self.client_obj.id,
            "project_type": ProjectType.SOFTWARE_SUPPORT,
            "project_owner": self.po_user.id,
            "team_members": [self.employee_user.id],
        }

        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_project_owner_role_is_rejected(self):
        self.authenticate(self.admin_user)
        data = {
            "name": "Invalid Owner Project",
            "client": self.client_obj.id,
            "project_type": ProjectType.SOFTWARE_SUPPORT,
            "project_owner": self.employee_user.id,
            "team_members": [self.employee_user.id],
        }

        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("project_owner", response.data)

    def test_invalid_team_member_role_is_rejected(self):
        self.authenticate(self.admin_user)
        data = {
            "name": "Invalid Team Project",
            "client": self.client_obj.id,
            "project_type": ProjectType.SOFTWARE_SUPPORT,
            "project_owner": self.po_user.id,
            "team_members": [self.client_user.id],
        }

        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("team_members", response.data)

    def test_admin_can_view_all_projects(self):
        self.authenticate(self.admin_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_project_owner_sees_only_owned_projects(self):
        self.authenticate(self.po_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.project.name)

    def test_employee_sees_only_assigned_projects(self):
        self.authenticate(self.employee_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.project.name)

    def test_employee_can_view_assigned_project_detail(self):
        self.authenticate(self.employee_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employee_cannot_view_unassigned_project_detail(self):
        self.authenticate(self.employee_user_2)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_owner_can_update_owned_project(self):
        self.authenticate(self.po_user)
        response = self.client.patch(
            self.detail_url, {"name": "Updated Project"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Updated Project")

    def test_project_owner_cannot_update_project_to_another_owner(self):
        self.authenticate(self.po_user)
        response = self.client.patch(
            self.detail_url,
            {"project_owner": self.po_user_2.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_update_project(self):
        self.authenticate(self.employee_user)
        response = self.client.patch(
            self.detail_url, {"name": "Blocked"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_project(self):
        self.authenticate(self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_assign_members_accepts_only_employees(self):
        self.authenticate(self.admin_user)

        response = self.client.post(
            self.assign_members_url,
            {"team_members": [self.employee_user.id, self.client_user.id]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_assign_members(self):
        self.authenticate(self.admin_user)

        response = self.client.post(
            self.assign_members_url,
            {"team_members": [self.employee_user.id, self.employee_user_2.id]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.team_members.count(), 2)

    def test_my_projects_returns_correct_projects_for_po(self):
        self.authenticate(self.po_user)
        response = self.client.get(self.my_projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_my_projects_returns_correct_projects_for_employee(self):
        self.authenticate(self.employee_user)
        response = self.client.get(self.my_projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
