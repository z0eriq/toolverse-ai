from __future__ import annotations

from django.core.cache import cache
from django.utils import timezone
from rest_framework.exceptions import Throttled

from apps.subscriptions.services import ensure_free_subscription


class ToolRunLimitExceeded(Throttled):
    """Raised when a free-tier user exceeds monthly tool runs."""

    default_detail = "Monthly tool run limit exceeded. Upgrade to Pro for unlimited runs."
    default_code = "tool_run_limit"


def _period_key() -> str:
    now = timezone.now()
    return f"{now.year}{now.month:02d}"


def _cache_key(user_id: int) -> str:
    return f"tool_runs:{user_id}:{_period_key()}"


def _user_plan(user):
    if not user or not getattr(user, "is_authenticated", False):
        return None
    ensure_free_subscription(user)
    sub = getattr(user, "subscription", None)
    if sub is None:
        from apps.subscriptions.models import Subscription

        sub = Subscription.objects.select_related("plan").filter(user=user).first()
    return sub.plan if sub else None


def check_tool_run_limit(user) -> None:
    """
    Raise ToolRunLimitExceeded (429) when an authenticated free user is over quota.
    Anonymous users and unlimited plans (-1) are allowed.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return
    plan = _user_plan(user)
    if plan is None:
        return
    limit = int(getattr(plan, "monthly_tool_runs", 50) or 50)
    if limit < 0:
        return  # unlimited
    used = int(cache.get(_cache_key(user.pk), 0) or 0)
    if used >= limit:
        raise ToolRunLimitExceeded(
            detail={
                "message": "Monthly tool run limit exceeded",
                "used": used,
                "limit": limit,
                "plan": plan.slug,
            }
        )


def increment_tool_run(user) -> int:
    """Increment monthly tool-run counter for authenticated users. Returns new count."""
    if not user or not getattr(user, "is_authenticated", False):
        return 0
    key = _cache_key(user.pk)
    try:
        return int(cache.incr(key))
    except ValueError:
        # Key missing — set with ~35 day TTL covering the month
        cache.set(key, 1, timeout=60 * 60 * 24 * 40)
        return 1
