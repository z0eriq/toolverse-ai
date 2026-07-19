from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.creator_hub.models import CreatorSubmission
from apps.tool_factory.models import ToolSpec

User = get_user_model()


@pytest.mark.django_db
def test_creator_submit_approve_creates_toolspec():
    creator = User.objects.create_user(email="creator@example.com", password="pass12345")
    admin = User.objects.create_superuser(email="admin-creator@example.com", password="pass12345")

    client = APIClient()
    client.force_authenticate(user=creator)
    create = client.post(
        "/api/v1/creator/submissions/",
        {
            "type": "tool",
            "payload": {
                "slug": "creator-demo-tool",
                "name": "Creator Demo Tool",
                "description": "Built by a creator",
                "category_slug": "ai",
            },
        },
        format="json",
    )
    assert create.status_code == 201
    submission_id = create.data["data"]["id"]

    submit = client.post(f"/api/v1/creator/submissions/{submission_id}/submit/", format="json")
    assert submit.status_code == 200
    assert submit.data["data"]["status"] == CreatorSubmission.Status.PENDING

    admin_client = APIClient()
    admin_client.force_authenticate(user=admin)
    approve = admin_client.post(
        f"/api/v1/admin/creator/submissions/{submission_id}/approve/",
        {"notes": "Looks good"},
        format="json",
    )
    assert approve.status_code == 200
    assert approve.data["data"]["status"] == CreatorSubmission.Status.APPROVED
    assert approve.data["data"]["tool_spec_slug"] == "creator-demo-tool"
    assert ToolSpec.objects.filter(slug="creator-demo-tool", status=ToolSpec.Status.DRAFT).exists()
    stub_fields = CreatorSubmission.objects.get(pk=submission_id)
    assert stub_fields.reviewer_notes == "Looks good"
