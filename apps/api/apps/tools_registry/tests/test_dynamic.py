import pytest
from rest_framework.test import APIClient

from apps.tools_registry.dynamic_models import DynamicToolDefinition
from apps.tools_registry.models import Tool
from apps.tools_registry.publish import publish_dynamic_tool
from apps.users.models import User


@pytest.mark.django_db
def test_publish_and_run_dynamic_tool():
    admin = User.objects.create_superuser(email="admin@example.com", password="password123")
    definition = DynamicToolDefinition.objects.create(
        slug="echo-upper",
        category_slug="text",
        name={"en": "Echo Upper"},
        description={"en": "Uppercase transform"},
        ui_schema={"fields": [{"name": "text", "type": "textarea"}]},
        pipeline=[
            {"type": "transform", "op": "uppercase", "source": "input.text", "target": "output"},
        ],
        capabilities=["server"],
        created_by=admin,
    )
    tool = publish_dynamic_tool(definition)
    assert tool.source == Tool.Source.DYNAMIC
    assert Tool.objects.filter(tool_id="dynamic:echo-upper", is_active=True).exists()

    client = APIClient()
    response = client.post(
        "/api/v1/t/dynamic/echo-upper/run/",
        {"input": {"text": "hello"}},
        format="json",
    )
    assert response.status_code == 200
    assert response.json()["data"]["output"] == "HELLO"
