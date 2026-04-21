from django.conf import settings
from django.db import models


class SubscriptionTier(models.Model):
    """Onboarding subscription path cards (e.g. Quiet Peaks, Constant Flow)."""

    slug = models.SlugField(unique=True)
    frequency_badge = models.CharField(
        max_length=32,
        blank=True,
        help_text="e.g. RARE, OCCASIONAL — shown before the name like “RARE: Quiet Peaks”",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon_key = models.CharField(max_length=64, blank=True, help_text="Client-side icon identifier")
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    @property
    def display_line(self) -> str:
        if self.frequency_badge:
            return f"{self.frequency_badge}: {self.name}"
        return self.name


class JourneyProgram(models.Model):
    """Starting programs (e.g. The Foundation, The Transformation)."""

    slug = models.SlugField(unique=True)
    journey_badge = models.CharField(
        max_length=120,
        blank=True,
        help_text="e.g. “14 DAYS OF GENTLE GROWTH” — upper line on the program card",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    cover_image_url = models.URLField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    @property
    def display_title(self) -> str:
        if self.journey_badge:
            return f"{self.journey_badge}: {self.name}"
        return self.name


class UserOnboarding(models.Model):
    STEP_SAFETY = "safety"
    STEP_SUBSCRIPTION = "subscription"
    STEP_PROGRAM = "program"
    STEP_COMPLETED = "completed"
    STEP_CHOICES = (
        (STEP_SAFETY, "Safety"),
        (STEP_SUBSCRIPTION, "Subscription tier"),
        (STEP_PROGRAM, "Program"),
        (STEP_COMPLETED, "Completed"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="onboarding",
    )
    current_step = models.CharField(max_length=20, choices=STEP_CHOICES, default=STEP_SAFETY)
    safety_agreed_at = models.DateTimeField(null=True, blank=True)
    safety_content_version = models.CharField(max_length=20, default="1.0")
    selected_tier = models.ForeignKey(
        SubscriptionTier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="onboarding_selections",
    )
    selected_program = models.ForeignKey(
        JourneyProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="onboarding_selections",
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User onboarding"
        verbose_name_plural = "User onboardings"

    def __str__(self):
        return f"{self.user.username} — {self.current_step}"

    @property
    def is_completed(self) -> bool:
        return self.current_step == self.STEP_COMPLETED and self.completed_at is not None
