from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class UserPoints(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="points",
    )
    balance = models.IntegerField(default=0)
    lifetime = models.IntegerField(default=0)

    class Meta:
        ordering = ["-lifetime"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.balance}"


class PointsLedger(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="points_ledger",
    )
    delta = models.IntegerField()
    reason = models.CharField(max_length=128, db_index=True)
    ref = models.CharField(max_length=128, blank=True, default="")
    balance_after = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.delta}:{self.reason}"


class Badge(TimeStampedModel):
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=64, blank=True, default="")
    points_required = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["points_required", "slug"]

    def __str__(self) -> str:
        return self.slug


class UserBadge(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="badges",
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="awards")

    class Meta:
        unique_together = (("user", "badge"),)
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.badge_id}"


class UserLevel(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="level",
    )
    level = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=64, blank=True, default="Novice")

    class Meta:
        ordering = ["-level"]

    def __str__(self) -> str:
        return f"{self.user_id}:L{self.level}"
