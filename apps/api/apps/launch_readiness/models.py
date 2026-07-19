from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class ReadinessCheck(TimeStampedModel):
    class Category(models.TextChoices):
        INFRA = "infra", "Infra"
        SEO = "seo", "SEO"
        ANALYTICS = "analytics", "Analytics"
        PAYMENTS = "payments", "Payments"
        EMAIL = "email", "Email"
        SECURITY = "security", "Security"
        MONITORING = "monitoring", "Monitoring"

    class Status(models.TextChoices):
        PASS = "pass", "Pass"
        WARN = "warn", "Warn"
        FAIL = "fail", "Fail"
        UNKNOWN = "unknown", "Unknown"

    key = models.SlugField(max_length=64, unique=True)
    category = models.CharField(max_length=32, choices=Category.choices, db_index=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.UNKNOWN,
        db_index=True,
    )
    detail = models.TextField(blank=True, default="")
    checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["category", "key"]

    def __str__(self) -> str:
        return f"{self.key}:{self.status}"
