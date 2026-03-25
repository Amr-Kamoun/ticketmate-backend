from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "client", "project_type", "project_owner", "created_at")
    search_fields = ("name", "client__name", "project_owner__username", "project_owner__email")
    list_filter = ("project_type", "created_at")