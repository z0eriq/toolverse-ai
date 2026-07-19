from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class ReferralCode(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_code",
    )
    code = models.SlugField(max_length=32, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.code


class ReferralAttribution(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUALIFIED = "qualified", "Qualified"
        REWARDED = "rewarded", "Rewarded"
        BLOCKED = "blocked", "Blocked"

    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referrals_made",
    )
    referee = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_attribution",
    )
    code = models.ForeignKey(
        ReferralCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attributions",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    device_hash = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["referrer", "status"])]

    def __str__(self) -> str:
        return f"{self.referrer_id}->{self.referee_id}:{self.status}"


class ReferralReward(TimeStampedModel):
    class Type(models.TextChoices):
        POINTS = "points", "Points"
        PRO_DAYS = "pro_days", "Pro days"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        GRANTED = "granted", "Granted"
        FAILED = "failed", "Failed"

    attribution = models.ForeignKey(
        ReferralAttribution,
        on_delete=models.CASCADE,
        related_name="rewards",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_rewards",
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.POINTS)
    amount = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.type}:{self.amount}:{self.status}"


class ReferralEvent(TimeStampedModel):
    class Kind(models.TextChoices):
        CLICK = "click", "Click"
        SIGNUP = "signup", "Signup"
        QUALIFY = "qualify", "Qualify"
        BLOCK = "block", "Block"

    kind = models.CharField(max_length=20, choices=Kind.choices, db_index=True)
    code = models.ForeignKey(
        ReferralCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referral_events",
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["kind", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.kind}:{self.pk}"
