from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class CreatorProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="creator_profile",
    )
    display_name = models.CharField(max_length=120, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    payout_ready = models.BooleanField(default=False)

    class Meta:
        ordering = ["display_name", "id"]

    def __str__(self) -> str:
        return self.display_name or f"creator:{self.user_id}"


class CreatorSubmission(TimeStampedModel):
    class Type(models.TextChoices):
        TOOL = "tool", "Tool"
        TEMPLATE = "template", "Template"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    creator = models.ForeignKey(
        CreatorProfile,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    type = models.CharField(max_length=20, choices=Type.choices, db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    tool_spec = models.ForeignKey(
        "tool_factory.ToolSpec",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="creator_submissions",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    reviewer_notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status", "-updated_at"]),
            models.Index(fields=["type", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.type}:{self.pk}:{self.status}"


class CreatorUsageStat(models.Model):
    submission = models.ForeignKey(
        CreatorSubmission,
        on_delete=models.CASCADE,
        related_name="usage_stats",
        null=True,
        blank=True,
    )
    tool_slug = models.SlugField(max_length=128, blank=True, default="", db_index=True)
    period = models.CharField(max_length=32, db_index=True)
    runs = models.PositiveIntegerField(default=0)
    unique_users = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-period"]
        indexes = [models.Index(fields=["tool_slug", "period"])]

    def __str__(self) -> str:
        return f"{self.tool_slug}:{self.period}"


class CreatorRevenueShareStub(TimeStampedModel):
    class Status(models.TextChoices):
        ACCRUED = "accrued", "Accrued"
        PAID = "paid", "Paid"

    creator = models.ForeignKey(
        CreatorProfile,
        on_delete=models.CASCADE,
        related_name="revenue_shares",
    )
    period = models.CharField(max_length=32, db_index=True)
    amount_cents = models.IntegerField(default=0)
    share_bps = models.PositiveIntegerField(default=7000)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACCRUED,
        db_index=True,
    )

    class Meta:
        ordering = ["-period"]
        unique_together = (("creator", "period"),)

    def __str__(self) -> str:
        return f"{self.creator_id}:{self.period}:{self.amount_cents}"
