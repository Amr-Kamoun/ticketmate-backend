from django.urls import path

from ticket_messages.views import TicketMessageListCreateAPIView

app_name = "ticket_messages"

urlpatterns = [
    path(
        "tickets/<int:ticket_id>/",
        TicketMessageListCreateAPIView.as_view(),
        name="ticket-message-list-create",
    ),
]
