from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MoodEntry(TimeStampedModel):
    MOOD_LABEL_CHOICES = (
        ("terrible", "Terrible"),
        ("bad", "Bad"),
        ("okay", "Okay"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="moods")
    mood_score = models.PositiveSmallIntegerField(help_text="1 to 10")
    mood_label = models.CharField(max_length=20, choices=MOOD_LABEL_CHOICES, blank=True)
    note = models.TextField(blank=True)
    entry_date = models.DateField()

    class Meta:
        ordering = ["-entry_date", "-created_at"]
        unique_together = ("user", "entry_date")

    def __str__(self):
        return f"{self.user.username} - {self.entry_date}"


class JournalEntry(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journals")
    title = models.CharField(max_length=120)
    content = models.TextField()
    is_private = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class BreathingExercise(TimeStampedModel):
    """Catalog of breathwork patterns (Box, 4-7-8, etc.) — timing lives in `phases` JSON."""

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    duration_minutes = models.PositiveSmallIntegerField(default=4)
    total_cycles = models.PositiveSmallIntegerField(default=10)
    difficulty_tag = models.CharField(max_length=40, blank=True, help_text="e.g. BEGINNER, ADVANCED")
    intensity_level = models.PositiveSmallIntegerField(default=1, help_text="1-4 dots in UI")
    theme_color = models.CharField(max_length=20, blank=True, help_text="teal, pink, …")
    phases = models.JSONField(default=list, help_text="List of {phase, seconds} e.g. inhale/hold/exhale")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class BreathingSession(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="breathing_sessions")
    exercise = models.ForeignKey(
        BreathingExercise,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
    )
    duration_seconds = models.PositiveIntegerField(default=60)
    cycles_completed = models.PositiveSmallIntegerField(default=0)
    completed = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]


class Habit(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=120)
    target_per_day = models.PositiveSmallIntegerField(default=1)
    streak = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class SubscriptionPlan(TimeStampedModel):
    PLAN_TYPE_CHOICES = (
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("lifetime", "Lifetime"),
    )

    name = models.CharField(max_length=120)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_label = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} ({self.plan_type})"


class UserSubscription(TimeStampedModel):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name="user_subscriptions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"


class UserPreference(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preference")
    daily_reminder = models.BooleanField(default=True)
    reminder_time = models.TimeField(null=True, blank=True)
    motivational_notification = models.BooleanField(default=True)
    quote_notification = models.BooleanField(default=True)
    theme = models.CharField(max_length=20, default="light")

    def __str__(self):
        return f"Preferences for {self.user.username}"
