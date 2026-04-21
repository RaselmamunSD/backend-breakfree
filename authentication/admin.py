from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import OTPVerification, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("full_name", "phone", "avatar", "is_verified")}),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ("email", "purpose", "code", "expires_at", "is_used", "created_at")
    list_filter = ("purpose", "is_used")
    search_fields = ("email", "code")
