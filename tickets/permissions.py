from rest_framework.permissions import BasePermission

from tickets.helpers import user_can_access_ticket


class CanAccessTicket(BasePermission):
    def has_object_permission(self, request, view, obj):
        return user_can_access_ticket(request.user, obj)
