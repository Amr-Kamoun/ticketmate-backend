from tickets.models import Ticket
from users.models import UserRole


def can_create_ticket(user, project):
    if not user.is_authenticated:
        return False

    if user.role == UserRole.ADMIN:
        return True

    if user.role == UserRole.PROJECT_OWNER and project.project_owner == user:
        return True

    if user.role == UserRole.EMPLOYEE:
        return project.team_members.filter(id=user.id).exists()

    if user.role == UserRole.CLIENT and user.client == project.client:
        return True

    return False


def user_can_access_ticket(user, ticket):
    if not user.is_authenticated:
        return False

    if user.role == UserRole.ADMIN:
        return True

    if user.role == UserRole.PROJECT_OWNER and ticket.project.project_owner == user:
        return True

    if user.role == UserRole.EMPLOYEE:
        return ticket.project.team_members.filter(id=user.id).exists()

    if user.role == UserRole.CLIENT and user.client == ticket.project.client:
        return True

    return False


def get_accessible_tickets(user):
    if not user.is_authenticated:
        return Ticket.objects.none()

    if user.role == UserRole.ADMIN:
        return Ticket.objects.all()

    if user.role == UserRole.PROJECT_OWNER:
        return Ticket.objects.filter(project__project_owner=user)

    if user.role == UserRole.EMPLOYEE:
        return Ticket.objects.filter(project__team_members=user).distinct()

    if user.role == UserRole.CLIENT and user.client_id:
        return Ticket.objects.filter(project__client=user.client)

    return Ticket.objects.none()
