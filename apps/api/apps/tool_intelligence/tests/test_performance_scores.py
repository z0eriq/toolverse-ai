from __future__ import annotations

import pytest

from apps.tool_intelligence.services import recompute_tool_performance_scores
from apps.tools_registry.models import Category, Tool


@pytest.mark.django_db
def test_tool_performance_scores_empty_ok():
    result = recompute_tool_performance_scores()
    assert result["total"] == 0
    from apps.tool_intelligence.models import ToolPerformanceScore

    assert ToolPerformanceScore.objects.count() == 0


@pytest.mark.django_db
def test_tool_performance_scores_bounds():
    cat = Category.objects.create(slug="test-cat", name={"en": "Test"}, description={"en": ""})
    tool = Tool.objects.create(
        tool_id="test/hello",
        slug="hello",
        category=cat,
        name={"en": "Hello"},
        description={"en": "Hi"},
        usage_count=10,
    )
    result = recompute_tool_performance_scores()
    assert result["updated"] >= 1
    from apps.tool_intelligence.models import ToolPerformanceScore

    score = ToolPerformanceScore.objects.get(tool=tool)
    for field in (
        "traffic_score",
        "usage_score",
        "revenue_score",
        "seo_score",
        "retention_score",
        "priority_score",
    ):
        val = getattr(score, field)
        assert 0.0 <= val <= 100.0
