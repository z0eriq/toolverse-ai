from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class BacklinkTarget(TimeStampedModel):
    url = models.URLField(max_length=1024)
    path = models.CharField(max_length=512, blank=True, default="", db_index=True)
    title = models.CharField(max_length=255, blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title or self.url


class BacklinkCampaign(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"

    name = models.CharField(max_length=255)
    target = models.ForeignKey(
        BacklinkTarget,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class BacklinkOpportunity(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        OUTREACH = "outreach", "Outreach"
        WON = "won", "Won"
        LOST = "lost", "Lost"
        DISMISSED = "dismissed", "Dismissed"

    campaign = models.ForeignKey(
        BacklinkCampaign,
        on_delete=models.CASCADE,
        related_name="opportunities",
        null=True,
        blank=True,
    )
    target = models.ForeignKey(
        BacklinkTarget,
        on_delete=models.CASCADE,
        related_name="opportunities",
    )
    source_domain = models.CharField(max_length=255, db_index=True)
    source_url = models.URLField(max_length=1024, blank=True, default="")
    contact_email = models.EmailField(blank=True, default="")
    priority = models.IntegerField(default=50, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    rationale = models.TextField(blank=True, default="")
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-priority", "-created_at"]
        indexes = [models.Index(fields=["status", "-priority"])]

    def __str__(self) -> str:
        return f"{self.source_domain}:{self.status}"


class BacklinkOutreachLog(TimeStampedModel):
    opportunity = models.ForeignKey(
        BacklinkOpportunity,
        on_delete=models.CASCADE,
        related_name="outreach_logs",
    )
    channel = models.CharField(max_length=64, default="email")
    message = models.TextField(blank=True, default="")
    outcome = models.CharField(max_length=64, blank=True, default="")
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"outreach:{self.opportunity_id}:{self.pk}"
