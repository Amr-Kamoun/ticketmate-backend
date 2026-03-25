from django.db import models
from clients.models import Client
from users.models import User
from common.choices import ProjectType, UserRole


class Project(models.Model):
    name = models.CharField(max_length=255)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    project_type = models.CharField(
        max_length=30,
        choices=ProjectType.choices,
    )
    project_owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        limit_choices_to={"role": UserRole.PROJECT_OWNER},
    )
    team_members = models.ManyToManyField(
        User,
        related_name="assigned_projects",
        blank=True,
        limit_choices_to={"role": UserRole.EMPLOYEE},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("client", "name")

    def __str__(self):
        return self.name