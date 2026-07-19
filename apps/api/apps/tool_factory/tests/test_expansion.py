from __future__ import annotations

import pytest

from apps.tool_factory.expansion import catalog_capacity_summary, queue_tool_expansion
from apps.tool_factory.models import ToolSpec


@pytest.mark.django_db
def test_queue_tool_expansion_creates_draft_specs():
    result = queue_tool_expansion(category="pdf", limit=5)
    assert result["created"] == 5
    assert result["status"] == ToolSpec.Status.DRAFT
    assert ToolSpec.objects.filter(status=ToolSpec.Status.DRAFT).count() == 5
    assert all(s.startswith("pdf-") for s in result["slugs"])
    # Idempotent skip on second run
    result2 = queue_tool_expansion(category="pdf", limit=5)
    assert result2["created"] == 0
    assert result2["skipped"] == 5


@pytest.mark.django_db
def test_catalog_has_1000_capacity_structure():
    summary = catalog_capacity_summary()
    assert summary["declared_capacity"] == 1000
    assert summary["structural_slots"] >= 250
    assert "pdf" in summary["by_category"]
    assert "business" in summary["by_category"]
