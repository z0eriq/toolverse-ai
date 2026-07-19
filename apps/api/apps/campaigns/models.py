from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class MarketingCampaign(TimeStampedModel):
    class Channel(models.TextChoices):
        SEARCH = "search", "Search"
        SOCIAL = "social", "Social"
        EMAIL = "email", "Email"
        AFFILIATE = "affiliate", "Affiliate"
        PARTNER = "partner", "Partner"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"

    key = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=255)
    channel = models.CharField(
        max_length=32,
        choices=Channel.choices,
        default=Channel.OTHER,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    budget_cents = models.PositiveIntegerField(default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status", "channel"]),
        ]

    def __str__(self) -> str:
        return f"{self.key}:{self.status}"


class CampaignResultDaily(models.Model):
    campaign = models.ForeignKey(
        MarketingCampaign,
        on_delete=models.CASCADE,
        related_name="daily_results",
    )
    date = models.DateField(db_index=True)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    revenue_cents = models.IntegerField(default=0)

    class Meta:
        ordering = ["-date"]
        unique_together = (("campaign", "date"),)
        indexes = [
            models.Index(fields=["date", "campaign"]),
        ]

    def __str__(self) -> str:
        return f"{self.campaign_id}:{self.date}"
