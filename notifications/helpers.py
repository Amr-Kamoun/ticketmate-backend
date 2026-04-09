from notifications.choices import NotificationType
from notifications.email_service import send_notification_email
from notifications.models import Notification
from tickets.choices import TicketStatus
from users.choices import UserRole


def create_notification(*, recipient, ticket, notification_type, message):
    if not recipient:
        return None

    notification = Notification.objects.create(
        recipient=recipient,
        ticket=ticket,
        notification_type=notification_type,
        message=message,
    )

    try:
        send_notification_email(
            recipient=recipient,
            subject=f"TicketMate Notification: {notification.get_notification_type_display()}",
            message=message,
        )
    except Exception:
        pass

    return notification


def create_ticket_created_notifications(ticket):
    recipients = []

    if ticket.project.project_owner:
        recipients.append(ticket.project.project_owner)

    notifications = []
    for recipient in recipients:
        if recipient == ticket.created_by:
            continue

        notification = create_notification(
            recipient=recipient,
            ticket=ticket,
            notification_type=NotificationType.TICKET_CREATED,
            message=f"A new ticket '{ticket.title}' was created.",
        )
        if notification:
            notifications.append(notification)

    return notifications


def create_ticket_assigned_notification(ticket):
    if not ticket.assigned_to:
        return None

    if ticket.assigned_to == ticket.created_by:
        return None

    return create_notification(
        recipient=ticket.assigned_to,
        ticket=ticket,
        notification_type=NotificationType.TICKET_ASSIGNED,
        message=f"You were assigned to ticket '{ticket.title}'.",
    )


def create_new_message_notifications(message_obj):
    ticket = message_obj.ticket
    sender = message_obj.author

    recipients = set()

    if ticket.project.project_owner and ticket.project.project_owner != sender:
        recipients.add(ticket.project.project_owner)

    if ticket.assigned_to and ticket.assigned_to != sender:
        recipients.add(ticket.assigned_to)

    if ticket.created_by != sender:
        if not message_obj.is_internal or ticket.created_by.role != UserRole.CLIENT:
            recipients.add(ticket.created_by)

    notifications = []
    for recipient in recipients:
        if message_obj.is_internal and recipient.role == UserRole.CLIENT:
            continue

        notification = create_notification(
            recipient=recipient,
            ticket=ticket,
            notification_type=NotificationType.NEW_MESSAGE,
            message=f"A new message was added to ticket '{ticket.title}'.",
        )
        if notification:
            notifications.append(notification)

    return notifications


def create_ticket_status_notification(ticket):
    if ticket.status == TicketStatus.RESOLVED:
        notification_type = NotificationType.TICKET_RESOLVED
        message = f"Ticket '{ticket.title}' was resolved."
    elif ticket.status == TicketStatus.CLOSED:
        notification_type = NotificationType.TICKET_CLOSED
        message = f"Ticket '{ticket.title}' was closed."
    else:
        return []

    recipients = set()

    if ticket.created_by:
        recipients.add(ticket.created_by)

    if ticket.project.project_owner:
        recipients.add(ticket.project.project_owner)

    if ticket.assigned_to:
        recipients.add(ticket.assigned_to)

    notifications = []
    for recipient in recipients:
        notification = create_notification(
            recipient=recipient,
            ticket=ticket,
            notification_type=notification_type,
            message=message,
        )
        if notification:
            notifications.append(notification)

    return notifications
