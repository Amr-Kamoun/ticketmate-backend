from django.db import models
from django.contrib.auth.models import AbstractUser

#placeholder for custom user and roles
class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    PROJECT_OWNER = "PROJECT_OWNER", "Project Owner"
    SUPPORT_EMPLOYEE = "SUPPORT_EMPLOYEE", "Support Employee"
    CLIENT_USER = "CLIENT_USER", "Client User"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.CLIENT_USER,
    )

    def __str__(self):
        return self.username