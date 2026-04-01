from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.helpers import create_new_message_notifications
from ticket_messages.models import TicketMessage
from ticket_messages.serializers import TicketMessageSerializer
from tickets.helpers import user_can_access_ticket
from tickets.models import Ticket
from users.choices import UserRole


class TicketMessageListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_ticket(self, ticket_id):
        return get_object_or_404(Ticket, pk=ticket_id)

    def get(self, request, ticket_id):
        ticket = self.get_ticket(ticket_id)

        if not user_can_access_ticket(request.user, ticket):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        messages = TicketMessage.objects.filter(ticket=ticket).select_related("author")

        if request.user.role == UserRole.CLIENT:
            messages = messages.filter(is_internal=False)

        serializer = TicketMessageSerializer(
            messages,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, ticket_id):
        ticket = self.get_ticket(ticket_id)

        serializer = TicketMessageSerializer(
            data={**request.data, "ticket": ticket.id},
            context={"request": request},
        )

        if serializer.is_valid():
            message_obj = serializer.save(author=request.user, ticket=ticket)
            create_new_message_notifications(message_obj)

            response_serializer = TicketMessageSerializer(
                message_obj,
                context={"request": request},
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)