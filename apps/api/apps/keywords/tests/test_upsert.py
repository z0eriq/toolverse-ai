from __future__ import annotations

from datetime import date

import pytest

from apps.keywords.models import KeywordOpportunity
from apps.keywords.services import difficulty_from_position, upsert_keywords_from_gsc
from apps.search_console.models import GSCMetricSnapshot, GSCProperty


@pytest.mark.django_db
def test_upsert_keywords_from_gsc():
    prop = GSCProperty.objects.create(site_url="https://example.com/")
    GSCMetricSnapshot.objects.create(
        property=prop,
        date=date.today(),
        query="best pdf tools",
        clicks=10,
        impressions=200,
        ctr=0.05,
        position=8.0,
    )
    GSCMetricSnapshot.objects.create(
        property=prop,
        date=date.today(),
        query="best pdf tools",
        clicks=5,
        impressions=100,
        ctr=0.05,
        position=6.0,
    )
    result = upsert_keywords_from_gsc()
    assert result["total"] >= 1
    opp = KeywordOpportunity.objects.get(keyword="best pdf tools", locale="en")
    assert opp.search_volume == 300
    assert opp.clicks == 15
    assert opp.difficulty == difficulty_from_position(opp.ranking_position)
    assert opp.priority_score > 0
    assert opp.suggested_tool_slug
    assert opp.last_synced_at is not None
