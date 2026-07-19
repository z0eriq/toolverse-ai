from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class AnalyticsEvent(TimeStampedModel):
    name = models.CharField(max_length=128, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
    )
    session_id = models.CharField(max_length=64, blank=True)
    path = models.CharField(max_length=512, blank=True)
    properties = models.JSONField(default=dict, blank=True)
    # Additive attribution / geo fields (nullable / blank for backward compatibility)
    tool_id = models.CharField(max_length=128, blank=True, default="", db_index=True)
    country = models.CharField(max_length=2, blank=True, default="")
    referrer = models.TextField(blank=True, default="")
    user_agent_hash = models.CharField(max_length=64, blank=True, default="")
    # Launch attribution (UTM + campaign key); properties JSON retained for extras
    utm_source = models.CharField(max_length=128, blank=True, default="", db_index=True)
    utm_medium = models.CharField(max_length=128, blank=True, default="")
    utm_campaign = models.CharField(max_length=128, blank=True, default="")
    campaign_key = models.CharField(max_length=128, blank=True, default="", db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name", "-created_at"]),
            models.Index(fields=["tool_id", "-created_at"]),
            models.Index(fields=["country", "-created_at"]),
            models.Index(fields=["campaign_key", "-created_at"]),
            models.Index(fields=["utm_source", "-created_at"]),
        ]


class AnalyticsDailyRollup(models.Model):
    date = models.DateField(db_index=True)
    tool_id = models.CharField(max_length=128, blank=True, default="", db_index=True)
    event_name = models.CharField(max_length=128, db_index=True)
    count = models.PositiveIntegerField(default=0)
    country = models.CharField(max_length=2, blank=True, default="")

    class Meta:
        ordering = ["-date", "event_name"]
        unique_together = (("date", "tool_id", "event_name", "country"),)
        indexes = [
            models.Index(fields=["date", "event_name"]),
            models.Index(fields=["date", "tool_id"]),
        ]

    def __str__(self) -> str:
        tool = self.tool_id or "*"
        country = self.country or "*"
        return f"{self.date} {self.event_name} {tool} {country}={self.count}"
