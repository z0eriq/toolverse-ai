from __future__ import annotations

import logging
import secrets
import string
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.referrals.models import (
    ReferralAttribution,
    ReferralCode,
    ReferralEvent,
    ReferralReward,
)

logger = logging.getLogger("toolverse.referrals")

IP_CAP_PER_DAY = int(getattr(settings, "REFERRAL_IP_CAP_PER_DAY", 5) or 5)
QUALIFY_POINTS = int(getattr(settings, "REFERRAL_QUALIFY_POINTS", 100) or 100)


def _generate_code(user) -> str:
    base = slugify((getattr(user, "name", "") or "")[:12]) or "tv"
    base = base.replace("-", "")[:8] or "tv"
    suffix = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"{base}{suffix}"[:32]


def get_or_create_code(user) -> ReferralCode:
    existing = ReferralCode.objects.filter(user=user).first()
    if existing:
        return existing
    for _ in range(8):
        code = _generate_code(user)
        if not ReferralCode.objects.filter(code=code).exists():
            return ReferralCode.objects.create(user=user, code=code)
    # Extremely unlikely fallback
    return ReferralCode.objects.create(
        user=user,
        code=secrets.token_hex(8),
    )


def track_click(code: str, *, ip: str | None = None, meta: dict | None = None) -> ReferralCode | None:
    ref = ReferralCode.objects.filter(code=code, is_active=True).select_related("user").first()
    if not ref:
        return None
    ReferralEvent.objects.create(
        kind=ReferralEvent.Kind.CLICK,
        code=ref,
        user=None,
        ip=ip,
        meta=meta or {},
    )
    return ref


@transaction.atomic
def attribute_signup(
    referee,
    code: str,
    *,
    ip: str | None = None,
    device_hash: str = "",
) -> ReferralAttribution | None:
    """Attribute a new signup to a referral code. Blocks self-referral."""
    ref_code = ReferralCode.objects.filter(code=code, is_active=True).select_related("user").first()
    if not ref_code:
        return None

    if ref_code.user_id == referee.pk:
        ReferralEvent.objects.create(
            kind=ReferralEvent.Kind.BLOCK,
            code=ref_code,
            user=referee,
            ip=ip,
            meta={"reason": "self_referral"},
        )
        attr, _ = ReferralAttribution.objects.update_or_create(
            referee=referee,
            defaults={
                "referrer": ref_code.user,
                "code": ref_code,
                "status": ReferralAttribution.Status.BLOCKED,
                "ip": ip,
                "device_hash": device_hash or "",
            },
        )
        return attr

    # IP rate cap
    if ip:
        since = timezone.now() - timedelta(days=1)
        ip_count = ReferralAttribution.objects.filter(
            ip=ip,
            created_at__gte=since,
        ).exclude(status=ReferralAttribution.Status.BLOCKED).count()
        if ip_count >= IP_CAP_PER_DAY:
            ReferralEvent.objects.create(
                kind=ReferralEvent.Kind.BLOCK,
                code=ref_code,
                user=referee,
                ip=ip,
                meta={"reason": "ip_cap"},
            )
            attr, _ = ReferralAttribution.objects.update_or_create(
                referee=referee,
                defaults={
                    "referrer": ref_code.user,
                    "code": ref_code,
                    "status": ReferralAttribution.Status.BLOCKED,
                    "ip": ip,
                    "device_hash": device_hash or "",
                },
            )
            return attr

    attr, created = ReferralAttribution.objects.update_or_create(
        referee=referee,
        defaults={
            "referrer": ref_code.user,
            "code": ref_code,
            "status": ReferralAttribution.Status.PENDING,
            "ip": ip,
            "device_hash": device_hash or "",
        },
    )
    if created or attr.status == ReferralAttribution.Status.PENDING:
        ReferralEvent.objects.create(
            kind=ReferralEvent.Kind.SIGNUP,
            code=ref_code,
            user=referee,
            ip=ip,
            meta={},
        )
    return attr


@transaction.atomic
def qualify_referral(referee) -> ReferralAttribution | None:
    """
    Mark attribution qualified and award referrer points (via gamification if available).
    Anti-abuse: self-referral and already-blocked attributions are skipped.
    """
    try:
        attr = ReferralAttribution.objects.select_related("referrer", "referee", "code").get(
            referee=referee
        )
    except ReferralAttribution.DoesNotExist:
        return None

    if attr.status == ReferralAttribution.Status.BLOCKED:
        return attr
    if attr.referrer_id == attr.referee_id:
        attr.status = ReferralAttribution.Status.BLOCKED
        attr.save(update_fields=["status", "updated_at"])
        ReferralEvent.objects.create(
            kind=ReferralEvent.Kind.BLOCK,
            code=attr.code,
            user=referee,
            meta={"reason": "self_referral"},
        )
        return attr
    if attr.status in {
        ReferralAttribution.Status.QUALIFIED,
        ReferralAttribution.Status.REWARDED,
    }:
        return attr

    attr.status = ReferralAttribution.Status.QUALIFIED
    attr.save(update_fields=["status", "updated_at"])
    ReferralEvent.objects.create(
        kind=ReferralEvent.Kind.QUALIFY,
        code=attr.code,
        user=referee,
        meta={},
    )

    reward = ReferralReward.objects.create(
        attribution=attr,
        user=attr.referrer,
        type=ReferralReward.Type.POINTS,
        amount=QUALIFY_POINTS,
        status=ReferralReward.Status.PENDING,
    )

    try:
        from apps.gamification.services import award_points

        award_points(
            attr.referrer,
            QUALIFY_POINTS,
            "referral_qualify",
            ref=f"attr:{attr.pk}",
        )
        reward.status = ReferralReward.Status.GRANTED
        reward.save(update_fields=["status", "updated_at"])
        attr.status = ReferralAttribution.Status.REWARDED
        attr.save(update_fields=["status", "updated_at"])
    except Exception as exc:  # noqa: BLE001
        logger.info("gamification award skipped: %s", exc)
        reward.status = ReferralReward.Status.FAILED
        reward.save(update_fields=["status", "updated_at"])

    return attr


def referral_stats() -> dict:
    return {
        "codes": ReferralCode.objects.count(),
        "attributions": ReferralAttribution.objects.count(),
        "pending": ReferralAttribution.objects.filter(
            status=ReferralAttribution.Status.PENDING
        ).count(),
        "qualified": ReferralAttribution.objects.filter(
            status__in=(
                ReferralAttribution.Status.QUALIFIED,
                ReferralAttribution.Status.REWARDED,
            )
        ).count(),
        "blocked": ReferralAttribution.objects.filter(
            status=ReferralAttribution.Status.BLOCKED
        ).count(),
        "clicks": ReferralEvent.objects.filter(kind=ReferralEvent.Kind.CLICK).count(),
        "rewards_granted": ReferralReward.objects.filter(
            status=ReferralReward.Status.GRANTED
        ).count(),
    }
