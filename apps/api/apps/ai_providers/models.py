from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class AIUsageLog(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_usage_logs",
    )
    provider = models.CharField(max_length=32, db_index=True)
    model = models.CharField(max_length=128)
    tokens_in = models.PositiveIntegerField(default=0)
    tokens_out = models.PositiveIntegerField(default=0)
    cost_estimate = models.DecimalField(max_digits=12, decimal_places=8, default=0)
    tool_id = models.CharField(max_length=128, blank=True, db_index=True)
    latency_ms = models.FloatField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["provider", "-created_at"]),
            models.Index(fields=["tool_id", "-created_at"]),
        ]
