from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.helpers import (
    create_ticket_assigned_notification,
    create_ticket_created_notifications,
    create_ticket_status_notification,
)
from tickets.helpers import can_create_ticket, get_accessible_tickets
from tickets.models import Ticket, TicketStatus
from tickets.permissions import CanAccessTicket
from tickets.serializers import TicketSerializer
from users.choices import UserRole

User = get_user_model()


class TicketListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = (
            get_accessible_tickets(request.user)
            .select_related("project", "created_by", "assigned_to", "linked_ticket")
            .order_by("-created_at")
        )

        status_filter = request.query_params.get("status")
        priority_filter = request.query_params.get("priority")
        project_filter = request.query_params.get("project")
        assigned_to_filter = request.query_params.get("assigned_to")
        search = request.query_params.get("search")

        if status_filter:
            tickets = tickets.filter(status=status_filter)

        if priority_filter:
            tickets = tickets.filter(priority=priority_filter)

        if project_filter:
            tickets = tickets.filter(project_id=project_filter)

        if assigned_to_filter:
            tickets = tickets.filter(assigned_to_id=assigned_to_filter)

        if search:
            tickets = tickets.filter(title__icontains=search)

        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TicketCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        project = serializer.validated_data.get("project")

        if not can_create_ticket(request.user, project):
            return Response(
                {"detail": "You are not allowed to create tickets for this project."},
                status=status.HTTP_403_FORBIDDEN,
            )

        ticket = serializer.save(created_by=request.user)
        create_ticket_created_notifications(ticket)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TicketDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, CanAccessTicket]

    def get_object(self, pk):
        return get_object_or_404(Ticket, pk=pk)

    def get(self, request, pk):
        ticket = self.get_object(pk)
        self.check_object_permissions(request, ticket)

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        ticket = self.get_object(pk)
        self.check_object_permissions(request, ticket)

        serializer = TicketSerializer(ticket, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        ticket = self.get_object(pk)
        self.check_object_permissions(request, ticket)

        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ticket = self.get_object(pk)
        self.check_object_permissions(request, ticket)

        if ticket.status == TicketStatus.CLOSED:
            return Response(
                {"detail": "Closed tickets cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TicketAssignAPIView(APIView):
    permission_classes = [IsAuthenticated, CanAccessTicket]

    def get_object(self, pk):
        return get_object_or_404(Ticket, pk=pk)

    def patch(self, request, pk):
        ticket = self.get_object(pk)
        self.check_object_permissions(request, ticket)

        assigned_to_id = request.data.get("assigned_to")
        if not assigned_to_id:
            return Response(
                {"assigned_to": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ticket.status == TicketStatus.CLOSED:
            return Response(
                {"detail": "Closed tickets cannot be modified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            assigned_user = User.objects.get(id=assigned_to_id)
        except User.DoesNotExist:
            return Response(
                {"assigned_to": ["User does not exist."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if assigned_user.role != UserRole.EMPLOYEE:
            return Response(
                {"assigned_to": ["User must be an employee."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            hasattr(ticket.project, "team_members")
            and not ticket.project.team_members.filter(id=assigned_user.id).exists()
        ):
            return Response(
                {"assigned_to": ["User is not part of this project team."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.assigned_to = assigned_user

        if ticket.status == TicketStatus.TODO:
            ticket.status = TicketStatus.IN_PROGRESS

        ticket.save()
        create_ticket_assigned_notification(ticket)

        return Response(
            {
                "detail": "Ticket assigned successfully.",
                "ticket_id": ticket.id,
                "assigned_to": ticket.assigned_to.id,
                "status": ticket.status,
            },
            status=status.HTTP_200_OK,
        )


class TicketStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, CanAccessTicket]

    ALLOWED_TRANSITIONS = {
        TicketStatus.TODO: [TicketStatus.IN_PROGRESS],
        TicketStatus.IN_PROGRESS: [TicketStatus.RESOLVED],
        TicketStatus.RESOLVED: [TicketStatus.CLOSED],
        TicketStatus.CLOSED: [],
    }

    def get_object(self, pk):
        return get_object_or_404(Ticket, pk=pk)

    def patch(self, request, pk):
        ticket = self.get_object(pk)
        self.check_object_permissions(request, ticket)

        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"status": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ticket.status == TicketStatus.CLOSED:
            return Response(
                {"detail": "Closed tickets cannot be modified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_statuses = self.ALLOWED_TRANSITIONS.get(ticket.status, [])
        if new_status not in allowed_statuses:
            return Response(
                {"detail": "Invalid status transition."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.status = new_status

        if new_status == TicketStatus.RESOLVED:
            ticket.resolved_at = timezone.now()
        elif new_status == TicketStatus.CLOSED:
            ticket.closed_at = timezone.now()

        ticket.save()
        create_ticket_status_notification(ticket)

        return Response(
            {"status": ticket.status},
            status=status.HTTP_200_OK,
        )


class TicketLinkAPIView(APIView):
    permission_classes = [IsAuthenticated, CanAccessTicket]

    def get_object(self, pk):
        return get_object_or_404(Ticket, pk=pk)

    def patch(self, request, pk):
        ticket = self.get_object(pk)
        self.check_object_permissions(request, ticket)

        linked_ticket_id = request.data.get("linked_ticket")
        if not linked_ticket_id:
            return Response(
                {"linked_ticket": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ticket.status == TicketStatus.CLOSED:
            return Response(
                {"detail": "Closed tickets cannot be modified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ticket.id == int(linked_ticket_id):
            return Response(
                {"detail": "Cannot link ticket to itself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        linked_ticket = get_object_or_404(Ticket, pk=linked_ticket_id)

        self.check_object_permissions(request, linked_ticket)

        ticket.linked_ticket = linked_ticket
        ticket.save()

        return Response(
            {"detail": "Linked"},
            status=status.HTTP_200_OK,
        )