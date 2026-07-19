import pytest
from rest_framework.test import APIClient

from apps.programmatic_seo.models import ProgrammaticPage


@pytest.mark.django_db
def test_programmatic_by_path():
    ProgrammaticPage.objects.create(
        slug="best/pdf-tools",
        path_pattern="best/{topic}",
        title={"en": "Best PDF Tools"},
        description={"en": "PDF tools"},
        body={"en": "<p>PDF</p>"},
        page_type=ProgrammaticPage.PageType.BEST_OF,
        topic="pdf-tools",
        status=ProgrammaticPage.Status.PUBLISHED,
    )
    ProgrammaticPage.objects.create(
        slug="best/draft-only",
        title={"en": "Draft"},
        description={"en": "Draft"},
        page_type=ProgrammaticPage.PageType.BEST_OF,
        status=ProgrammaticPage.Status.DRAFT,
    )

    client = APIClient()
    res = client.get("/api/v1/programmatic/by-path/", {"path": "best/pdf-tools"})
    assert res.status_code == 200
    assert res.data["success"] is True
    assert res.data["data"]["slug"] == "best/pdf-tools"
    assert res.data["data"]["title"]["en"] == "Best PDF Tools"

    missing = client.get("/api/v1/programmatic/by-path/", {"path": "best/draft-only"})
    assert missing.status_code == 404
