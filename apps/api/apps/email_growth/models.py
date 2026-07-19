from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class NewsletterSubscriber(TimeStampedModel):
    email = models.EmailField(unique=True, db_index=True)
    locale = models.CharField(max_length=10, default="en")
    is_active = models.BooleanField(default=True, db_index=True)
    source = models.CharField(max_length=64, blank=True, default="web")
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email


class EmailCampaign(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    slug = models.SlugField(max_length=128, unique=True)
    subject = models.CharField(max_length=255)
    body_html = models.TextField(blank=True, default="")
    body_text = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="email_campaigns",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.slug


class EmailSendLog(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    campaign = models.ForeignKey(
        EmailCampaign,
        on_delete=models.CASCADE,
        related_name="send_logs",
        null=True,
        blank=True,
    )
    subscriber = models.ForeignKey(
        NewsletterSubscriber,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="send_logs",
    )
    email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        db_index=True,
    )
    error = models.TextField(blank=True, default="")
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.email}:{self.status}"
