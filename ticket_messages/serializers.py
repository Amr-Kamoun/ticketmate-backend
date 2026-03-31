from rest_framework import serializers

from ticket_messages.models import TicketMessage
from tickets.helpers import user_can_access_ticket
from users.choices import UserRole


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

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")

        if not ticket:
            raise serializers.ValidationError({"ticket": "This field is required."})

        if not user_can_access_ticket(user, ticket):
            raise serializers.ValidationError(
                {"detail": "You do not have access to this ticket."}
            )

        if is_internal and user.role not in {
            UserRole.ADMIN,
            UserRole.PROJECT_OWNER,
            UserRole.EMPLOYEE,
        }:
            raise serializers.ValidationError(
                {"is_internal": "Only staff users can create internal messages."}
            )

        if body is not None and not body.strip():
            raise serializers.ValidationError({"body": "Message body cannot be empty."})

        return attrs
