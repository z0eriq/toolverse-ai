from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.analytics.models import AnalyticsEvent
from apps.campaigns.models import MarketingCampaign

User = get_user_model()


@pytest.mark.django_db
def test_create_campaign_and_attach_event():
    admin = User.objects.create_user(
        email="campaign-admin@example.com",
        password="pass12345",
        role=User.Role.ADMIN,
        is_staff=True,
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    url = reverse("admin-campaigns")
    resp = client.post(
        url,
        {
            "key": "test-launch",
            "name": "Test Launch",
            "channel": "search",
            "status": "active",
            "budget_cents": 10000,
            "meta": {"utm_campaign": "test-launch"},
        },
        format="json",
    )
    assert resp.status_code == 201
    campaign = MarketingCampaign.objects.get(key="test-launch")
    assert campaign.status == MarketingCampaign.Status.ACTIVE

    event = AnalyticsEvent.objects.create(
        name="page_view",
        session_id="camp-1",
        campaign_key=campaign.key,
        utm_campaign=campaign.key,
        utm_source="google",
    )
    assert event.campaign_key == "test-launch"
    assert AnalyticsEvent.objects.filter(campaign_key=campaign.key).count() == 1

    summary = client.get(reverse("admin-campaigns-summary"))
    assert summary.status_code == 200
    assert summary.data["data"]["campaigns_total"] >= 1
