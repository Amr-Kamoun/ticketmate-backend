from rest_framework import serializers

from ticket_messages.helpers import validate_ticket_message_payload
from ticket_messages.models import TicketMessage


class TicketMessageSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = TicketMessage
        fields = [
            "id",
            "ticket",
            "author",
            "author_name",
            "author_username",
            "body",
            "is_internal",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "author_name",
            "author_username",
            "created_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        ticket = attrs.get("ticket") or getattr(self.instance, "ticket", None)
        is_internal = attrs.get(
            "is_internal",
            getattr(self.instance, "is_internal", False),
        )
        body = attrs.get("body")

        errors = validate_ticket_message_payload(
            user=user,
            ticket=ticket,
            is_internal=is_internal,
            body=body,
        )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
