from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.ai_providers.base import AIResult
from apps.assistant.services import detect_intent
from apps.tools_registry.models import Category, Tool


@pytest.mark.django_db
def test_upgrade_to_premium_returns_pricing_cta():
    assert detect_intent("I want to upgrade to premium") == "premium_upsell"

    category = Category.objects.create(
        slug="developer",
        name={"en": "Developer"},
        description={"en": "Dev"},
    )
    Tool.objects.create(
        tool_id="json-formatter",
        slug="json-formatter",
        category=category,
        name={"en": "JSON Formatter"},
        description={"en": "Format JSON"},
        search_document="json formatter",
        is_active=True,
    )
    fake = AIResult(
        content='{"reply":"You can upgrade anytime.","recommended":[]}',
        provider="openai",
        model="gpt-test",
        tokens_in=5,
        tokens_out=10,
    )
    client = APIClient()
    with patch("apps.assistant.services.get_ai_router") as mock_router:
        mock_router.return_value.complete.return_value = fake
        res = client.post(
            "/api/v1/assistant/chat/",
            {"message": "upgrade to premium please"},
            format="json",
        )
    assert res.status_code == 200
    meta = res.data["data"]["meta"]
    assert meta["intent"] == "premium_upsell"
    assert meta["suggested_cta"]["href"] == "/pricing"
