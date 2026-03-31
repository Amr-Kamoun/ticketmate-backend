from django.contrib import admin

from attachments.models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "uploaded_by", "created_at")
    search_fields = ("ticket__title", "uploaded_by__username", "uploaded_by__email")
