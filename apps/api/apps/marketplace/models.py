from __future__ import annotations

import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel


def _pepper() -> str:
    return getattr(settings, "API_KEY_PEPPER", "") or settings.SECRET_KEY


def hash_api_key(plaintext: str) -> str:
    """Peppered SHA-256 hash of an API key."""
    material = f"{_pepper()}:{plaintext}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    """
    Return (plaintext, key_prefix, key_hash).

    Plaintext is shown once at creation; only the hash is stored.
    """
    # tv_ prefix + 32 bytes url-safe ≈ 43 chars
    plaintext = f"tv_{secrets.token_urlsafe(32)}"
    prefix = plaintext[:8]
    return plaintext, prefix, hash_api_key(plaintext)


class ApiKey(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    name = models.CharField(max_length=128)
    key_prefix = models.CharField(max_length=8, db_index=True)
    key_hash = models.CharField(max_length=64, unique=True)
    scopes = models.JSONField(default=list, blank=True)
    rate_limit_per_minute = models.PositiveIntegerField(default=60)
    monthly_quota = models.PositiveIntegerField(default=10_000)
    usage_this_month = models.PositiveIntegerField(default=0)
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["key_prefix"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.key_prefix}…)"

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def is_active(self) -> bool:
        return not self.is_revoked

    def revoke(self) -> None:
        if self.revoked_at is None:
            self.revoked_at = timezone.now()
            self.save(update_fields=["revoked_at", "updated_at"])

    @classmethod
    def create_for_user(
        cls,
        user,
        *,
        name: str,
        scopes: list | None = None,
        rate_limit_per_minute: int = 60,
        monthly_quota: int = 10_000,
    ) -> tuple[ApiKey, str]:
        plaintext, prefix, digest = generate_api_key()
        key = cls.objects.create(
            user=user,
            name=name,
            key_prefix=prefix,
            key_hash=digest,
            scopes=scopes or [],
            rate_limit_per_minute=rate_limit_per_minute,
            monthly_quota=monthly_quota,
        )
        return key, plaintext


class ApiUsage(TimeStampedModel):
    api_key = models.ForeignKey(ApiKey, on_delete=models.CASCADE, related_name="usage_logs")
    endpoint = models.CharField(max_length=256)
    method = models.CharField(max_length=16, default="GET")
    status_code = models.PositiveSmallIntegerField(default=200)
    units = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["api_key", "-created_at"]),
            models.Index(fields=["endpoint", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.api_key_id} {self.method} {self.endpoint} {self.status_code}"


class DeveloperOrganization(TimeStampedModel):
    class PlanTier(models.TextChoices):
        FREE = "free", "Free"
        PRO = "pro", "Pro"
        ENTERPRISE = "enterprise", "Enterprise"

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="developer_orgs",
    )
    plan_tier = models.CharField(
        max_length=20,
        choices=PlanTier.choices,
        default=PlanTier.FREE,
        db_index=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ApiInvoiceStub(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        PAID = "paid", "Paid"

    org = models.ForeignKey(
        DeveloperOrganization,
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    amount_cents = models.PositiveIntegerField(default=0)
    usage_units = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    class Meta:
        ordering = ["-period_end"]

    def __str__(self) -> str:
        return f"invoice:{self.org_id}:{self.period_start}:{self.status}"


class SalesLead(TimeStampedModel):
    class Intent(models.TextChoices):
        DEMO = "demo", "Demo"
        ENTERPRISE = "enterprise", "Enterprise"
        CONTACT = "contact", "Contact"

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=120)
    email = models.EmailField(db_index=True)
    company = models.CharField(max_length=255, blank=True, default="")
    company_size = models.CharField(max_length=64, blank=True, default="")
    role = models.CharField(max_length=120, blank=True, default="")
    message = models.TextField(blank=True, default="")
    intent = models.CharField(
        max_length=20,
        choices=Intent.choices,
        default=Intent.CONTACT,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    utm_source = models.CharField(max_length=128, blank=True, default="")
    utm_medium = models.CharField(max_length=128, blank=True, default="")
    utm_campaign = models.CharField(max_length=128, blank=True, default="")
    campaign_key = models.CharField(max_length=128, blank=True, default="", db_index=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["intent", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.email}:{self.intent}:{self.status}"
