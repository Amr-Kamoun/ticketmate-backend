from django.contrib.auth.models import AbstractUser
from django.db import models

from users.choices import UserRole


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    def __str__(self):
        return self.username
