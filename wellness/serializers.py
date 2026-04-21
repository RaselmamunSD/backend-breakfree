from rest_framework import serializers

from .models import (
    BreathingSession,
    Habit,
    JournalEntry,
    MoodEntry,
    SubscriptionPlan,
    UserPreference,
    UserSubscription,
)


class MoodEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodEntry
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")

    def validate_mood_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Mood score must be between 1 and 10.")
        return value


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class BreathingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreathingSession
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_detail = SubscriptionPlanSerializer(source="plan", read_only=True)

    class Meta:
        model = UserSubscription
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")
