from django.db import models


class TicketType(models.TextChoices):
    PROBLEM = "PROBLEM", "Problem"
    INQUIRY = "INQUIRY", "Inquiry"
    NEW_REQUEST = "NEW_REQUEST", "New Request"


class TicketPriority(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class TicketStatus(models.TextChoices):
    TODO = "TODO", "Todo"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    RESOLVED = "RESOLVED", "Resolved"
    CLOSED = "CLOSED", "Closed"