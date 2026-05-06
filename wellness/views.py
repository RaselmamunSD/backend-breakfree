from celery import shared_task
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    BreathingExercise,
    BreathingSession,
    Habit,
    JournalEntry,
    MoodEntry,
    SubscriptionPlan,
    UserPreference,
    UserSubscription,
)
from .serializers import (
    BreathingExerciseSerializer,
    BreathingSessionSerializer,
    HabitSerializer,
    JournalEntrySerializer,
    MoodEntrySerializer,
    SubscriptionPlanSerializer,
    UserPreferenceSerializer,
    UserSubscriptionSerializer,
)


@shared_task
def sample_background_task(user_id):
    return f"Background task completed for user {user_id}"


class UserOwnedModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MoodEntryViewSet(UserOwnedModelViewSet):
    serializer_class = MoodEntrySerializer
    queryset = MoodEntry.objects.all()


class JournalEntryViewSet(UserOwnedModelViewSet):
    serializer_class = JournalEntrySerializer
    queryset = JournalEntry.objects.all()


class BreathingSessionViewSet(UserOwnedModelViewSet):
    serializer_class = BreathingSessionSerializer
    queryset = BreathingSession.objects.all()


class BreathingExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BreathingExerciseSerializer
    permission_classes = [permissions.AllowAny]
    queryset = BreathingExercise.objects.filter(is_active=True)


class HabitViewSet(UserOwnedModelViewSet):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]
    queryset = SubscriptionPlan.objects.filter(is_active=True)


class UserSubscriptionViewSet(UserOwnedModelViewSet):
    serializer_class = UserSubscriptionSerializer
    queryset = UserSubscription.objects.select_related("plan").all()


class UserPreferenceViewSet(UserOwnedModelViewSet):
    serializer_class = UserPreferenceSerializer
    queryset = UserPreference.objects.all()

    def get_queryset(self):
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        obj, _ = UserPreference.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class ProfileDashboardView(APIView):
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        latest_subscription = user.subscriptions.select_related("plan").first()
        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "avatar": user.avatar,
                },
                "stats": {
                    "journal_entries": user.journals.count(),
                    "habit_count": user.habits.filter(is_active=True).count(),
                    "longest_streak": max([h.streak for h in user.habits.all()], default=0),
                },
                "subscription": (
                    {
                        "status": latest_subscription.status,
                        "plan": latest_subscription.plan.name,
                        "plan_type": latest_subscription.plan.plan_type,
                        "end_date": latest_subscription.end_date,
                    }
                    if latest_subscription
                    else None
                ),
            }
        )
