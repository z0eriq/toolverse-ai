from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.marketplace.models import SalesLead


@pytest.mark.django_db
def test_sales_lead_post_creates():
    client = APIClient()
    url = reverse("marketplace-leads")
    resp = client.post(
        url,
        {
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "company": "Analytical Engines",
            "intent": "demo",
            "message": "Interested in enterprise",
        },
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["success"] is True
    assert SalesLead.objects.filter(email="ada@example.com").exists()
    lead = SalesLead.objects.get(email="ada@example.com")
    assert lead.intent == "demo"
    assert lead.status == "new"
