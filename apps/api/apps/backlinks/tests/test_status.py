from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.backlinks.models import BacklinkOpportunity, BacklinkTarget

User = get_user_model()


@pytest.mark.django_db
def test_backlink_status_transition():
    admin = User.objects.create_superuser(email="backlinks@example.com", password="pass12345")
    target = BacklinkTarget.objects.create(
        url="https://toolverse.ai/tools/pdf/merge",
        path="tools/pdf/merge",
        title="PDF Merge",
    )
    opp = BacklinkOpportunity.objects.create(
        target=target,
        source_domain="techblog.example",
        status=BacklinkOpportunity.Status.OPEN,
        priority=70,
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    res = client.post(
        f"/api/v1/admin/backlinks/opportunities/{opp.pk}/status/",
        {"status": "outreach"},
        format="json",
    )
    assert res.status_code == 200
    opp.refresh_from_db()
    assert opp.status == BacklinkOpportunity.Status.OUTREACH
