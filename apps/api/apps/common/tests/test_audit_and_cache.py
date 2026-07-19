import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.common.audit import log_audit
from apps.common.models import AuditLog
from apps.tools_registry.cache import cache_get, cache_set

User = get_user_model()


@pytest.mark.django_db
def test_log_audit_creates_row():
    user = User.objects.create_user(email="auditor@example.com", password="password123")
    factory = RequestFactory()
    request = factory.post("/api/v1/marketplace/keys/")
    request.user = user
    request.META["REMOTE_ADDR"] = "203.0.113.10"
    request.META["HTTP_USER_AGENT"] = "pytest-agent/1.0"

    entry = log_audit(
        request,
        "marketplace.api_key.create",
        resource_type="marketplace.ApiKey",
        resource_id=42,
        meta={"name": "CI"},
    )

    assert entry.pk is not None
    assert AuditLog.objects.filter(pk=entry.pk).exists()
    stored = AuditLog.objects.get(pk=entry.pk)
    assert stored.actor_id == user.pk
    assert stored.action == "marketplace.api_key.create"
    assert stored.resource_type == "marketplace.ApiKey"
    assert stored.resource_id == "42"
    assert stored.ip == "203.0.113.10"
    assert "pytest-agent" in stored.user_agent
    assert stored.meta["name"] == "CI"


@pytest.mark.django_db
def test_log_audit_anonymous_actor_null():
    factory = RequestFactory()
    request = factory.get("/api/v1/tools/")
    request.user = type("Anon", (), {"is_authenticated": False})()

    entry = log_audit(request, "tools.list", resource_type="tools_registry.Tool")
    assert entry.pk is not None
    assert entry.actor_id is None


def test_cache_get_set_roundtrip():
    key = "tools:test:cache:v1"
    assert cache_get(key) is None
    cache_set(key, {"ok": True, "n": 1}, timeout=30)
    assert cache_get(key) == {"ok": True, "n": 1}
