from __future__ import annotations

import pytest

from apps.seo_optimizer.models import SeoRecommendation
from apps.seo_optimizer.services import analyze_page
from apps.tools_registry.models import Category, Tool


@pytest.mark.django_db
def test_analyze_page_creates_recommendations():
    cat, _ = Category.objects.get_or_create(
        slug="text",
        defaults={"name": {"en": "Text"}, "description": {"en": ""}},
    )
    Tool.objects.create(
        tool_id="seo-demo",
        slug="seo-demo",
        category=cat,
        name={"en": "SEO Demo"},
        description={"en": "Demo tool"},
        seo_title={"en": "Short"},
        seo_description={"en": "Too short"},
        seo_keywords=[],
        capabilities=["server"],
        faq=[],
        howto_steps=[],
        related_slugs=[],
    )
    recs = analyze_page("/tools/text/seo-demo")
    assert len(recs) >= 2
    assert SeoRecommendation.objects.filter(path="/tools/text/seo-demo").count() >= 2
    types = {r.type for r in recs}
    assert SeoRecommendation.Type.TITLE in types or SeoRecommendation.Type.FAQ in types
