from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.tools_registry.models import Category, Tool


@pytest.mark.django_db
def test_mobile_tools_returns_list():
    category = Category.objects.create(
        slug="developer",
        name={"en": "Developer"},
        description={"en": "Dev"},
    )
    Tool.objects.create(
        tool_id="json-formatter",
        slug="json-formatter",
        category=category,
        name={"en": "JSON Formatter", "ar": "منسق"},
        description={"en": "Format JSON"},
        is_active=True,
    )
    client = APIClient()
    res = client.get(
        "/api/v1/mobile/tools/?compact=1",
        HTTP_X_CLIENT_PLATFORM="ios",
    )
    assert res.status_code == 200
    assert res.data["success"] is True
    data = res.data["data"]
    assert isinstance(data, list)
    assert data
    item = data[0]
    assert set(item.keys()) == {"slug", "category", "name"}
    assert item["name"] == {"en": "JSON Formatter"}
    assert "ar" not in item["name"]
