from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.content_factory.models import ContentItem
from apps.growth_agent.actions import execute_growth_action
from apps.growth_agent.models import GrowthAction

User = get_user_model()


@pytest.mark.django_db
def test_approve_create_content_draft_not_published():
    action = GrowthAction.objects.create(
        action_type=GrowthAction.ActionType.CREATE_CONTENT_DRAFT,
        payload={"keyword": "pdf compressor online", "title": "PDF Compressor Guide"},
        status=GrowthAction.Status.PROPOSED,
    )
    result = execute_growth_action(action)
    assert result.status == GrowthAction.Status.EXECUTED
    assert result.result_ref.get("published") is False
    item = ContentItem.objects.get(pk=result.result_ref["id"])
    assert item.status == ContentItem.Status.HUMAN_REVIEW
    assert item.status != ContentItem.Status.PUBLISHED
    assert item.published_at is None


@pytest.mark.django_db
def test_approve_endpoint_creates_draft():
    admin = User.objects.create_superuser(email="growth-admin@example.com", password="pass12345")
    action = GrowthAction.objects.create(
        action_type=GrowthAction.ActionType.CREATE_CONTENT_DRAFT,
        payload={"keyword": "json formatter", "locale": "en"},
        status=GrowthAction.Status.PROPOSED,
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    res = client.post(f"/api/v1/admin/growth-agent/actions/{action.pk}/approve/")
    assert res.status_code == 200
    assert res.data["success"] is True
    action.refresh_from_db()
    assert action.status == GrowthAction.Status.EXECUTED
    item = ContentItem.objects.get(pk=action.result_ref["id"])
    assert item.status == ContentItem.Status.HUMAN_REVIEW
