from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BreathingExerciseViewSet,
    BreathingSessionViewSet,
    HabitViewSet,
    JournalEntryViewSet,
    MoodEntryViewSet,
    ProfileDashboardView,
    SubscriptionPlanViewSet,
    UserPreferenceViewSet,
    UserSubscriptionViewSet,
)

router = DefaultRouter()
router.register("moods", MoodEntryViewSet, basename="mood")
router.register("journals", JournalEntryViewSet, basename="journal")
router.register("breathing-exercises", BreathingExerciseViewSet, basename="breathing-exercise")
router.register("breathing-sessions", BreathingSessionViewSet, basename="breathing-session")
router.register("habits", HabitViewSet, basename="habit")
router.register("subscription-plans", SubscriptionPlanViewSet, basename="subscription-plan")
router.register("my-subscriptions", UserSubscriptionViewSet, basename="my-subscription")
router.register("preferences", UserPreferenceViewSet, basename="preference")

urlpatterns = [
    path("profile/dashboard/", ProfileDashboardView.as_view(), name="profile-dashboard"),
    path("", include(router.urls)),
]
