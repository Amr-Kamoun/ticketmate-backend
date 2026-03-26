from django.db import models


class ProjectType(models.TextChoices):
    ORACLE_SUPPORT = "ORACLE_SUPPORT", "Oracle Support"
    SOFTWARE_SUPPORT = "SOFTWARE_SUPPORT", "Software Support"
    OPEN_SOURCE_SUPPORT = "OPEN_SOURCE_SUPPORT", "Open-Source Support"
