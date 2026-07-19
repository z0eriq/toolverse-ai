from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Plan(TimeStampedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="USD")
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    monthly_tool_runs = models.IntegerField(
        default=50,
        help_text="Monthly tool runs; -1 means unlimited",
    )
    api_monthly_quota = models.IntegerField(default=1000)
    ads_free = models.BooleanField(default=False)
    history_days = models.IntegerField(default=30)

    def __str__(self) -> str:
        return self.slug


class Subscription(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELED = "canceled", "Canceled"
        PAST_DUE = "past_due", "Past due"
        TRIALING = "trialing", "Trialing"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    current_period_end = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=128, blank=True)
    stripe_subscription_id = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return f"{self.user_id}:{self.plan.slug}"

    @property
    def is_active(self) -> bool:
        if self.status not in {self.Status.ACTIVE, self.Status.TRIALING}:
            return False
        if self.current_period_end and self.current_period_end < timezone.now():
            return False
        return True
