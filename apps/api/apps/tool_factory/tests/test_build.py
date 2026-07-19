from __future__ import annotations

import pytest

from apps.tool_factory.models import ToolSpec
from apps.tool_factory.services import build_tool_from_spec
from apps.tools_registry.models import Tool
from apps.users.models import User


@pytest.mark.django_db
def test_build_tool_from_spec_creates_tool():
    admin = User.objects.create_superuser(email="factory@example.com", password="password123")
    spec = ToolSpec.objects.create(
        slug="factory-echo",
        category_slug="text",
        name={"en": "Factory Echo"},
        description={"en": "Echo via factory"},
        ui_schema={"fields": [{"name": "text", "type": "textarea"}]},
        pipeline=[
            {"type": "transform", "op": "uppercase", "source": "input.text", "target": "output"},
        ],
        faq=[{"question": {"en": "Free?"}, "answer": {"en": "Yes"}}],
        howto=[{"en": "Type text"}, {"en": "Run"}],
        capabilities=["server"],
        recipe=ToolSpec.Recipe.GENERIC,
        created_by=admin,
        is_viral=True,
        share_text={"en": "Try Factory Echo"},
    )
    result = build_tool_from_spec(spec.pk, user=admin)
    assert result["tool_id"] == "dynamic:factory-echo"
    tool = Tool.objects.get(tool_id="dynamic:factory-echo")
    assert tool.is_active
    assert tool.faq
    assert tool.howto_steps
    assert hasattr(tool, "growth_meta")
    assert tool.growth_meta.is_viral is True
    spec.refresh_from_db()
    assert spec.status == ToolSpec.Status.READY
