from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AppContentView,
    BreatheToolView,
    CBTTipRandomView,
    CurrentJourneyViewSet,
    DashboardOverviewView,
    DashboardShortcutViewSet,
    ExposureItemViewSet,
    ExposureLadderViewSet,
    FearForecastViewSet,
    FeatureTutorialViewSet,
    ForecastViewSet,
    GuestFearForecastCreateView,
    GuestMoodLogView,
    GroundingQuestSessionViewSet,
    JourneyDayCompleteView,
    JourneyDayDetailView,
    JourneyDetailView,
    JourneyListView,
    JournalView,
    MoodLogView,
    PredictionViewSet,
    PremiumEntitlementsView,
    PremiumPlanViewSet,
    PremiumRestorePurchaseView,
    PremiumSubscriptionViewSet,
    ProfileDeleteAccountView,
    ProfileSectionView,
    SOSSessionViewSet,
    SOSModeEventViewSet,
    StatisticsView,
    UserSettingViewSet,
    WorryForecastTemplateViewSet,
)

router = DefaultRouter()
router.register("feature-tutorials", FeatureTutorialViewSet, basename="feature-tutorial")
router.register("shortcuts", DashboardShortcutViewSet, basename="shortcut")
router.register("current-journey", CurrentJourneyViewSet, basename="current-journey")
router.register("predict", PredictionViewSet, basename="predict")
router.register("forecasts", ForecastViewSet, basename="forecast")
router.register("fear-forecasts", FearForecastViewSet, basename="fear-forecast")
router.register("worry-forecast-templates", WorryForecastTemplateViewSet, basename="worry-forecast-template")
router.register("tools/grounding-quests", GroundingQuestSessionViewSet, basename="grounding-quest")
router.register("sos-mode", SOSModeEventViewSet, basename="sos-mode")
router.register("sos-sessions", SOSSessionViewSet, basename="sos-session")
router.register("exposure-ladders", ExposureLadderViewSet, basename="exposure-ladder")
router.register("exposures", ExposureItemViewSet, basename="exposure-item")
router.register("settings", UserSettingViewSet, basename="feature-settings")
router.register("premium/plans", PremiumPlanViewSet, basename="premium-plan")
router.register("premium/subscriptions", PremiumSubscriptionViewSet, basename="premium-subscription")

urlpatterns = [
    path("premium/entitlements/", PremiumEntitlementsView.as_view(), name="premium-entitlements"),
    path("premium/restore-purchase/", PremiumRestorePurchaseView.as_view(), name="premium-restore"),
    path("dashboard/", DashboardOverviewView.as_view(), name="feature-dashboard"),
    path("statistics/", StatisticsView.as_view(), name="feature-statistics"),
    path("log-mood/", MoodLogView.as_view(), name="feature-log-mood"),
    path("journal/", JournalView.as_view(), name="feature-journal"),
    path("tools/breathe/", BreatheToolView.as_view(), name="feature-tools-breathe"),
    path("tips/cbt/", CBTTipRandomView.as_view(), name="feature-cbt-tip"),
    path("app-content/", AppContentView.as_view(), name="feature-app-content-list"),
    path("app-content/<str:key>/", AppContentView.as_view(), name="feature-app-content-detail"),
    path("journeys/", JourneyListView.as_view(), name="journey-list"),
    path("journeys/<slug:slug>/", JourneyDetailView.as_view(), name="journey-detail"),
    path("journeys/<slug:slug>/days/<int:day_number>/", JourneyDayDetailView.as_view(), name="journey-day-detail"),
    path(
        "journeys/<slug:slug>/days/<int:day_number>/complete/",
        JourneyDayCompleteView.as_view(),
        name="journey-day-complete",
    ),
    path("guest/log-mood/", GuestMoodLogView.as_view(), name="guest-log-mood"),
    path("guest/fear-forecasts/", GuestFearForecastCreateView.as_view(), name="guest-fear-forecast"),
    path("profile/", ProfileSectionView.as_view(), name="feature-profile"),
    path("profile/delete-account/", ProfileDeleteAccountView.as_view(), name="feature-profile-delete"),
    path("", include(router.urls)),
]
