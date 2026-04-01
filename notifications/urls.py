from django.urls import path

from notifications.views import NotificationListAPIView, NotificationMarkAsReadAPIView

app_name = "notifications"

urlpatterns = [
    path("", NotificationListAPIView.as_view(), name="notification-list"),
    path(
        "<int:pk>/read/",
        NotificationMarkAsReadAPIView.as_view(),
        name="notification-mark-read",
    ),
]