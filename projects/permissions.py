from rest_framework.permissions import BasePermission

from users.models import UserRole


class CanManageProject(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            UserRole.ADMIN,
            UserRole.PROJECT_OWNER,
        ]

    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.ADMIN:
            return True
        if request.user.role == UserRole.PROJECT_OWNER:
            return obj.project_owner_id == request.user.id
        return False


class CanViewProject(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == UserRole.ADMIN:
            return True
        if request.user.role == UserRole.PROJECT_OWNER and obj.project_owner_id == request.user.id:
            return True
        if request.user.role == UserRole.EMPLOYEE and obj.team_members.filter(id=request.user.id).exists():
            return True
        return False