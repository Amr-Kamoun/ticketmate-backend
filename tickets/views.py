from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.models import Ticket, TicketStatus
from tickets.serializers import TicketSerializer

'''
all permission are subject to change the are just set like that for now
'''
class TicketListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = Ticket.objects.select_related(
            "project", "created_by", "assigned_to", "linked_ticket"
        ).all().order_by("-created_at")

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
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        serializer = TicketSerializer(ticket, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.status == TicketStatus.CLOSED:
            return Response(
                {"detail": "Closed tickets cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TicketAssignAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)

        if ticket.status == TicketStatus.CLOSED:
            return Response(
                {"detail": "Closed tickets cannot be edited."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assigned_to = request.data.get("assigned_to")
        if not assigned_to:
            return Response(
                {"assigned_to": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.assigned_to_id = assigned_to
        ticket.save()

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TicketStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    ALLOWED_TRANSITIONS = {
        TicketStatus.TODO: [TicketStatus.IN_PROGRESS],
        TicketStatus.IN_PROGRESS: [TicketStatus.RESOLVED],
        TicketStatus.RESOLVED: [TicketStatus.CLOSED],
        TicketStatus.CLOSED: [],
    }

    def patch(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)

        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"status": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_statuses = self.ALLOWED_TRANSITIONS.get(ticket.status, [])

        if new_status not in allowed_statuses:
            return Response(
                {
                    "detail": f"Invalid status transition from {ticket.status} to {new_status}."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.status = new_status
        ticket.save()

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TicketLinkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)

        if ticket.status == TicketStatus.CLOSED:
            return Response(
                {"detail": "Closed tickets cannot be edited."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        linked_ticket_id = request.data.get("linked_ticket")
        if not linked_ticket_id:
            return Response(
                {"linked_ticket": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        linked_ticket = get_object_or_404(Ticket, pk=linked_ticket_id)

        if ticket.id == linked_ticket.id:
            return Response(
                {"detail": "A ticket cannot be linked to itself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.linked_ticket = linked_ticket
        ticket.save()

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)