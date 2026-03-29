from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"


class IsProjectOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "PROJECT_OWNER"


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "EMPLOYEE"


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "CLIENT"


class IsAdminOrProjectOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            "ADMIN",
            "PROJECT_OWNER",
        ]
