from __future__ import annotations

import pytest

from apps.keywords.models import KeywordOpportunity
from apps.tool_intelligence.models import ToolOpportunity, ToolTemplate
from apps.tool_intelligence.services import recompute_tool_opportunities


@pytest.mark.django_db
def test_recompute_tool_opportunities():
    KeywordOpportunity.objects.create(
        keyword="best pdf merger",
        locale="en",
        search_volume=500,
        impressions=500,
        clicks=40,
        ctr=0.08,
        difficulty=40,
        priority_score=10.0,
        suggested_tool_slug="pdf-ocr-extract",
    )
    ToolTemplate.objects.create(
        slug="pdf-ocr-extract",
        category_slug="pdf",
        recipe="pdf",
        priority_weight=1.2,
        description="OCR PDF",
    )
    result = recompute_tool_opportunities()
    assert result["total"] >= 1
    opp = ToolOpportunity.objects.get(suggested_slug="pdf-ocr-extract")
    assert opp.priority_score > 0
    assert opp.demand_score >= 0
    assert opp.category_slug == "pdf"
    assert ToolOpportunity.objects.filter(suggested_slug="new-pdf-tool").exists()
