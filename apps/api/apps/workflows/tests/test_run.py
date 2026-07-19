from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.workflows.models import Workflow
from apps.workflows.services import run_workflow

User = get_user_model()


@pytest.mark.django_db
def test_workflow_two_step_transform():
    user = User.objects.create_user(email="wf@example.com", password="pass12345")
    workflow = Workflow.objects.create(
        owner=user,
        name="Upper then trim",
        slug="upper-trim",
        steps=[
            {"type": "transform", "op": "uppercase", "source": "input.text", "target": "output"},
            {"type": "transform", "op": "trim", "source": "output", "target": "output"},
        ],
        visibility=Workflow.Visibility.PRIVATE,
    )
    run = run_workflow(workflow, {"text": "  hello world  "}, user=user)
    assert run.status == "success"
    assert run.output["output"] == "HELLO WORLD"


@pytest.mark.django_db
def test_workflow_share_token():
    user = User.objects.create_user(email="share@example.com", password="pass12345")
    workflow = Workflow.objects.create(
        owner=user,
        name="Shared WF",
        slug="shared-wf",
        steps=[{"type": "transform", "op": "lowercase", "source": "input.text", "target": "output"}],
        visibility=Workflow.Visibility.UNLISTED,
    )
    client = APIClient()
    res = client.get(f"/api/v1/workflows/shared/{workflow.share_token}/")
    assert res.status_code == 200
    assert res.data["success"] is True
    assert res.data["data"]["slug"] == "shared-wf"

    # Private should 404
    workflow.visibility = Workflow.Visibility.PRIVATE
    workflow.save(update_fields=["visibility", "updated_at"])
    res2 = client.get(f"/api/v1/workflows/shared/{workflow.share_token}/")
    assert res2.status_code == 404
