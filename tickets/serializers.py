from rest_framework import serializers

from tickets.models import Ticket, TicketStatus


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "ticket_type",
            "priority",
            "status",
            "project",
            "created_by",
            "assigned_to",
            "linked_ticket",
            "created_at",
            "updated_at",
            "resolved_at",
            "closed_at",
        ]
        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "resolved_at",
            "closed_at",
        )

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        if instance and instance.status == TicketStatus.CLOSED:
            raise serializers.ValidationError("Closed tickets cannot be edited.")

        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("status", None)
        validated_data.pop("assigned_to", None)
        validated_data.pop("linked_ticket", None)
        return super().update(instance, validated_data)
