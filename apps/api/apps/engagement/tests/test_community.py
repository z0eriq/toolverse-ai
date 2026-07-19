from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.engagement.models import Collection

User = get_user_model()


@pytest.mark.django_db
def test_public_collection_listed_private_not():
    user = User.objects.create_user(email="community@example.com", password="pass12345")
    public = Collection.objects.create(
        user=user,
        name="Public Picks",
        slug="public-picks",
        is_public=True,
        public_slug="public-picks",
    )
    Collection.objects.create(
        user=user,
        name="Secret Bundle",
        slug="secret-bundle",
        is_public=False,
    )

    client = APIClient()
    res = client.get("/api/v1/community/collections/")
    assert res.status_code == 200
    assert res.data["success"] is True
    slugs = {c["public_slug"] for c in res.data["data"]}
    assert public.public_slug in slugs
    assert None not in slugs or "secret-bundle" not in slugs
    assert all(c.get("is_public") for c in res.data["data"])
    names = {c["name"] for c in res.data["data"]}
    assert "Public Picks" in names
    assert "Secret Bundle" not in names
