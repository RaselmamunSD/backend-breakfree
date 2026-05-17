from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification, FCMDevice
from .fcm import send_push_notification

@receiver(post_save, sender=Notification)
def send_fcm_notification(sender, instance, created, **kwargs):
    if created:
        devices = FCMDevice.objects.filter(user=instance.user, is_active=True)
        for device in devices:
            send_push_notification(
                token=device.token,
                title=instance.title,
                body=instance.message,
                data={
                    "notification_id": str(instance.id),
                    "notification_type": instance.notification_type,
                    "action_url": instance.action_url or ""
                }
            )
