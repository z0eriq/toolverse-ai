import pytest

from apps.recommendations.services import get_related_tools
from apps.tools_registry.models import Category, Tool


@pytest.mark.django_db
def test_related_tools_cold_start_same_category_by_usage():
    category = Category.objects.create(
        slug="developer",
        name={"en": "Developer"},
        description={"en": "Dev tools"},
        order=1,
    )
    other_category = Category.objects.create(
        slug="design",
        name={"en": "Design"},
        description={"en": "Design tools"},
        order=2,
    )

    base = Tool.objects.create(
        tool_id="json-formatter",
        slug="json-formatter",
        category=category,
        name={"en": "JSON Formatter"},
        description={"en": "Format JSON"},
        usage_count=10,
        related_slugs=[],
    )
    high = Tool.objects.create(
        tool_id="base64",
        slug="base64",
        category=category,
        name={"en": "Base64"},
        description={"en": "Encode"},
        usage_count=100,
        related_slugs=[],
    )
    mid = Tool.objects.create(
        tool_id="uuid",
        slug="uuid",
        category=category,
        name={"en": "UUID"},
        description={"en": "Generate"},
        usage_count=50,
        related_slugs=[],
    )
    Tool.objects.create(
        tool_id="color-picker",
        slug="color-picker",
        category=other_category,
        name={"en": "Color"},
        description={"en": "Pick"},
        usage_count=999,
        related_slugs=[],
    )

    related = get_related_tools(base.slug, limit=6)
    slugs = [t.slug for t in related]

    assert high.slug in slugs
    assert mid.slug in slugs
    assert "color-picker" not in slugs
    assert base.slug not in slugs
    assert slugs[0] == high.slug
    assert slugs[1] == mid.slug


@pytest.mark.django_db
def test_related_tools_prefers_related_slugs_override():
    category = Category.objects.create(
        slug="developer",
        name={"en": "Developer"},
        description={"en": "Dev tools"},
    )
    Tool.objects.create(
        tool_id="a",
        slug="tool-a",
        category=category,
        name={"en": "A"},
        description={"en": "A"},
        usage_count=1,
        related_slugs=["tool-c", "tool-b"],
    )
    Tool.objects.create(
        tool_id="b",
        slug="tool-b",
        category=category,
        name={"en": "B"},
        description={"en": "B"},
        usage_count=99,
        related_slugs=[],
    )
    Tool.objects.create(
        tool_id="c",
        slug="tool-c",
        category=category,
        name={"en": "C"},
        description={"en": "C"},
        usage_count=1,
        related_slugs=[],
    )

    related = get_related_tools("tool-a", limit=6)
    assert [t.slug for t in related] == ["tool-c", "tool-b"]
