from django.contrib import admin

from .models import JourneyProgram, SubscriptionTier, UserOnboarding


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ("name", "frequency_badge", "slug", "sort_order", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")


@admin.register(JourneyProgram)
class JourneyProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "journey_badge", "slug", "sort_order", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")


@admin.register(UserOnboarding)
class UserOnboardingAdmin(admin.ModelAdmin):
    list_display = ("user", "current_step", "safety_agreed_at", "completed_at", "updated_at")
    list_filter = ("current_step",)
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user", "selected_tier", "selected_program")
