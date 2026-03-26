from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    PROJECT_OWNER = "PROJECT_OWNER", "Project Owner"
    EMPLOYEE = "EMPLOYEE", "Employee"
    CLIENT = "CLIENT", "Client"
