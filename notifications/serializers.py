from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "ticket",
            "notification_type",
            "message",
            "is_read",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "ticket",
            "notification_type",
            "message",
            "created_at",
        ]
