from django.contrib import admin

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

admin.site.register(BreathingExercise)
admin.site.register(MoodEntry)
admin.site.register(JournalEntry)
admin.site.register(BreathingSession)
admin.site.register(Habit)
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
admin.site.register(UserPreference)
