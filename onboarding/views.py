from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JourneyProgram, SubscriptionTier, UserOnboarding
from .serializers import (
    JourneyProgramSerializer,
    SafetyAgreeSerializer,
    SelectProgramSerializer,
    SelectTierSerializer,
    SubscriptionTierSerializer,
    UserOnboardingSerializer,
)


def get_or_create_onboarding(user) -> UserOnboarding:
    obj, _ = UserOnboarding.objects.get_or_create(user=user)
    return obj


class SubscriptionTierListView(generics.ListAPIView):
    serializer_class = SubscriptionTierSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = SubscriptionTier.objects.filter(is_active=True)


class JourneyProgramListView(generics.ListAPIView):
    serializer_class = JourneyProgramSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = JourneyProgram.objects.filter(is_active=True)


class OnboardingStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ob = get_or_create_onboarding(request.user)
        return Response(UserOnboardingSerializer(ob).data)


class OnboardingSafetyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = SafetyAgreeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        if not ser.validated_data["agreed"]:
            return Response({"detail": "You must agree to continue."}, status=status.HTTP_400_BAD_REQUEST)

        ob = get_or_create_onboarding(request.user)
        if ob.current_step != UserOnboarding.STEP_SAFETY:
            return Response(
                {"detail": "Safety step already completed.", "onboarding": UserOnboardingSerializer(ob).data},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ob.safety_agreed_at = timezone.now()
        ob.safety_content_version = ser.validated_data.get("content_version", "1.0")
        ob.current_step = UserOnboarding.STEP_SUBSCRIPTION
        ob.save(update_fields=["safety_agreed_at", "safety_content_version", "current_step", "updated_at"])
        return Response(UserOnboardingSerializer(ob).data, status=status.HTTP_200_OK)


class OnboardingSelectTierView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = SelectTierSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        slug = ser.validated_data["tier_slug"]
        tier = SubscriptionTier.objects.filter(slug=slug, is_active=True).first()
        if not tier:
            return Response({"detail": "Unknown or inactive tier."}, status=status.HTTP_400_BAD_REQUEST)

        ob = get_or_create_onboarding(request.user)
        if ob.current_step == UserOnboarding.STEP_SAFETY:
            return Response({"detail": "Complete the safety step first."}, status=status.HTTP_400_BAD_REQUEST)
        if ob.current_step == UserOnboarding.STEP_COMPLETED:
            return Response({"detail": "Onboarding already completed."}, status=status.HTTP_400_BAD_REQUEST)

        ob.selected_tier = tier
        if ob.current_step == UserOnboarding.STEP_SUBSCRIPTION:
            ob.current_step = UserOnboarding.STEP_PROGRAM
        ob.save(update_fields=["selected_tier", "current_step", "updated_at"])
        return Response(UserOnboardingSerializer(ob).data, status=status.HTTP_200_OK)


class OnboardingSelectProgramView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = SelectProgramSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        slug = ser.validated_data["program_slug"]
        program = JourneyProgram.objects.filter(slug=slug, is_active=True).first()
        if not program:
            return Response({"detail": "Unknown or inactive program."}, status=status.HTTP_400_BAD_REQUEST)

        ob = get_or_create_onboarding(request.user)
        if ob.current_step in (UserOnboarding.STEP_SAFETY, UserOnboarding.STEP_SUBSCRIPTION):
            return Response({"detail": "Complete previous steps first."}, status=status.HTTP_400_BAD_REQUEST)
        if ob.current_step == UserOnboarding.STEP_COMPLETED:
            return Response({"detail": "Onboarding already completed."}, status=status.HTTP_400_BAD_REQUEST)

        ob.selected_program = program
        ob.current_step = UserOnboarding.STEP_COMPLETED
        ob.completed_at = timezone.now()
        ob.save(
            update_fields=["selected_program", "current_step", "completed_at", "updated_at"]
        )
        return Response(UserOnboardingSerializer(ob).data, status=status.HTTP_200_OK)
