import json

import pytest

from apps.tools_registry.discovery import sync_tools_from_filesystem
from apps.tools_registry.models import Tool


@pytest.mark.django_db
def test_sync_tools(tmp_path, settings):
    tool_dir = tmp_path / "sample-tool"
    tool_dir.mkdir()
    manifest = {
        "id": "sample-tool",
        "slug": "sample-tool",
        "category": "developer",
        "name": {"en": "Sample"},
        "description": {"en": "Sample tool"},
        "version": "1.0.0",
        "seo": {"title": {"en": "Sample"}, "keywords": ["sample"]},
        "capabilities": ["client"],
    }
    (tool_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    settings.TOOLS_DIR = tmp_path
    result = sync_tools_from_filesystem()
    assert result["created"] == 1
    assert Tool.objects.filter(tool_id="sample-tool").exists()
