from django.urls import path
from .views import (
    TicketListAPIView,
    TicketCreateAPIView,
    TicketDetailAPIView,
    TicketAssignAPIView,
    TicketStatusUpdateAPIView,
    TicketLinkAPIView,
)

app_name = "tickets"

urlpatterns = [
    path("", TicketListAPIView.as_view(), name="ticket-list"),
    path("create/", TicketCreateAPIView.as_view(), name="ticket-create"),
    path("<int:pk>/", TicketDetailAPIView.as_view(), name="ticket-detail"),
    path("<int:pk>/assign/", TicketAssignAPIView.as_view(), name="ticket-assign"),
    path("<int:pk>/status/", TicketStatusUpdateAPIView.as_view(), name="ticket-status-update"),
    path("<int:pk>/link/", TicketLinkAPIView.as_view(), name="ticket-link"),
]