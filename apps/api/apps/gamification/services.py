from __future__ import annotations

import logging

from django.db import transaction

from apps.gamification.models import Badge, PointsLedger, UserBadge, UserLevel, UserPoints

logger = logging.getLogger("toolverse.gamification")

LEVEL_TITLES = {
    1: "Novice",
    2: "Explorer",
    3: "Builder",
    4: "Pro",
    5: "Legend",
}


def _level_for_lifetime(lifetime: int) -> tuple[int, str]:
    if lifetime >= 5000:
        return 5, LEVEL_TITLES[5]
    if lifetime >= 2000:
        return 4, LEVEL_TITLES[4]
    if lifetime >= 500:
        return 3, LEVEL_TITLES[3]
    if lifetime >= 100:
        return 2, LEVEL_TITLES[2]
    return 1, LEVEL_TITLES[1]


@transaction.atomic
def award_points(user, amount: int, reason: str, *, ref: str = "") -> UserPoints:
    """Increment user points balance and append a ledger row."""
    amount = int(amount)
    if amount == 0:
        points, _ = UserPoints.objects.get_or_create(user=user)
        return points

    points, _ = UserPoints.objects.select_for_update().get_or_create(user=user)
    points.balance = int(points.balance) + amount
    if amount > 0:
        points.lifetime = int(points.lifetime) + amount
    points.save(update_fields=["balance", "lifetime", "updated_at"])

    PointsLedger.objects.create(
        user=user,
        delta=amount,
        reason=(reason or "award")[:128],
        ref=(ref or "")[:128],
        balance_after=points.balance,
    )

    level_num, title = _level_for_lifetime(points.lifetime)
    UserLevel.objects.update_or_create(
        user=user,
        defaults={"level": level_num, "title": title},
    )

    # Auto-award badges by lifetime threshold
    for badge in Badge.objects.filter(is_active=True, points_required__lte=points.lifetime):
        UserBadge.objects.get_or_create(user=user, badge=badge)

    logger.info("award_points user=%s amount=%s reason=%s", user.pk, amount, reason)
    return points


def get_user_gamification(user) -> dict:
    points, _ = UserPoints.objects.get_or_create(user=user)
    level, _ = UserLevel.objects.get_or_create(
        user=user,
        defaults={"level": 1, "title": "Novice"},
    )
    badges = list(
        UserBadge.objects.filter(user=user)
        .select_related("badge")
        .order_by("-created_at")
    )
    return {
        "balance": points.balance,
        "lifetime": points.lifetime,
        "level": level.level,
        "title": level.title,
        "badges": [
            {
                "slug": ub.badge.slug,
                "name": ub.badge.name,
                "description": ub.badge.description,
                "icon": ub.badge.icon,
                "awarded_at": ub.created_at.isoformat(),
            }
            for ub in badges
        ],
        "recent_ledger": [
            {
                "delta": row.delta,
                "reason": row.reason,
                "ref": row.ref,
                "balance_after": row.balance_after,
                "created_at": row.created_at.isoformat(),
            }
            for row in PointsLedger.objects.filter(user=user).order_by("-created_at")[:20]
        ],
    }
