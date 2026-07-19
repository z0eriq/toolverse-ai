from __future__ import annotations

import pytest

from apps.programmatic_seo.models import ProgrammaticPage
from apps.programmatic_seo.services import generate_landing_batch


@pytest.mark.django_db
def test_generate_landing_batch_creates_drafts():
    result = generate_landing_batch(
        kinds=["tool", "tutorial", "comparison"],
        limit=6,
        locale="en",
        publish=False,
    )
    assert result["created"] == 6
    assert result["status"] == ProgrammaticPage.Status.DRAFT
    assert ProgrammaticPage.objects.filter(status="draft").count() == 6
    types = set(ProgrammaticPage.objects.values_list("page_type", flat=True))
    assert ProgrammaticPage.PageType.TOOL in types or "tool" in types
    assert ProgrammaticPage.PageType.TUTORIAL in types or "tutorial" in types
