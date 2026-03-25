from rest_framework import serializers
from tickets.models import Ticket, TicketStatus


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        if instance and instance.status == TicketStatus.CLOSED:
            raise serializers.ValidationError("Closed tickets cannot be edited.")

        return attrs