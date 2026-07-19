from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_launch_readiness_returns_categorized_checks():
    admin = User.objects.create_user(
        email="admin-lr@example.com",
        password="pass12345",
        role=User.Role.ADMIN,
        is_staff=True,
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    url = reverse("admin-launch-readiness")
    resp = client.post(url)
    assert resp.status_code == 200
    assert resp.data["success"] is True
    checks = resp.data["data"]
    assert isinstance(checks, list)
    assert len(checks) >= 1
    categories = {c["category"] for c in checks}
    assert categories
    for c in checks:
        assert "key" in c
        assert "category" in c
        assert "status" in c
