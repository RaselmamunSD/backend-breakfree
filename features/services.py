"""Shared helpers for feature modules (premium checks, streaks, etc.)."""

from __future__ import annotations

from datetime import date, timedelta

from django.db.models import Q
from django.utils import timezone


def user_is_premium(user) -> bool:
    """True if user has an active premium or wellness subscription."""
    today = timezone.localdate()
    if user.premium_subscriptions.filter(status="active").filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    ).exists():
        return True
    if user.subscriptions.filter(status="active").filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    ).exists():
        return True
    return False


def premium_feature_gates(user) -> dict[str, bool]:
    """Boolean flags used by mobile to show SOS+, AI Coach, etc. Mirrors Figma entitlement grid."""
    active = user_is_premium(user)
    return {
        "program_day_4_plus": active,
        "sos_plus": active,
        "ai_coach_insights": active,
        "forecast_proof_system": active,
        "personal_action_plans": active,
    }


def subscription_end_date_for_plan(plan: "PremiumPlan") -> date | None:
    """Compute default end_date for a new PremiumSubscription row (None = lifetime)."""
    today = timezone.localdate()
    if plan.billing_cycle == "lifetime":
        return None
    if plan.billing_cycle == "monthly":
        return today + timedelta(days=31)
    if plan.billing_cycle == "yearly":
        return today + timedelta(days=366)
    return today + timedelta(days=31)


def resolve_premium_plan_by_store_product(product_id: str):
    """Return PremiumPlan matching App Store / Play product id."""
    from .models import PremiumPlan

    if not product_id:
        return None
    pid = product_id.strip()
    return (
        PremiumPlan.objects.filter(is_active=True)
        .filter(Q(ios_product_id=pid) | Q(google_product_id=pid))
        .order_by("sort_order")
        .first()
    )


def consecutive_day_streak(dates: list[date]) -> int:
    """Longest trailing streak from today backwards (dates need not be sorted)."""
    if not dates:
        return 0
    unique_days = sorted(set(dates), reverse=True)
    today = timezone.localdate()
    if unique_days[0] not in (today, today - timedelta(days=1)):
        return 0
    streak = 1
    expected = unique_days[0] - timedelta(days=1)
    for d in unique_days[1:]:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        elif d < expected:
            break
    return streak
