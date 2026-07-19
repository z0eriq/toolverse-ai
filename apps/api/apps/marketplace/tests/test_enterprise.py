from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.marketplace.models import DeveloperOrganization
from apps.subscriptions.models import Plan
from apps.subscriptions.services import ensure_plans

User = get_user_model()


@pytest.mark.django_db
def test_plan_limits_fields():
    ensure_plans()
    free = Plan.objects.get(slug="free")
    premium = Plan.objects.get(slug="premium")
    assert free.monthly_tool_runs == 50
    assert free.api_monthly_quota == 1000
    assert free.ads_free is False
    assert free.history_days == 30
    assert premium.name == "Pro"
    assert premium.monthly_tool_runs == -1
    assert premium.ads_free is True
    assert premium.api_monthly_quota >= 1000


@pytest.mark.django_db
def test_org_create():
    user = User.objects.create_user(email="dev@example.com", password="pass12345")
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("marketplace-orgs")
    resp = client.post(url, {"name": "Acme Tools", "plan_tier": "pro"}, format="json")
    assert resp.status_code == 201
    assert resp.data["success"] is True
    org = DeveloperOrganization.objects.get(name="Acme Tools")
    assert org.owner_id == user.pk
    assert org.plan_tier == "pro"
