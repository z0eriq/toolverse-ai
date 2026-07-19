from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.experiments.models import Experiment


@pytest.mark.django_db
def test_experiment_assign():
    Experiment.objects.create(
        key="home-cta",
        name="Home CTA",
        variants=[
            {"key": "control", "weight": 50},
            {"key": "variant_b", "weight": 50},
        ],
        is_active=True,
    )
    client = APIClient()
    url = reverse("experiments-assign")
    resp = client.get(url, {"key": "home-cta", "subject_key": "user-abc"})
    assert resp.status_code == 200
    assert resp.data["success"] is True
    assert resp.data["data"]["variant"] in {"control", "variant_b"}
    # Sticky assignment
    resp2 = client.get(url, {"key": "home-cta", "subject_key": "user-abc"})
    assert resp2.data["data"]["variant"] == resp.data["data"]["variant"]
