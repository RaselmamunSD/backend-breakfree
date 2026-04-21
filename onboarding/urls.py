from django.urls import path

from .views import (
    JourneyProgramListView,
    OnboardingSafetyView,
    OnboardingSelectProgramView,
    OnboardingSelectTierView,
    OnboardingStatusView,
    SubscriptionTierListView,
)

urlpatterns = [
    path("onboarding/status/", OnboardingStatusView.as_view(), name="onboarding-status"),
    path("onboarding/safety/", OnboardingSafetyView.as_view(), name="onboarding-safety"),
    path("onboarding/subscription-tier/", OnboardingSelectTierView.as_view(), name="onboarding-tier"),
    path("onboarding/program/", OnboardingSelectProgramView.as_view(), name="onboarding-program"),
    path("onboarding/subscription-tiers/", SubscriptionTierListView.as_view(), name="onboarding-tier-list"),
    path("onboarding/programs/", JourneyProgramListView.as_view(), name="onboarding-program-list"),
]
