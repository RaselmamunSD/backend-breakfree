from rest_framework import serializers

from .models import Notification, FCMDevice


class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ["id", "token", "device_type", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        token = validated_data.get("token")
        
        # If the token already exists, update user and device_type, otherwise create new
        device, created = FCMDevice.objects.update_or_create(
            token=token,
            defaults={
                "user": user,
                "device_type": validated_data.get("device_type", "android"),
                "is_active": validated_data.get("is_active", True)
            }
        )
        return device


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "read_at",
            "action_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "read_at"]
