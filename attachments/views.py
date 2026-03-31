from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attachments.serializers import AttachmentSerializer
from tickets.permissions import CanAccessTicket


class AttachmentUploadAPIView(APIView):
    permission_classes = [IsAuthenticated, CanAccessTicket]

    def post(self, request):
        serializer = AttachmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ticket = serializer.validated_data["ticket"]
        self.check_object_permissions(request, ticket)

        serializer.save(uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
