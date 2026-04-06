from django.db.models import Count

from projects.models import Project
from tickets.choices import TicketStatus
from tickets.models import Ticket


def get_dashboard_stats():
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.exclude(status=TicketStatus.CLOSED).count()
    resolved_tickets = Ticket.objects.filter(status=TicketStatus.RESOLVED).count()
    closed_tickets = Ticket.objects.filter(status=TicketStatus.CLOSED).count()

    tickets_by_priority = list(
        Ticket.objects.values("priority")
        .annotate(count=Count("id"))
        .order_by("priority")
    )

    tickets_by_project = list(
        Ticket.objects.values("project__id", "project__name")
        .annotate(count=Count("id"))
        .order_by("project__name")
    )

    tickets_by_status = list(
        Ticket.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    tickets_per_employee = list(
        Ticket.objects.filter(assigned_to__isnull=False)
        .values(
            "assigned_to__id",
            "assigned_to__username",
            "assigned_to__full_name",
        )
        .annotate(count=Count("id"))
        .order_by("assigned_to__username")
    )

    resolved_tickets_qs = Ticket.objects.filter(resolved_at__isnull=False)
    resolution_durations = [
        max((ticket.resolved_at - ticket.created_at).total_seconds(), 0)
        for ticket in resolved_tickets_qs
    ]
    average_resolution_time_seconds = (
        sum(resolution_durations) / len(resolution_durations)
        if resolution_durations
        else 0
    )

    active_projects_count = Project.objects.count()

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets,
        "tickets_by_priority": tickets_by_priority,
        "tickets_by_project": tickets_by_project,
        "tickets_by_status": tickets_by_status,
        "tickets_per_employee": tickets_per_employee,
        "active_projects_count": active_projects_count,
        "average_resolution_time_seconds": average_resolution_time_seconds,
    }