from __future__ import annotations

import pytest
from django.utils import timezone

from apps.search_console.models import GSCMetricSnapshot, IndexedUrl
from apps.search_console.services import upsert_indexed_urls_from_gsc


@pytest.mark.django_db
def test_upsert_indexed_urls_creates_row():
    GSCMetricSnapshot.objects.create(
        date=timezone.now().date(),
        page="https://toolverse.ai/tools/pdf-merge",
        query="pdf merge",
        clicks=12,
        impressions=400,
        ctr=0.03,
        position=8.5,
    )
    result = upsert_indexed_urls_from_gsc()
    assert result["created"] >= 1
    row = IndexedUrl.objects.get(url_path="/tools/pdf-merge")
    assert row.impressions == 400
    assert row.clicks == 12
    assert row.status == IndexedUrl.Status.INDEXED
    assert row.position == 8.5
    assert row.last_crawled_at is not None
