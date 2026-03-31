import os

from rest_framework import serializers

from attachments.models import Attachment

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".doc",
    ".docx",
    ".txt",
}


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = [
            "id",
            "ticket",
            "file",
            "uploaded_by",
            "created_at",
        ]
        read_only_fields = ("id", "uploaded_by", "created_at")

    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError("Unsupported file type.")
        return value
