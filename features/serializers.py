from django.contrib.auth import get_user_model
from rest_framework import serializers

from wellness.models import BreathingExercise, JournalEntry, MoodEntry

from .models import (
    AppContent,
    CBTTip,
    CurrentJourney,
    DashboardShortcut,
    ExposureItem,
    ExposureLadder,
    ExposureLadderStep,
    FearForecast,
    FeatureTutorial,
    Forecast,
    GroundingQuestSession,
    Prediction,
    PremiumPlan,
    PremiumSubscription,
    ProgramDay,
    ProgramTrack,
    SOSSession,
    SOSModeEvent,
    UserDayCompletion,
    UserProgramProgress,
    UserSetting,
    WorryForecastTemplate,
)

User = get_user_model()


class FeatureTutorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureTutorial
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class DashboardShortcutSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardShortcut
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class CurrentJourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentJourney
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class GroundingQuestSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroundingQuestSession
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class SOSModeEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSModeEvent
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at", "activated_at")


class SOSSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSSession
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class ExposureLadderStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExposureLadderStep
        fields = "__all__"
        read_only_fields = ("ladder", "created_at", "updated_at")


class ExposureLadderSerializer(serializers.ModelSerializer):
    steps = ExposureLadderStepSerializer(many=True, read_only=True)

    class Meta:
        model = ExposureLadder
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class ExposureItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExposureItem
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")

    def validate_difficulty_level(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Difficulty must be 1-10.")
        return value


class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class PremiumPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumPlan
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class PremiumSubscriptionSerializer(serializers.ModelSerializer):
    plan_detail = PremiumPlanSerializer(source="plan", read_only=True)

    class Meta:
        model = PremiumSubscription
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class RestorePurchaseSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=("ios", "android"))
    product_id = serializers.CharField(required=False, allow_blank=True, default="")
    purchase_token = serializers.CharField(required=False, allow_blank=True, default="")
    transaction_id = serializers.CharField(required=False, allow_blank=True, default="")
    plan_key = serializers.CharField(required=False, allow_blank=True, default="")


class FearForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = FearForecast
        fields = "__all__"
        read_only_fields = ("user", "device_id", "created_at", "updated_at", "resolved_at")

    def validate_belief_strength(self, value):
        if value > 100:
            raise serializers.ValidationError("Must be 0-100.")
        return value

    def validate_likelihood_percent(self, value):
        if value > 100:
            raise serializers.ValidationError("Must be 0-100.")
        return value

    def validate_distress_level(self, value):
        if value > 10:
            raise serializers.ValidationError("Must be 0-10.")
        return value


class WorryForecastTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorryForecastTemplate
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class ProgramTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramTrack
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class ProgramDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramDay
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class UserProgramProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgramProgress
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class CBTTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CBTTip
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class AppContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppContent
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class MoodLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodEntry
        fields = ("id", "mood_score", "mood_label", "note", "entry_date", "created_at")
        read_only_fields = ("id", "created_at")


class JournalLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ("id", "title", "content", "is_private", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "full_name", "phone", "avatar", "is_verified")
        read_only_fields = ("id", "username", "email", "full_name", "phone", "avatar", "is_verified")
