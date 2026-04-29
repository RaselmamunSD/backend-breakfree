from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    readonly_fields = ("created_at", "updated_at", "read_at")
    fieldsets = (
        ("User Info", {"fields": ("user",)}),
        ("Content", {"fields": ("title", "message")}),
        ("Type & Status", {"fields": ("notification_type", "is_read")}),
        ("Links", {"fields": ("action_url",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "read_at")}),
    )
