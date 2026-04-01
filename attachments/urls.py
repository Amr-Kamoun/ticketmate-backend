from django.urls import path

from attachments.views import AttachmentUploadAPIView

app_name = "attachments"

urlpatterns = [
    path(
        "tickets/<int:ticket_id>/attachments/",
        AttachmentUploadAPIView.as_view(),
        name="attachment-upload",
    ),
]
