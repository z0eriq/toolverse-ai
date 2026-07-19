from __future__ import annotations

import pytest

from apps.competitor_intel.models import CompetitorDomain, CompetitorKeyword, CompetitorOpportunity
from apps.competitor_intel.services import recompute_competitor_opportunities


@pytest.mark.django_db
def test_recompute_creates_opportunity_from_gap():
    domain = CompetitorDomain.objects.create(domain="rival.example", name="Rival")
    CompetitorKeyword.objects.create(
        competitor=domain,
        keyword="best free pdf merger",
        position=3.0,
        search_volume=5000,
        our_has_coverage=False,
    )
    CompetitorKeyword.objects.create(
        competitor=domain,
        keyword="json formatter",
        position=1.0,
        search_volume=8000,
        our_has_coverage=True,
    )
    result = recompute_competitor_opportunities()
    assert result["created"] >= 1
    assert CompetitorOpportunity.objects.filter(keyword="best free pdf merger").exists()
    assert not CompetitorOpportunity.objects.filter(keyword="json formatter").exists()
