from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditLog(models.Model):
    """Immutable security / admin action trail."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=120, db_index=True)
    resource_type = models.CharField(max_length=80, blank=True, default="", db_index=True)
    resource_id = models.CharField(max_length=120, blank=True, default="", db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action", "-created_at"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.action}:{self.resource_type}:{self.resource_id}"


class BlockedIP(models.Model):
    """Simple IP blocklist for abuse mitigation."""

    ip = models.GenericIPAddressField(unique=True, db_index=True)
    reason = models.CharField(max_length=255, blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"

    def __str__(self) -> str:
        return self.ip


class PushSubscription(models.Model):
    """Web Push subscription (VAPID)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )
    endpoint = models.URLField(max_length=2048, unique=True)
    keys = models.JSONField(default=dict, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"push:{self.user_id}:{self.pk}"
