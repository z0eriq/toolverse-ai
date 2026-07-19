from __future__ import annotations

import pytest

from apps.monetization.ad_services import generate_ad_recommendations
from apps.monetization.models import AdOptimizationRec, AdPerformanceDaily, RevenueEvent
from django.utils import timezone


@pytest.mark.django_db
def test_generate_ad_recommendations_from_fixture():
    today = timezone.now().date()
    AdPerformanceDaily.objects.create(
        date=today,
        placement_key="sidebar",
        impressions=1000,
        clicks=3,
        revenue_cents=50,
        ctr=0.003,
        rpm=50.0,
    )
    RevenueEvent.objects.create(
        type=RevenueEvent.Type.AD_IMPRESSION,
        amount_cents=0,
        meta={"placement": "sidebar"},
    )
    result = generate_ad_recommendations()
    assert result["created"] >= 1
    assert AdOptimizationRec.objects.count() >= 1
