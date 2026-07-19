from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.marketplace.models import SalesLead
from apps.monetization.readiness import adsense_readiness
from apps.monetization.seed import ensure_default_placements


@pytest.mark.django_db
def test_checkout_session_stub_without_stripe(settings):
    settings.STRIPE_SECRET_KEY = ""
    client = APIClient()
    url = reverse("billing-checkout-session")
    resp = client.post(url, {}, format="json")
    assert resp.status_code == 200
    assert resp.data["success"] is True
    data = resp.data["data"]
    assert data["status"] == "stub"
    assert "url" in data


@pytest.mark.django_db
def test_adsense_readiness_flag(settings):
    settings.ADSENSE_CLIENT_ID = ""
    ensure_default_placements()
    result = adsense_readiness()
    assert result["adsense_ready"] is False
    assert result["placements_enabled"] >= 1

    settings.ADSENSE_CLIENT_ID = "ca-pub-1234567890"
    result2 = adsense_readiness()
    assert result2["adsense_ready"] is True
    assert result2["client_id_configured"] is True

    client = APIClient()
    url = reverse("monetization-adsense-ready")
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data["data"]["adsense_ready"] is True


@pytest.mark.django_db
def test_sales_lead_stores_utm_and_company_size():
    client = APIClient()
    url = reverse("marketplace-leads")
    resp = client.post(
        url,
        {
            "name": "Grace Hopper",
            "email": "grace@example.com",
            "company": "Navy Labs",
            "company_size": "51-200",
            "intent": "enterprise",
            "utm_source": "linkedin",
            "utm_medium": "social",
            "utm_campaign": "enterprise-q3",
            "campaign_key": "ent-q3",
            "message": "Need SSO",
        },
        format="json",
    )
    assert resp.status_code == 201
    lead = SalesLead.objects.get(email="grace@example.com")
    assert lead.company_size == "51-200"
    assert lead.utm_source == "linkedin"
    assert lead.campaign_key == "ent-q3"
    assert lead.intent == "enterprise"
