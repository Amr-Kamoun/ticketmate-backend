from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from notifications.email_service import send_notification_email
from users.choices import UserRole

User = get_user_model()


class NotificationEmailServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="User12345!",
            full_name="User One",
            role=UserRole.EMPLOYEE,
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_send_notification_email_returns_one_for_valid_recipient(self):
        result = send_notification_email(
            recipient=self.user,
            subject="Test Notification",
            message="This is a test email.",
        )

        self.assertEqual(result, 1)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_send_notification_email_returns_zero_when_recipient_has_no_email(self):
        self.user.email = ""
        self.user.save(update_fields=["email"])

        result = send_notification_email(
            recipient=self.user,
            subject="Test Notification",
            message="This is a test email.",
        )

        self.assertEqual(result, 0)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_send_notification_email_returns_zero_when_recipient_is_none(self):
        result = send_notification_email(
            recipient=None,
            subject="Test Notification",
            message="This is a test email.",
        )

        self.assertEqual(result, 0)