from users.models import UserRole


def can_create_ticket(user, project):
    if not user.is_authenticated:
        return False

    if user.role == UserRole.ADMIN:
        return True

    if project.project_owner == user:
        return True

    if (
        hasattr(project, "team_members")
        and project.team_members.filter(id=user.id).exists()
    ):
        return True

    return False


def user_can_access_ticket(user, ticket):
    if not user.is_authenticated:
        return False

    if user.role == UserRole.ADMIN:
        return True

    if ticket.project.project_owner == user:
        return True

    if ticket.assigned_to == user:
        return True

    if (
        hasattr(ticket.project, "team_members")
        and ticket.project.team_members.filter(id=user.id).exists()
    ):
        return True

    return False
