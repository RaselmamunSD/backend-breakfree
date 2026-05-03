from datetime import timedelta

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from wellness.models import BreathingExercise, BreathingSession, JournalEntry, MoodEntry, UserPreference
from wellness.serializers import UserPreferenceSerializer

from .models import (
    AppContent,
    CBTTip,
    CurrentJourney,
    DashboardShortcut,
    ExposureItem,
    ExposureLadder,
    FearForecast,
    FeatureTutorial,
    Forecast,
    GroundingQuestSession,
    GuestQuota,
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
from .serializers import (
    AppContentSerializer,
    CBTTipSerializer,
    CurrentJourneySerializer,
    DashboardShortcutSerializer,
    ExposureItemSerializer,
    ExposureLadderSerializer,
    ExposureLadderStepSerializer,
    FearForecastSerializer,
    FeatureTutorialSerializer,
    ForecastSerializer,
    GroundingQuestSessionSerializer,
    JournalLiteSerializer,
    MoodLogSerializer,
    PredictionSerializer,
    PremiumPlanSerializer,
    PremiumSubscriptionSerializer,
    ProfileSerializer,
    RestorePurchaseSerializer,
    ProgramDaySerializer,
    ProgramTrackSerializer,
    SOSSessionSerializer,
    SOSModeEventSerializer,
    UserProgramProgressSerializer,
    UserSettingSerializer,
    WorryForecastTemplateSerializer,
)
from .services import (
    consecutive_day_streak,
    premium_feature_gates,
    resolve_premium_plan_by_store_product,
    subscription_end_date_for_plan,
    user_is_premium,
)


def _device_id(request) -> str:
    return (request.headers.get("X-Device-Id") or request.data.get("device_id") or "").strip()


def _expire_live_forecasts(qs):
    now = timezone.now()
    qs.filter(status=FearForecast.STATUS_LIVE, expires_at__lte=now).update(status=FearForecast.STATUS_EXPIRED)


def _default_forecast_expires_at(proof: str):
    now = timezone.now()
    if proof == FearForecast.PROOF_TONIGHT:
        return now + timedelta(hours=10)
    if proof == FearForecast.PROOF_TOMORROW:
        return now + timedelta(hours=24)
    if proof == FearForecast.PROOF_AFTER_EVENT:
        return now + timedelta(days=3)
    return None


class UserOwnedModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FeatureTutorialViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FeatureTutorialSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FeatureTutorial.objects.filter(is_active=True)


class DashboardShortcutViewSet(UserOwnedModelViewSet):
    serializer_class = DashboardShortcutSerializer
    queryset = DashboardShortcut.objects.all()


class CurrentJourneyViewSet(UserOwnedModelViewSet):
    serializer_class = CurrentJourneySerializer
    queryset = CurrentJourney.objects.all()

    def list(self, request, *args, **kwargs):
        obj, _ = CurrentJourney.objects.get_or_create(user=request.user)
        return Response(self.get_serializer(obj).data)


class PredictionViewSet(UserOwnedModelViewSet):
    serializer_class = PredictionSerializer
    queryset = Prediction.objects.all()


class ForecastViewSet(UserOwnedModelViewSet):
    serializer_class = ForecastSerializer
    queryset = Forecast.objects.all()


class GroundingQuestSessionViewSet(UserOwnedModelViewSet):
    serializer_class = GroundingQuestSessionSerializer
    queryset = GroundingQuestSession.objects.all()

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        obj = self.get_object()
        if obj.quest_status != GroundingQuestSession.STATUS_NOT_STARTED:
            return Response({"detail": "Already started or completed."}, status=status.HTTP_400_BAD_REQUEST)
        obj.quest_status = GroundingQuestSession.STATUS_IN_PROGRESS
        obj.started_at = timezone.now()
        obj.save(update_fields=["quest_status", "started_at", "updated_at"])
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=["patch"])
    def tasks(self, request, pk=None):
        obj = self.get_object()
        tasks = request.data.get("task_progress")
        if tasks is None:
            return Response({"detail": "task_progress required."}, status=status.HTTP_400_BAD_REQUEST)
        obj.task_progress = tasks
        done = sum(1 for t in tasks if t.get("found", 0) >= t.get("target", 0) or t.get("skipped"))
        obj.completed_steps = min(done, len(tasks))
        obj.save(update_fields=["task_progress", "completed_steps", "updated_at"])
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        obj = self.get_object()
        obj.quest_status = GroundingQuestSession.STATUS_COMPLETED
        obj.is_completed = True
        obj.ended_at = timezone.now()
        obj.save(update_fields=["quest_status", "is_completed", "ended_at", "updated_at"])
        return Response(self.get_serializer(obj).data)


