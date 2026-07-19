from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.ai_providers.base import AIResult
from apps.tools_registry.models import Category, Tool


@pytest.mark.django_db
def test_assistant_chat_returns_structure():
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
        search_document="json formatter format validate",
        is_active=True,
    )

    fake = AIResult(
        content=(
            '{"reply":"Try our JSON Formatter.",'
            '"recommended":[{"slug":"json-formatter","category":"developer",'
            '"name":"JSON Formatter","reason":"Formats JSON"}]}'
        ),
        provider="openai",
        model="gpt-test",
        tokens_in=10,
        tokens_out=20,
    )

    client = APIClient()
    with patch("apps.assistant.services.get_ai_router") as mock_router:
        mock_router.return_value.complete.return_value = fake
        res = client.post(
            "/api/v1/assistant/chat/",
            {"message": "I need to format json"},
            format="json",
        )

    assert res.status_code == 200
    assert res.data["success"] is True
    data = res.data["data"]
    assert "reply" in data
    assert isinstance(data["recommended_tools"], list)
    assert data["recommended_tools"]
    item = data["recommended_tools"][0]
    assert set(item.keys()) >= {"slug", "category", "name", "reason"}
    assert item["slug"] == "json-formatter"
