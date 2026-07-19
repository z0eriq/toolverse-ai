from __future__ import annotations

import pytest

from apps.keywords.models import KeywordOpportunity
from apps.seo_optimizer.models import SeoOpportunityTask
from apps.seo_optimizer.services import generate_seo_opportunity_tasks


@pytest.mark.django_db
def test_generate_seo_opportunity_tasks_empty_ok():
    result = generate_seo_opportunity_tasks()
    assert result["created"] >= 0


@pytest.mark.django_db
def test_generate_seo_opportunity_tasks_with_keyword():
    KeywordOpportunity.objects.create(
        keyword="best pdf compressor",
        locale="en",
        search_volume=1000,
        impressions=500,
        priority_score=88.0,
        suggested_tool_slug="pdf-compressor",
    )
    result = generate_seo_opportunity_tasks()
    assert result["created"] >= 1
    assert SeoOpportunityTask.objects.filter(source="keyword").count() >= 1
