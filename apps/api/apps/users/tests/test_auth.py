import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_healthz():
    client = APIClient()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
def test_register_and_me():
    client = APIClient()
    response = client.post(
        "/api/v1/auth/register/",
        {"email": "user@example.com", "password": "password123", "name": "Test"},
        format="json",
    )
    assert response.status_code == 201
    access = response.json()["data"]["tokens"]["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    me = client.get("/api/v1/auth/me/")
    assert me.status_code == 200
    assert me.json()["data"]["email"] == "user@example.com"


@pytest.mark.django_db
def test_tools_list_after_sync(settings, tmp_path):
    import json
    from apps.tools_registry.discovery import sync_tools_from_filesystem

    tool_dir = tmp_path / "demo-tool"
    tool_dir.mkdir()
    (tool_dir / "manifest.json").write_text(
        json.dumps(
            {
                "id": "demo-tool",
                "slug": "demo-tool",
                "category": "developer",
                "name": {"en": "Demo"},
                "description": {"en": "Demo"},
                "version": "1.0.0",
                "seo": {"title": {"en": "Demo"}, "keywords": []},
                "capabilities": ["client"],
            }
        ),
        encoding="utf-8",
    )
    settings.TOOLS_DIR = tmp_path
    sync_tools_from_filesystem()
    client = APIClient()
    response = client.get("/api/v1/tools/")
    assert response.status_code == 200
