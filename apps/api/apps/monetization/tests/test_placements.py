from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.monetization.models import AdPlacement
from apps.monetization.seed import ensure_default_placements


@pytest.mark.django_db
def test_public_placements_endpoint():
    ensure_default_placements()
    assert AdPlacement.objects.count() >= 4
    client = APIClient()
    response = client.get("/api/v1/monetization/placements/")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) >= 4
