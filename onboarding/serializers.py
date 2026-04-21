from rest_framework import serializers

from .models import JourneyProgram, SubscriptionTier, UserOnboarding


class SubscriptionTierSerializer(serializers.ModelSerializer):
    display_line = serializers.ReadOnlyField()

    class Meta:
        model = SubscriptionTier
        fields = (
            "id",
            "slug",
            "frequency_badge",
            "name",
            "display_line",
            "description",
            "icon_key",
            "sort_order",
        )


class JourneyProgramSerializer(serializers.ModelSerializer):
    display_title = serializers.ReadOnlyField()

    class Meta:
        model = JourneyProgram
        fields = (
            "id",
            "slug",
            "journey_badge",
            "name",
            "display_title",
            "description",
            "cover_image_url",
            "sort_order",
        )


class UserOnboardingSerializer(serializers.ModelSerializer):
    selected_tier_detail = SubscriptionTierSerializer(source="selected_tier", read_only=True)
    selected_program_detail = JourneyProgramSerializer(source="selected_program", read_only=True)
    is_completed = serializers.ReadOnlyField()

    class Meta:
        model = UserOnboarding
        fields = (
            "current_step",
            "safety_agreed_at",
            "safety_content_version",
            "selected_tier",
            "selected_program",
            "selected_tier_detail",
            "selected_program_detail",
            "completed_at",
            "is_completed",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "safety_agreed_at",
            "completed_at",
            "created_at",
            "updated_at",
        )


class SafetyAgreeSerializer(serializers.Serializer):
    agreed = serializers.BooleanField()
    content_version = serializers.CharField(required=False, default="1.0", max_length=20)


class SelectTierSerializer(serializers.Serializer):
    tier_slug = serializers.SlugField()


class SelectProgramSerializer(serializers.Serializer):
    program_slug = serializers.SlugField()
