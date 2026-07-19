from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class AdPlacement(TimeStampedModel):
    class Key(models.TextChoices):
        BANNER = "banner", "Banner"
        IN_TOOL = "in-tool", "In tool"
        SIDEBAR = "sidebar", "Sidebar"
        SATELLITE = "satellite", "Satellite"

    class Network(models.TextChoices):
        ADSENSE = "adsense", "AdSense"
        CUSTOM = "custom", "Custom"

    key = models.CharField(max_length=32, choices=Key.choices, unique=True, db_index=True)
    enabled = models.BooleanField(default=True)
    network = models.CharField(
        max_length=32,
        choices=Network.choices,
        default=Network.ADSENSE,
    )
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["key"]

    def __str__(self) -> str:
        return self.key


class SponsoredTool(TimeStampedModel):
    tool = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="sponsored_entries",
    )
    sponsor_name = models.CharField(max_length=255)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    priority = models.PositiveIntegerField(default=0)
    creative = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-priority", "-updated_at"]

    def __str__(self) -> str:
        return f"{self.sponsor_name}:{self.tool_id}"


class AffiliateLink(TimeStampedModel):
    tool = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="affiliate_links",
    )
    label = models.CharField(max_length=255)
    destination_url = models.URLField(max_length=1024)
    network = models.CharField(max_length=64, blank=True, default="")
    utm = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["label"]

    def __str__(self) -> str:
        return self.label


class RevenueEvent(models.Model):
    class Type(models.TextChoices):
        AD_IMPRESSION = "ad_impression", "Ad impression"
        AD_CLICK = "ad_click", "Ad click"
        SUBSCRIPTION = "subscription", "Subscription"
        AFFILIATE = "affiliate", "Affiliate"
        API = "api", "API"

    type = models.CharField(max_length=32, choices=Type.choices, db_index=True)
    amount_cents = models.IntegerField(default=0)
    currency = models.CharField(max_length=8, default="USD")
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["type", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.type}:{self.amount_cents}{self.currency}"


class AdPerformanceDaily(TimeStampedModel):
    date = models.DateField(db_index=True)
    placement_key = models.CharField(max_length=32, db_index=True)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    revenue_cents = models.IntegerField(default=0)
    ctr = models.FloatField(default=0.0)
    rpm = models.FloatField(default=0.0)

    class Meta:
        ordering = ["-date", "placement_key"]
        unique_together = (("date", "placement_key"),)
        indexes = [models.Index(fields=["placement_key", "-date"])]

    def __str__(self) -> str:
        return f"{self.date}:{self.placement_key}"


class AdOptimizationRec(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACCEPTED = "accepted", "Accepted"
        DISMISSED = "dismissed", "Dismissed"

    placement_key = models.CharField(max_length=32, db_index=True, blank=True, default="")
    title = models.CharField(max_length=255)
    rationale = models.TextField(blank=True, default="")
    priority = models.IntegerField(default=50, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    evidence = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-priority", "-created_at"]
        indexes = [models.Index(fields=["status", "-priority"])]

    def __str__(self) -> str:
        return self.title
