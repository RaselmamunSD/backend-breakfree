from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def default_grounding_quest_tasks():
    return [
        {"id": "green", "title": "Find 3 green things", "target": 3, "found": 0, "skipped": False},
        {"id": "lines", "title": "Find 2 straight lines", "target": 2, "found": 0, "skipped": False},
        {"id": "soft", "title": "Find 1 soft thing", "target": 1, "found": 0, "skipped": False},
    ]


class FeatureTutorial(TimeStampedModel):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    media_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=2)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "title"]


class DashboardShortcut(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shortcuts")
    name = models.CharField(max_length=80)
    icon_key = models.CharField(max_length=60, blank=True)
    target_route = models.CharField(max_length=120)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]


class CurrentJourney(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="current_journey")
    title = models.CharField(max_length=120, default="Foundation Journey")
    stage = models.CharField(max_length=60, default="Started")
    progress_percent = models.PositiveSmallIntegerField(default=0)
    target_days = models.PositiveIntegerField(default=30)
    completed_days = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)


class Prediction(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="predictions")
    risk_score = models.PositiveSmallIntegerField()
    confidence_score = models.PositiveSmallIntegerField(default=70)
    insight = models.CharField(max_length=255)
    recommendation = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]


class Forecast(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="forecasts")
    focus_area = models.CharField(max_length=80, default="Mood")
    forecast_date = models.DateField()
    mood_trend = models.CharField(max_length=80)
    stress_trend = models.CharField(max_length=80, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-forecast_date", "-created_at"]


class GroundingQuestSession(TimeStampedModel):
    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = (
        (STATUS_NOT_STARTED, "Not started"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_COMPLETED, "Completed"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grounding_sessions")
    title = models.CharField(max_length=120, default="Grounding Quest")
    subtitle = models.CharField(max_length=200, blank=True)
    grounding_type = models.CharField(max_length=60, default="room-scan")
    quest_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED)
    camera_enabled = models.BooleanField(default=False)
    task_progress = models.JSONField(default=default_grounding_quest_tasks)
    total_steps = models.PositiveSmallIntegerField(default=5)
    completed_steps = models.PositiveSmallIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=45)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class SOSModeEvent(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sos_events")
    is_active = models.BooleanField(default=True)
    trigger_reason = models.CharField(max_length=255, blank=True)
    safety_plan = models.TextField(blank=True)
    activated_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-activated_at"]


class SOSSession(TimeStampedModel):
    """Multi-step SOS flow: mode selection → breathe/ground → name-it → complete."""

    STEP_SELECT = "select_mode"
    STEP_BREATHE = "breathe"
    STEP_GROUNDING = "grounding"
    STEP_NAME_IT = "name_it"
    STEP_DONE = "done"
    STEP_CHOICES = (
        (STEP_SELECT, "Select mode"),
        (STEP_BREATHE, "Breathe"),
        (STEP_GROUNDING, "Grounding"),
        (STEP_NAME_IT, "Name it"),
        (STEP_DONE, "Done"),
    )

    MODE_BREATHE = "breathe"
    MODE_GROUNDING = "grounding"
    MODE_CHOICES = ((MODE_BREATHE, "Breathe"), (MODE_GROUNDING, "Grounding"))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sos_sessions")
    current_step = models.CharField(max_length=20, choices=STEP_CHOICES, default=STEP_SELECT)
    active_mode = models.CharField(max_length=20, choices=MODE_CHOICES, blank=True)
    breathe_cycles_completed = models.PositiveSmallIntegerField(default=0)
    grounding_see = models.TextField(blank=True)
    grounding_hear = models.TextField(blank=True)
    grounding_feel = models.TextField(blank=True)
    fear_statement = models.TextField(blank=True)
    next_action = models.TextField(blank=True)
    wants_sos_plus = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class ExposureLadder(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exposure_ladders")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]


class ExposureLadderStep(TimeStampedModel):
    ladder = models.ForeignKey(ExposureLadder, on_delete=models.CASCADE, related_name="steps")
    step_title = models.CharField(max_length=160)
    difficulty_level = models.PositiveSmallIntegerField(default=1)
    position = models.PositiveSmallIntegerField(default=1)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["position", "id"]


class ExposureItem(TimeStampedModel):
    """Single exposure card (category + task + difficulty) — matches Exposure Ladder UI."""

    STATUS_NOT_SCHEDULED = "not_scheduled"
    STATUS_SCHEDULED = "scheduled"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = (
        (STATUS_NOT_SCHEDULED, "Not scheduled"),
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_COMPLETED, "Completed"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exposure_items")
    category = models.CharField(max_length=120, blank=True)
    specific_exposure = models.TextField()
    difficulty_level = models.PositiveSmallIntegerField(default=5, help_text="1-10")
    ladder_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_SCHEDULED)
    check_in_note = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    distress_before = models.PositiveSmallIntegerField(null=True, blank=True)
    distress_after = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class UserSetting(TimeStampedModel):
    THEME_SYSTEM = "system"
    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    THEME_CHOICES = (
        (THEME_SYSTEM, "System"),
        (THEME_LIGHT, "Light"),
        (THEME_DARK, "Dark"),
    )

    ANALYTICS_PRIVATE = "private"
    ANALYTICS_SHARE = "share"
    ANALYTICS_CHOICES = (
        (ANALYTICS_PRIVATE, "Private"),
        (ANALYTICS_SHARE, "Share"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feature_settings")
    notifications_enabled = models.BooleanField(default=True)
    sound_enabled = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=False)
    theme_mode = models.CharField(max_length=20, choices=THEME_CHOICES, default=THEME_SYSTEM)
    selected_program_key = models.CharField(max_length=40, blank=True, help_text="e.g. quick_start_14, deep_dive_30")
    analytics_sharing = models.CharField(max_length=20, choices=ANALYTICS_CHOICES, default=ANALYTICS_SHARE)
    replay_tutorial_requested = models.BooleanField(default=False)
    demo_reset_at = models.DateTimeField(null=True, blank=True)
    language = models.CharField(max_length=10, default="en")


class PremiumPlan(TimeStampedModel):
    BILLING_CHOICES = (("monthly", "Monthly"), ("yearly", "Yearly"), ("lifetime", "Lifetime"))
    UI_OLD = "old"
    UI_NEW = "new"
    UI_CHOICES = ((UI_OLD, "Old layout"), (UI_NEW, "New layout"))

    name = models.CharField(max_length=80)
    plan_key = models.CharField(max_length=40, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CHOICES)
    badge_tag = models.CharField(max_length=40, blank=True, help_text="REGULAR, BEST VALUE, PREMIUM, …")
    sort_order = models.PositiveSmallIntegerField(default=0)
    ui_version = models.CharField(max_length=10, choices=UI_CHOICES, default=UI_NEW)
    is_legacy = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    feature_summary = models.TextField(blank=True)
    ios_product_id = models.CharField(max_length=120, blank=True, help_text="App Store subscription product id")
    google_product_id = models.CharField(max_length=120, blank=True, help_text="Google Play base plan / product id")

    class Meta:
        ordering = ["sort_order", "price"]


class PremiumSubscription(TimeStampedModel):
    STATUS_CHOICES = (("active", "Active"), ("expired", "Expired"), ("cancelled", "Cancelled"))
    PLATFORM_IOS = "ios"
    PLATFORM_ANDROID = "android"
    PLATFORM_CHOICES = (
        (PLATFORM_IOS, "iOS"),
        (PLATFORM_ANDROID, "Android"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="premium_subscriptions")
    plan = models.ForeignKey(PremiumPlan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    restored_at = models.DateTimeField(null=True, blank=True, help_text="Set when activated via restore-purchase.")
    store_platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, blank=True)
    store_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Opaque transaction / order id from the store client.",
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]


class GuestQuota(TimeStampedModel):
    """Tracks free-tier usage for unauthenticated clients (stable `X-Device-Id` header)."""

    device_id = models.CharField(max_length=128, unique=True, db_index=True)
    mood_logs_used = models.PositiveSmallIntegerField(default=0)
    fear_forecasts_used = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.device_id


class FearForecast(TimeStampedModel):
    """Fear / worry forecasts (Predict + Worry Forecast screens)."""

    STATUS_LIVE = "live"
    STATUS_EXPIRED = "expired"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = (
        (STATUS_LIVE, "Live"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_RESOLVED, "Resolved"),
    )

    PROOF_TONIGHT = "tonight"
    PROOF_TOMORROW = "tomorrow_morning"
    PROOF_AFTER_EVENT = "after_event"
    PROOF_NONE = "none"
    PROOF_CHOICES = (
        (PROOF_TONIGHT, "Tonight"),
        (PROOF_TOMORROW, "Tomorrow morning"),
        (PROOF_AFTER_EVENT, "After the event"),
        (PROOF_NONE, "No reminder"),
    )

    OUTCOME_SAFE = "safe"
    OUTCOME_HAPPENED = "happened"
    OUTCOME_CHOICES = (
        (OUTCOME_SAFE, "It was fine / safe"),
        (OUTCOME_HAPPENED, "It happened"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fear_forecasts",
        null=True,
        blank=True,
    )
    device_id = models.CharField(max_length=128, blank=True, db_index=True)
    title = models.CharField(max_length=200, blank=True)
    story_text = models.TextField(help_text="The scary 'what if' narrative")
    category = models.CharField(max_length=80, blank=True)
    belief_strength = models.PositiveSmallIntegerField(default=50, help_text="0-100")
    template_key = models.CharField(max_length=80, blank=True)
    proof_check_in = models.CharField(max_length=30, choices=PROOF_CHOICES, default=PROOF_NONE)
    likelihood_percent = models.PositiveSmallIntegerField(default=50)
    distress_level = models.PositiveSmallIntegerField(default=5, help_text="0-10")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_LIVE)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["device_id", "status"]),
        ]


class WorryForecastTemplate(TimeStampedModel):
    """Preset chips for quick worry logging."""

    key = models.SlugField(unique=True)
    label = models.CharField(max_length=200)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "label"]


class ProgramTrack(TimeStampedModel):
    """Journey program (e.g. 14-day Quick Start)."""

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=200, blank=True)
    total_days = models.PositiveSmallIntegerField(default=14)
    free_preview_days = models.PositiveSmallIntegerField(
        default=3,
        help_text="Days unlocked without premium; later days require premium.",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "title"]


class ProgramDay(TimeStampedModel):
    program = models.ForeignKey(ProgramTrack, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveSmallIntegerField()
    label_date = models.CharField(max_length=40, blank=True, help_text="Display-only date label")
    title = models.CharField(max_length=200)
    short_description = models.TextField(blank=True)
    content_body = models.TextField(blank=True)
    action_steps = models.JSONField(default=list)
    journal_prompts = models.JSONField(default=list)
    regulation_tool = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["program", "day_number"]
        unique_together = ("program", "day_number")


class UserProgramProgress(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="program_progress")
    program = models.ForeignKey(ProgramTrack, on_delete=models.CASCADE, related_name="user_progress")
    last_opened_day = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ("user", "program")


class UserDayCompletion(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="day_completions")
    day = models.ForeignKey(ProgramDay, on_delete=models.CASCADE, related_name="completions")

    class Meta:
        unique_together = ("user", "day")


class CBTTip(TimeStampedModel):
    body = models.TextField()
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]


class AppContent(TimeStampedModel):
    """Key/value JSON: emergency numbers, social URLs, premium preview, feature flags."""

    key = models.SlugField(unique=True)
    payload = models.JSONField(default=dict)

    class Meta:
        ordering = ["key"]
