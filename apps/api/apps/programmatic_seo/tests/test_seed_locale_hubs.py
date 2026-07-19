from __future__ import annotations

import pytest
from django.core.management import call_command

from apps.common.locales import SUPPORTED_LOCALES
from apps.programmatic_seo.models import ProgrammaticPage


@pytest.mark.django_db
def test_seed_locale_hubs():
    call_command("seed_locale_hubs")
    for locale in SUPPORTED_LOCALES:
        assert ProgrammaticPage.objects.filter(slug=f"locale-hub-{locale}").exists()
