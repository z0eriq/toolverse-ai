from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.referrals.models import ReferralAttribution
from apps.referrals.services import attribute_signup, get_or_create_code

User = get_user_model()


@pytest.mark.django_db
def test_self_referral_blocked():
    user = User.objects.create_user(email="ref@example.com", password="pass12345")
    code = get_or_create_code(user)
    attr = attribute_signup(user, code.code, ip="127.0.0.1")
    assert attr is not None
    assert attr.status == ReferralAttribution.Status.BLOCKED

    client = APIClient()
    client.force_authenticate(user=user)
    resp = client.post("/api/v1/referrals/claim/", {"code": code.code}, format="json")
    assert resp.status_code == 400
