from rest_framework import serializers

from attachments.models import Attachment
from attachments.validators import validate_file_extension, validate_file_size


class AttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        validators=[validate_file_extension, validate_file_size]
    )

    class Meta:
        model = Attachment
        fields = [
            "id",
            "ticket",
            "file",
            "uploaded_by",
            "created_at",
        ]
        read_only_fields = ("id", "ticket", "uploaded_by", "created_at")
