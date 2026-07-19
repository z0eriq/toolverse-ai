from __future__ import annotations

import pytest

from apps.seo_optimizer.health import compute_seo_health
from apps.seo_optimizer.models import SeoHealthScore
from apps.tools_registry.models import Category, Tool


@pytest.mark.django_db
def test_seo_health_overall_in_range():
    cat, _ = Category.objects.get_or_create(
        slug="text",
        defaults={"name": {"en": "Text"}, "description": {"en": ""}},
    )
    Tool.objects.create(
        tool_id="health-demo",
        slug="health-demo",
        category=cat,
        name={"en": "Health Demo"},
        description={"en": "A reasonably long description for content scoring heuristics."},
        seo_title={"en": "Health Demo Tool Online Free"},
        seo_description={"en": "Use Health Demo to analyze pages with a solid meta description length."},
        seo_keywords=["health", "demo"],
        capabilities=["server"],
        faq=[{"q": "What?", "a": "Demo"}, {"q": "Why?", "a": "Test"}],
        howto_steps=[{"step": 1, "text": "Open"}, {"step": 2, "text": "Run"}],
        related_slugs=["json-formatter", "base64-encode"],
        is_active=True,
    )
    score = compute_seo_health("/tools/text/health-demo")
    assert 0 <= score.overall <= 100
    assert SeoHealthScore.objects.filter(path="/tools/text/health-demo").exists()
    assert score.performance == 70.0
