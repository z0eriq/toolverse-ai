from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_command_center_returns_numeric_keys():
    admin = User.objects.create_user(
        email="admin-cc@example.com",
        password="pass12345",
        role=User.Role.ADMIN,
        is_staff=True,
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    url = reverse("admin-command-center")
    resp = client.get(url, {"days": 30})
    assert resp.status_code == 200
    assert resp.data["success"] is True
    data = resp.data["data"]
    for key in (
        "dau",
        "mau",
        "registrations",
        "tool_executions",
        "premium_conversions",
        "revenue_cents",
        "api_usage_units",
        "seo_clicks",
        "seo_impressions",
        "adsense_ready",
        "open_campaigns",
        "indexed_urls_count",
        "draft_tool_specs_count",
    ):
        assert key in data
    assert "funnel" in data
    assert "deploy_release" in data
    assert "countries" in data
    assert "top_tools" in data
