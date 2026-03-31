from django.urls import path

from attachments.views import AttachmentUploadAPIView

app_name = "attachments"

urlpatterns = [
    path("upload/", AttachmentUploadAPIView.as_view(), name="attachment-upload"),
]
