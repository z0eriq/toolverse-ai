from __future__ import annotations

import pytest

from apps.content_factory.autopilot import run_content_autopilot
from apps.content_factory.models import AutopilotRun, ContentItem
from apps.keywords.models import KeywordOpportunity


@pytest.mark.django_db
def test_autopilot_ends_human_review(settings):
    settings.AUTOPILOT_AUTO_PUBLISH = False
    kw = KeywordOpportunity.objects.create(
        keyword="free pdf compress",
        locale="en",
        search_volume=100,
        impressions=100,
        difficulty=30,
        priority_score=5.0,
    )
    run = run_content_autopilot(kw.pk)
    assert run.status == AutopilotRun.Status.HUMAN_REVIEW
    assert run.stage == "human_review"
    assert run.content_item_id is not None
    content = ContentItem.objects.get(pk=run.content_item_id)
    assert content.status == ContentItem.Status.HUMAN_REVIEW
    assert "faq" in run.meta
    assert run.quality_score > 0
