from __future__ import annotations

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import Throttled

from apps.marketplace.models import ApiKey, ApiUsage


class QuotaExceeded(Throttled):
    default_detail = "Monthly API quota exceeded."
    default_code = "quota_exceeded"


def check_quota(key: ApiKey) -> bool:
    """Return True if the key may consume more units this month."""
    if key.is_revoked:
        return False
    return key.usage_this_month < key.monthly_quota


def increment_usage(
    key: ApiKey,
    endpoint: str,
    status: int,
    *,
    method: str = "GET",
    units: int = 1,
) -> ApiUsage:
    """
    Record usage and bump the monthly counter.

    Raises ``QuotaExceeded`` when the monthly quota would be exceeded.
    """
    if units < 1:
        units = 1

    with transaction.atomic():
        locked = ApiKey.objects.select_for_update().get(pk=key.pk)
        if locked.is_revoked:
            raise QuotaExceeded(detail="API key has been revoked")
        if locked.usage_this_month + units > locked.monthly_quota:
            raise QuotaExceeded()

        ApiKey.objects.filter(pk=locked.pk).update(
            usage_this_month=F("usage_this_month") + units,
            last_used_at=timezone.now(),
        )
        return ApiUsage.objects.create(
            api_key=locked,
            endpoint=endpoint,
            method=method,
            status_code=status,
            units=units,
        )
