from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attachments.serializers import AttachmentSerializer
from tickets.models import Ticket
from tickets.permissions import CanAccessTicket


class AttachmentUploadAPIView(APIView):
    permission_classes = [IsAuthenticated, CanAccessTicket]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        self.check_object_permissions(request, ticket)

        serializer = AttachmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(ticket=ticket, uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
