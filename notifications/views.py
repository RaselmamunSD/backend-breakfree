from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    lookup_value_regex = r'\d+'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Return notifications for the authenticated user."""
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for the authenticated user."""
        notifications = self.get_queryset().filter(is_read=False)
        updated_count = notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({
            "message": f"{updated_count} notifications marked as read",
            "updated_count": updated_count
        })

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        """Mark a specific notification as read."""
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get count of unread notifications."""
        unread_count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": unread_count})
