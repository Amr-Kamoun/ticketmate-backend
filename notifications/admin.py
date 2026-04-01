from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipient",
        "ticket",
        "notification_type",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = (
        "recipient__username",
        "recipient__full_name",
        "ticket__title",
        "message",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)