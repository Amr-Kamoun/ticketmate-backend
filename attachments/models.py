from django.conf import settings
from django.db import models

from tickets.models import Ticket


class Attachment(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(upload_to="attachments/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_attachments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment #{self.id} for Ticket #{self.ticket_id}"
