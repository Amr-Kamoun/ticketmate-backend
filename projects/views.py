from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.choices import UserRole
from users.models import User

from .models import Project
from .permissions import CanManageProject, CanViewProject
from .serializers import AssignProjectMembersSerializer, ProjectSerializer


class ProjectListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=ProjectSerializer(many=True),
    )
    def get(self, request):
        user = request.user

        if user.role == UserRole.ADMIN:
            projects = Project.objects.all().order_by("-created_at")
        elif user.role == UserRole.PROJECT_OWNER:
            projects = Project.objects.filter(project_owner=user).order_by(
                "-created_at"
            )
        elif user.role == UserRole.EMPLOYEE:
            projects = Project.objects.filter(team_members=user).order_by("-created_at")
        else:
            projects = Project.objects.none()

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ProjectSerializer,
        responses={201: ProjectSerializer},
    )
    def post(self, request):
        if request.user.role not in [UserRole.ADMIN, UserRole.PROJECT_OWNER]:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project_owner = serializer.validated_data["project_owner"]

            if (
                request.user.role == UserRole.PROJECT_OWNER
                and project_owner != request.user
            ):
                return Response(
                    {
                        "detail": "Project owners can only create projects assigned to themselves."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Project, pk=pk)

    @extend_schema(
        responses=ProjectSerializer,
    )
    def get(self, request, pk):
        project = self.get_object(pk)
        if not CanViewProject().has_object_permission(request, self, project):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ProjectSerializer,
        responses=ProjectSerializer,
    )
    def put(self, request, pk):
        project = self.get_object(pk)
        if not CanManageProject().has_object_permission(request, self, project):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            project_owner = serializer.validated_data["project_owner"]

            if (
                request.user.role == UserRole.PROJECT_OWNER
                and project_owner != request.user
            ):
                return Response(
                    {
                        "detail": "Project owners can only assign projects to themselves."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=ProjectSerializer,
        responses=ProjectSerializer,
    )
    def patch(self, request, pk):
        project = self.get_object(pk)
        if not CanManageProject().has_object_permission(request, self, project):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            if request.user.role == UserRole.PROJECT_OWNER:
                project_owner = serializer.validated_data.get("project_owner")
                if project_owner and project_owner != request.user:
                    return Response(
                        {
                            "detail": "Project owners can only assign projects to themselves."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
    )
    def delete(self, request, pk):
        project = self.get_object(pk)
        if not CanManageProject().has_object_permission(request, self, project):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignProjectMembersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AssignProjectMembersSerializer,
        responses=ProjectSerializer,
    )
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        if not CanManageProject().has_object_permission(request, self, project):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        member_ids = request.data.get("team_members", [])
        members = User.objects.filter(id__in=member_ids, role=UserRole.EMPLOYEE)

        if len(member_ids) != members.count():
            return Response(
                {"detail": "All team members must have EMPLOYEE role."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project.team_members.set(members)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyProjectsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=ProjectSerializer(many=True),
    )
    def get(self, request):
        user = request.user

        if user.role == UserRole.ADMIN:
            projects = Project.objects.all().order_by("-created_at")
        elif user.role == UserRole.PROJECT_OWNER:
            projects = Project.objects.filter(project_owner=user).order_by(
                "-created_at"
            )
        elif user.role == UserRole.EMPLOYEE:
            projects = Project.objects.filter(team_members=user).order_by("-created_at")
        else:
            projects = Project.objects.none()

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
