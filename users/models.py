from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    PROJECT_OWNER = "PROJECT_OWNER", "Project Owner"
    EMPLOYEE = "EMPLOYEE", "Employee"
    CLIENT = "CLIENT", "Client"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
    )

    def __str__(self):
        return self.username
