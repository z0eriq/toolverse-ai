from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.analytics.funnels import build_conversion_funnel
from apps.analytics.models import AnalyticsEvent

User = get_user_model()


@pytest.mark.django_db
def test_build_conversion_funnel_rates():
    AnalyticsEvent.objects.create(name="page_view", session_id="s1")
    AnalyticsEvent.objects.create(name="tool_impression", session_id="s1", tool_id="pdf-merge")
    AnalyticsEvent.objects.create(name="tool_click", session_id="s1", tool_id="pdf-merge")
    AnalyticsEvent.objects.create(name="tool_use", session_id="s1", tool_id="pdf-merge")
    AnalyticsEvent.objects.create(name="tool_use", session_id="s1", tool_id="pdf-merge")
    AnalyticsEvent.objects.create(name="tool_complete", session_id="s1", tool_id="pdf-merge")
    AnalyticsEvent.objects.create(
        name="tool_use",
        session_id="s1",
        tool_id="pdf-merge",
        properties={"action": "complete"},
    )
    AnalyticsEvent.objects.create(name="premium_intent", session_id="s1")
    AnalyticsEvent.objects.create(name="revenue", session_id="s1")

    funnel = build_conversion_funnel(days=30)
    assert funnel["impressions"] == 2
    assert funnel["clicks"] == 1
    assert funnel["uses"] == 3
    assert funnel["completes"] == 2  # tool_complete + action=complete
    assert funnel["premium_intent"] == 1
    assert funnel["revenue"] >= 1
    assert funnel["completion_rate"] == round(2 / 3, 4)
    assert funnel["conversion_rate"] > 0
    assert len(funnel["steps"]) == 6


@pytest.mark.django_db
def test_funnels_api_admin_only():
    admin = User.objects.create_user(
        email="funnel-admin@example.com",
        password="pass12345",
        role=User.Role.ADMIN,
        is_staff=True,
    )
    client = APIClient()
    url = reverse("analytics-funnels")

    anon = client.get(url)
    assert anon.status_code in (401, 403)

    client.force_authenticate(user=admin)
    resp = client.get(url, {"days": 14})
    assert resp.status_code == 200
    assert resp.data["success"] is True
    data = resp.data["data"]
    assert "steps" in data
    assert "completion_rate" in data
    assert "conversion_rate" in data
    assert data["window_days"] == 14


@pytest.mark.django_db
def test_track_copies_utm_from_properties():
    client = APIClient()
    url = reverse("analytics-track")
    resp = client.post(
        url,
        {
            "name": "page_view",
            "session_id": "utm-sess",
            "path": "/",
            "properties": {
                "utm_source": "google",
                "utm_medium": "cpc",
                "utm_campaign": "launch",
                "campaign_key": "launch-2026",
            },
        },
        format="json",
    )
    assert resp.status_code == 200
    event = AnalyticsEvent.objects.get(id=resp.data["data"]["id"])
    assert event.utm_source == "google"
    assert event.utm_medium == "cpc"
    assert event.utm_campaign == "launch"
    assert event.campaign_key == "launch-2026"


@pytest.mark.django_db
def test_track_accepts_top_level_utm():
    client = APIClient()
    url = reverse("analytics-track")
    resp = client.post(
        url,
        {
            "name": "tool_use",
            "session_id": "utm-top",
            "tool_id": "json-formatter",
            "utm_source": "newsletter",
            "utm_medium": "email",
            "utm_campaign": "digest",
            "campaign_key": "email-digest",
            "properties": {},
        },
        format="json",
    )
    assert resp.status_code == 200
    event = AnalyticsEvent.objects.get(id=resp.data["data"]["id"])
    assert event.utm_source == "newsletter"
    assert event.campaign_key == "email-digest"