class SOSModeEventViewSet(UserOwnedModelViewSet):
    serializer_class = SOSModeEventSerializer
    queryset = SOSModeEvent.objects.all()

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        obj = self.get_object()
        obj.is_active = False
        obj.resolved_at = timezone.now()
        obj.save(update_fields=["is_active", "resolved_at", "updated_at"])
        return Response(self.get_serializer(obj).data)


class SOSSessionViewSet(UserOwnedModelViewSet):
    serializer_class = SOSSessionSerializer
    queryset = SOSSession.objects.all()

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        obj = self.get_object()
        obj.current_step = SOSSession.STEP_DONE
        obj.completed_at = timezone.now()
        obj.save(update_fields=["current_step", "completed_at", "updated_at"])
        return Response(self.get_serializer(obj).data)


class ExposureLadderViewSet(UserOwnedModelViewSet):
    serializer_class = ExposureLadderSerializer
    queryset = ExposureLadder.objects.all()

    @action(detail=True, methods=["post"])
    def add_step(self, request, pk=None):
        ladder = self.get_object()
        serializer = ExposureLadderStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ladder=ladder)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExposureItemViewSet(UserOwnedModelViewSet):
    serializer_class = ExposureItemSerializer
    queryset = ExposureItem.objects.all()


class UserSettingViewSet(UserOwnedModelViewSet):
    serializer_class = UserSettingSerializer
    queryset = UserSetting.objects.all()

    def list(self, request, *args, **kwargs):
        obj, _ = UserSetting.objects.get_or_create(user=request.user)
        return Response(self.get_serializer(obj).data)

    @action(detail=False, methods=["patch"], url_path="me")
    def me(self, request):
        obj, _ = UserSetting.objects.get_or_create(user=request.user)
        ser = self.get_serializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

    @action(detail=False, methods=["post"], url_path="demo-reset")
    def demo_reset(self, request):
        user = request.user
        user.moods.all().delete()
        user.journals.all().delete()
        user.fear_forecasts.all().delete()
        user.exposure_items.all().delete()
        user.grounding_sessions.all().delete()
        user.sos_sessions.all().delete()
        obj, _ = UserSetting.objects.get_or_create(user=user)
        obj.demo_reset_at = timezone.now()
        obj.save(update_fields=["demo_reset_at", "updated_at"])
        return Response({"detail": "Demo data cleared.", "demo_reset_at": obj.demo_reset_at})


class PremiumPlanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PremiumPlanSerializer
    permission_classes = [permissions.AllowAny]
    queryset = PremiumPlan.objects.filter(is_active=True)


class PremiumSubscriptionViewSet(UserOwnedModelViewSet):
    serializer_class = PremiumSubscriptionSerializer
    queryset = PremiumSubscription.objects.select_related("plan").all()


class PremiumEntitlementsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localdate()
        sub = (
            user.premium_subscriptions.filter(status="active")
            .filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
            .select_related("plan")
            .first()
        )
        layout = sub.plan.ui_version if sub else PremiumPlan.UI_NEW
        return Response(
            {
                "is_premium": user_is_premium(user),
                "gates": premium_feature_gates(user),
                "paywall_ui_version": layout,
                "active_subscription": PremiumSubscriptionSerializer(sub).data if sub else None,
            }
        )


class PremiumRestorePurchaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = RestorePurchaseSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        product_id = (d.get("product_id") or "").strip()
        plan_key = (d.get("plan_key") or "").strip()
        plan = resolve_premium_plan_by_store_product(product_id)
        if not plan and plan_key:
            plan = PremiumPlan.objects.filter(plan_key=plan_key, is_active=True).first()
        if not plan:
            return Response(
                {"detail": "Unknown product_id or plan_key. Use GET /api/premium/plans/ for ids and plan_key values."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trust = getattr(settings, "RESTORE_PURCHASE_TRUST_RECEIPT", False)
        if not (settings.DEBUG or trust):
            return Response(
                {
                    "detail": (
                        "Store receipt verification is not enabled on this server. "
                        "For local/staging set DEBUG=True or RESTORE_PURCHASE_TRUST_RECEIPT=true. "
                        "Production must verify via App Store Server API or Google Play Developer API "
                        "before activating a subscription."
                    ),
                    "code": "store_verification_required",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        tok = (d.get("purchase_token") or "").strip()
        if len(tok) < 8:
            return Response(
                {"detail": "Provide purchase_token from the native purchase / restore callback (min length 8)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        plat = (
            PremiumSubscription.PLATFORM_IOS
            if d["platform"] == "ios"
            else PremiumSubscription.PLATFORM_ANDROID
        )
        ref_piece = ((d.get("transaction_id") or "").strip() or tok)[:255]

        today = timezone.localdate()
        user = request.user
        PremiumSubscription.objects.filter(user=user, status="active").update(status="cancelled")
        end = subscription_end_date_for_plan(plan)
        sub = PremiumSubscription.objects.create(
            user=user,
            plan=plan,
            status="active",
            start_date=today,
            end_date=end,
            restored_at=timezone.now(),
            store_platform=plat,
            store_reference=ref_piece,
        )
        return Response(PremiumSubscriptionSerializer(sub).data, status=status.HTTP_201_CREATED)


class FearForecastViewSet(UserOwnedModelViewSet):
    serializer_class = FearForecastSerializer
    queryset = FearForecast.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        _expire_live_forecasts(qs)
        st = self.request.query_params.get("status")
        if st:
            qs = qs.filter(status=st)
        return qs

    def perform_create(self, serializer):
        proof = serializer.validated_data.get("proof_check_in", FearForecast.PROOF_NONE)
        exp = serializer.validated_data.get("expires_at") or _default_forecast_expires_at(proof)
        serializer.save(user=self.request.user, device_id="", expires_at=exp)

    @action(detail=True, methods=["post"], url_path="outcome")
    def set_outcome(self, request, pk=None):
        obj = self.get_object()
        out = request.data.get("outcome")
        if out not in (FearForecast.OUTCOME_SAFE, FearForecast.OUTCOME_HAPPENED):
            return Response({"detail": "outcome must be 'safe' or 'happened'."}, status=status.HTTP_400_BAD_REQUEST)
        obj.outcome = out
        obj.status = FearForecast.STATUS_RESOLVED
        obj.resolved_at = timezone.now()
        obj.save(update_fields=["outcome", "status", "resolved_at", "updated_at"])
        return Response(FearForecastSerializer(obj).data)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        user = request.user
        qs = FearForecast.objects.filter(user=user)
        _expire_live_forecasts(qs)
        resolved = qs.filter(status=FearForecast.STATUS_RESOLVED)
        total = resolved.count()
        safe = resolved.filter(outcome=FearForecast.OUTCOME_SAFE).count()
        safe_rate = round(100 * safe / total) if total else 0
        today = timezone.localdate()
        daily = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            cnt = resolved.filter(resolved_at__date=d).count()
            daily.append({"date": str(d), "resolved_count": cnt})
        return Response({"safe_rate_percent": safe_rate, "resolved_total": total, "proof_bank_week": daily})


class WorryForecastTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorryForecastTemplateSerializer
    permission_classes = [permissions.AllowAny]
    queryset = WorryForecastTemplate.objects.filter(is_active=True)


class CBTTipRandomView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        tip = CBTTip.objects.filter(is_active=True).order_by("?").first()
        if not tip:
            return Response(
                {
                    "body": (
                        "Be specific. Instead of 'I'll feel bad,' try naming the exact sensation and duration "
                        "so you can test it later."
                    )
                }
            )
        return Response(CBTTipSerializer(tip).data)


class AppContentView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, key=None):
        if key:
            row = AppContent.objects.filter(key=key).first()
            if not row:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response(row.payload)
        data = {c.key: c.payload for c in AppContent.objects.all()}
        return Response(data)


class JourneyListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        programs = ProgramTrack.objects.filter(is_active=True)
        return Response(ProgramTrackSerializer(programs, many=True).data)


class JourneyDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug):
        program = ProgramTrack.objects.filter(slug=slug, is_active=True).first()
        if not program:
            return Response({"detail": "Unknown program."}, status=status.HTTP_404_NOT_FOUND)
        premium = user_is_premium(request.user)
        completed_ids = set(
            UserDayCompletion.objects.filter(user=request.user, day__program=program).values_list(
                "day_id", flat=True
            )
        )
        days_out = []
        for d in program.days.all():
            locked = (d.day_number > program.free_preview_days) and not premium
            days_out.append(
                {
                    "id": d.id,
                    "day_number": d.day_number,
                    "label_date": d.label_date,
                    "title": d.title,
                    "short_description": d.short_description if not locked else "",
                    "is_locked": locked,
                    "is_completed": d.id in completed_ids,
                }
            )
        progress, _ = UserProgramProgress.objects.get_or_create(user=request.user, program=program)
        return Response(
            {
                "program": ProgramTrackSerializer(program).data,
                "days": days_out,
                "progress": UserProgramProgressSerializer(progress).data,
                "user_is_premium": premium,
            }
        )


class JourneyDayDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug, day_number):
        program = ProgramTrack.objects.filter(slug=slug, is_active=True).first()
        if not program:
            return Response({"detail": "Unknown program."}, status=status.HTTP_404_NOT_FOUND)
        day = ProgramDay.objects.filter(program=program, day_number=day_number).first()
        if not day:
            return Response({"detail": "Unknown day."}, status=status.HTTP_404_NOT_FOUND)
        locked = (day.day_number > program.free_preview_days) and not user_is_premium(request.user)
        if locked:
            return Response(
                {
                    "locked": True,
                    "detail": "Unlock with Premium to view this day.",
                    "day_number": day.day_number,
                    "title": day.title,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(ProgramDaySerializer(day).data)


class JourneyDayCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, day_number):
        program = ProgramTrack.objects.filter(slug=slug, is_active=True).first()
        if not program:
            return Response({"detail": "Unknown program."}, status=status.HTTP_404_NOT_FOUND)
        day = ProgramDay.objects.filter(program=program, day_number=day_number).first()
        if not day:
            return Response({"detail": "Unknown day."}, status=status.HTTP_404_NOT_FOUND)
        locked = (day.day_number > program.free_preview_days) and not user_is_premium(request.user)
        if locked:
            return Response({"detail": "Premium required."}, status=status.HTTP_403_FORBIDDEN)
        UserDayCompletion.objects.get_or_create(user=request.user, day=day)
        progress, _ = UserProgramProgress.objects.get_or_create(user=request.user, program=program)
        progress.last_opened_day = max(progress.last_opened_day, day_number)
        progress.save(update_fields=["last_opened_day", "updated_at"])
        return Response({"detail": "Day marked complete.", "day_number": day_number})


class GuestMoodLogView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        did = _device_id(request)
        if not did:
            return Response({"detail": "Send X-Device-Id header or device_id in body."}, status=400)
        q, _ = GuestQuota.objects.get_or_create(device_id=did)
        if q.mood_logs_used >= 1:
            return Response(
                {"detail": "Free mood log used. Create an account to continue.", "code": "guest_mood_limit"},
                status=status.HTTP_403_FORBIDDEN,
            )
        q.mood_logs_used += 1
        q.save(update_fields=["mood_logs_used", "updated_at"])
        return Response(
            {
                "detail": "Mood saved (guest).",
                "device_id": did,
                "mood_label": request.data.get("mood_label"),
                "note": request.data.get("note", ""),
            },
            status=status.HTTP_201_CREATED,
        )


class GuestFearForecastCreateView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        did = _device_id(request)
        if not did:
            return Response({"detail": "Send X-Device-Id header or device_id in body."}, status=400)
        q, _ = GuestQuota.objects.get_or_create(device_id=did)
        if q.fear_forecasts_used >= 1:
            return Response(
                {"detail": "Free forecast used. Sign up to save your proof bank.", "code": "guest_forecast_limit"},
                status=status.HTTP_403_FORBIDDEN,
            )
        ser = FearForecastSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        proof = ser.validated_data.get("proof_check_in", FearForecast.PROOF_NONE)
        exp = ser.validated_data.get("expires_at") or _default_forecast_expires_at(proof)
        obj = ser.save(user=None, device_id=did, expires_at=exp)
        q.fear_forecasts_used += 1
        q.save(update_fields=["fear_forecasts_used", "updated_at"])
        return Response(FearForecastSerializer(obj).data, status=status.HTTP_201_CREATED)


class ProfileSectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        pref, _ = UserPreference.objects.get_or_create(user=user)
        active_premium = PremiumSubscription.objects.filter(user=user, status="active").filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.localdate())
        ).first()
        return Response(
            {
                "user": ProfileSerializer(user).data,
                "is_premium": user_is_premium(user),
                "premium_subscription": (
                    PremiumSubscriptionSerializer(active_premium).data if active_premium else None
                ),
                "wellness_preferences": UserPreferenceSerializer(pref).data,
            }
        )


class ProfileDeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        user.delete()
        return Response({"detail": "Account deleted."}, status=status.HTTP_200_OK)


class DashboardOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        current_journey, _ = CurrentJourney.objects.get_or_create(user=user)
        latest_prediction = user.predictions.first()
        unread_notifications = user.notifications.filter(is_read=False).count()
        return Response(
            {
                "greeting_name": user.full_name or user.username,
                "unread_notifications": unread_notifications,
                "current_journey": CurrentJourneySerializer(current_journey).data,
                "today_mood_logged": user.moods.filter(entry_date=timezone.localdate()).exists(),
                "latest_prediction": PredictionSerializer(latest_prediction).data if latest_prediction else None,
                "quick_stats": {
                    "total_mood_logs": user.moods.count(),
                    "total_journal_entries": user.journals.count(),
                    "grounding_sessions": user.grounding_sessions.count(),
                },
            }
        )


class StatisticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        moods = MoodEntry.objects.filter(user=user)
        mood_dates = list(moods.values_list("entry_date", flat=True))
        streak = consecutive_day_streak(mood_dates)
        best_streak = streak
        avg_mood = round(sum(m.mood_score for m in moods) / moods.count(), 2) if moods.exists() else 0

        ff = FearForecast.objects.filter(user=user)
        _expire_live_forecasts(ff)
        resolved = ff.filter(status=FearForecast.STATUS_RESOLVED)
        total_r = resolved.count()
        safe_r = resolved.filter(outcome=FearForecast.OUTCOME_SAFE).count()
        worry_accuracy = round(100 * safe_r / total_r) if total_r else 0

        exposures = ExposureItem.objects.filter(user=user)
        today = timezone.localdate()
        week_ago = today - timedelta(days=7)
        exposures_week_done = exposures.filter(
            ladder_status=ExposureItem.STATUS_COMPLETED, updated_at__date__gte=week_ago
        ).count()
        exp_daily = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            c = exposures.filter(ladder_status=ExposureItem.STATUS_COMPLETED, updated_at__date=d).count()
            exp_daily.append({"date": str(d), "count": c})

        distress_drops = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            day_items = exposures.filter(updated_at__date=d).exclude(distress_before__isnull=True).exclude(
                distress_after__isnull=True
            )
            drops = [e.distress_before - e.distress_after for e in day_items]
            avg_drop = round(sum(drops) / len(drops), 1) if drops else 0
            distress_drops.append({"date": str(d), "avg_drop": avg_drop})

        proof_week = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            proof_week.append(
                {
                    "date": str(d),
                    "count": resolved.filter(resolved_at__date=d).count(),
                }
            )

        return Response(
            {
                "daily_streak": {
                    "current_streak": streak,
                    "best_streak": best_streak,
                    "total_mood_days": len(set(mood_dates)),
                },
                "mood": {
                    "entries": moods.count(),
                    "average_score": avg_mood,
                    "last_7_days": moods.filter(entry_date__gte=today - timedelta(days=7)).count(),
                },
                "proof_bank_week": proof_week,
                "worries_did_not_happen_percent": worry_accuracy,
                "exposures_week": {
                    "weekly_total": exposures_week_done,
                    "daily_counts": exp_daily,
                },
                "avg_distress_drop_week": distress_drops,
                "journals": {"entries": JournalEntry.objects.filter(user=user).count()},
                "sos": {
                    "total_events": user.sos_events.count(),
                    "active_events": user.sos_events.filter(is_active=True).count(),
                    "sessions_completed": user.sos_sessions.filter(completed_at__isnull=False).count(),
                },
            }
        )


class MoodLogView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from wellness.serializers import MoodEntrySerializer

        data = dict(request.data)
        if "entry_date" not in data:
            data["entry_date"] = timezone.localdate().isoformat()
        if data.get("mood_label") and not data.get("mood_score"):
            mapping = {"terrible": 2, "bad": 4, "okay": 6, "good": 8, "excellent": 10}
            data["mood_score"] = mapping.get(data["mood_label"], 6)
        ser = MoodEntrySerializer(data=data)
        ser.is_valid(raise_exception=True)
        entry_date = ser.validated_data.get("entry_date")
        obj, _ = MoodEntry.objects.update_or_create(
            user=request.user,
            entry_date=entry_date,
            defaults={
                "mood_score": ser.validated_data["mood_score"],
                "mood_label": ser.validated_data.get("mood_label", ""),
                "note": ser.validated_data.get("note", ""),
            },
        )
        return Response(MoodLogSerializer(obj).data, status=status.HTTP_201_CREATED)


class JournalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = JournalLiteSerializer(JournalEntry.objects.filter(user=request.user), many=True).data
        return Response(data)


class BreatheToolView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        duration_seconds = int(request.data.get("duration_seconds", 60))
        completed = bool(request.data.get("completed", True))
        notes = request.data.get("notes", "")
        cycles_completed = int(request.data.get("cycles_completed", 0))
        exercise = None
        ex_id = request.data.get("exercise")
        ex_slug = request.data.get("exercise_slug")
        if ex_id:
            exercise = BreathingExercise.objects.filter(pk=ex_id).first()
        elif ex_slug:
            exercise = BreathingExercise.objects.filter(slug=ex_slug).first()
        session = BreathingSession.objects.create(
            user=request.user,
            exercise=exercise,
            duration_seconds=duration_seconds,
            cycles_completed=cycles_completed,
            completed=completed,
            notes=notes,
        )
        return Response(
            {
                "id": session.id,
                "exercise": exercise.id if exercise else None,
                "duration_seconds": session.duration_seconds,
                "cycles_completed": session.cycles_completed,
                "completed": session.completed,
                "notes": session.notes,
                "created_at": session.created_at,
            },
            status=status.HTTP_201_CREATED,
        )
