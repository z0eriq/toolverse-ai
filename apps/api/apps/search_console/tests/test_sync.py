from __future__ import annotations

import pytest

from apps.search_console.services import sync_search_analytics


@pytest.mark.django_db
def test_gsc_sync_skips_without_credentials(settings):
    settings.GSC_CREDENTIALS_JSON = ""
    settings.GSC_CREDENTIALS_FILE = ""
    result = sync_search_analytics()
    assert result["synced"] == 0
    assert result["skipped"] == "no_credentials"
