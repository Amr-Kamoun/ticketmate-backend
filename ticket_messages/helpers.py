from tickets.helpers import user_can_access_ticket
from users.choices import UserRole

STAFF_MESSAGE_ROLES = {
    UserRole.ADMIN,
    UserRole.PROJECT_OWNER,
    UserRole.EMPLOYEE,
}


def validate_ticket_message_payload(*, user, ticket, is_internal, body):
    errors = {}

    if not user or not user.is_authenticated:
        errors["detail"] = "Authentication is required."
        return errors

    if not ticket:
        errors["ticket"] = "This field is required."
        return errors

    if not user_can_access_ticket(user, ticket):
        errors["detail"] = "You do not have access to this ticket."

    if is_internal and user.role not in STAFF_MESSAGE_ROLES:
        errors["is_internal"] = "Only staff users can create internal messages."

    if body is not None and not body.strip():
        errors["body"] = "Message body cannot be empty."

    return errors
