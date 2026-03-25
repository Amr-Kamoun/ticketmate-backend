from django.conf import settings
from django.db import models

from tickets.choices import TicketType, TicketPriority, TicketStatus


class Ticket(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    ticket_type = models.CharField(
        max_length=20,
        choices=TicketType.choices,
        default=TicketType.PROBLEM,
    )

    priority = models.CharField(
        max_length=20,
        choices=TicketPriority.choices,
        default=TicketPriority.MEDIUM,
    )

    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.TODO,
    )

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tickets",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        null=True,
        blank=True,
    )

    linked_ticket = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="related_tickets",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status}"