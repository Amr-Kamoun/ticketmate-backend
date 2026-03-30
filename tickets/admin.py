from django.contrib import admin

from tickets.models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "ticket_type",
        "priority",
        "status",
        "project",
        "created_by",
        "assigned_to",
        "created_at",
    )
    list_filter = ("ticket_type", "priority", "status", "project")
    search_fields = ("title", "description")
