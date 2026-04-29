from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user,
            title="Test Notification",
            message="This is a test notification",
            notification_type="info"
        )
        self.assertEqual(notification.title, "Test Notification")
        self.assertFalse(notification.is_read)
