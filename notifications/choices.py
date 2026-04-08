from django.db import models


class NotificationType(models.TextChoices):
    TICKET_CREATED = "TICKET_CREATED", "Ticket Created"
    TICKET_ASSIGNED = "TICKET_ASSIGNED", "Ticket Assigned"
    NEW_MESSAGE = "NEW_MESSAGE", "New Message"
    TICKET_RESOLVED = "TICKET_RESOLVED", "Ticket Resolved"
    TICKET_CLOSED = "TICKET_CLOSED", "Ticket Closed"
