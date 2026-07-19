from __future__ import annotations

import pytest

from apps.programmatic_seo.models import ProgrammaticPage
from apps.programmatic_seo.services import generate_programmatic_batch


@pytest.mark.django_db
def test_batch_creates_unique_slugs():
    result = generate_programmatic_batch(
        page_type=ProgrammaticPage.PageType.USE_CASE,
        limit=5,
        locale="en",
        publish=False,
    )
    assert result["created"] == 5
    assert result["status"] == ProgrammaticPage.Status.DRAFT
    slugs = result["slugs"]
    assert len(slugs) == len(set(slugs))
    assert ProgrammaticPage.objects.filter(slug__in=slugs, status="draft").count() == 5

    # Second batch should still create unique slugs
    result2 = generate_programmatic_batch(
        page_type=ProgrammaticPage.PageType.USE_CASE,
        limit=3,
        locale="en",
        publish=False,
    )
    assert result2["created"] == 3
    overlap = set(slugs) & set(result2["slugs"])
    assert not overlap
