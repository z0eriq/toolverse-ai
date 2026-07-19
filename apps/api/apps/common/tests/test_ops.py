from __future__ import annotations

import os

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.django_db
def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "release" in body


@pytest.mark.django_db
def test_metricsz(client):
    response = client.get("/metricsz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "analytics_events" in body
    assert "revenue_cents" in body
    assert "growth_actions_proposed" in body


@pytest.mark.django_db
def test_readyz_includes_checks(client):
    response = client.get("/readyz")
    assert response.status_code in {200, 503}
    body = response.json()
    assert "checks" in body
    assert "database" in body["checks"]
    assert "cache" in body["checks"]
    assert "celery_broker" in body["checks"]
    assert "release" in body


def test_validate_production_fails_without_secret(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("ALLOWED_HOSTS", "example.com")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    monkeypatch.setenv("USE_SQLITE", "true")
    with pytest.raises(CommandError):
        call_command("validate_production")


def test_validate_production_passes_with_required_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "x" * 40)
    monkeypatch.setenv("ALLOWED_HOSTS", "example.com")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    monkeypatch.setenv("USE_SQLITE", "true")
    call_command("validate_production")
