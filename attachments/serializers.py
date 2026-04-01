from rest_framework import serializers

from attachments.validators import validate_file_extension, validate_file_size

from .models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        validators=[validate_file_extension, validate_file_size]
    )

    class Meta:
        model = Attachment
        fields = [
            "id",
            "ticket",
            "message",
            "file",
            "uploaded_by",
            "created_at",
        ]
        read_only_fields = ("id", "ticket", "uploaded_by", "created_at")

    def validate(self, attrs):
        ticket = self.context.get("ticket")
        message = attrs.get("message")

        if message and message.ticket != ticket:
            raise serializers.ValidationError(
                "Message must belong to the selected ticket."
            )

        return attrs
