from __future__ import annotations

import pytest

from apps.growth_agent.models import GrowthInsight, GrowthTask
from apps.growth_agent.services import run_growth_agent


@pytest.mark.django_db
def test_growth_agent_creates_insight_on_empty_db():
    run = run_growth_agent()
    assert run.status in {"success", "failed"}
    assert run.insights_created >= 1
    assert GrowthInsight.objects.count() >= 1
    assert GrowthTask.objects.count() >= 1
