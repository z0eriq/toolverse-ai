from __future__ import annotations

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model

from apps.creator_hub.models import CreatorSubmission, CreatorUsageStat
from apps.creator_hub.services import (
    approve_submission,
    get_or_create_creator_profile,
    rollup_creator_usage,
)

User = get_user_model()


@pytest.mark.django_db
def test_rollup_creates_usage_stat():
    user = User.objects.create_user(email="creator@example.com", password="pass12345")
    profile = get_or_create_creator_profile(user)
    submission = CreatorSubmission.objects.create(
        creator=profile,
        type=CreatorSubmission.Type.TOOL,
        payload={"slug": "creator-widget", "name": "Creator Widget"},
        status=CreatorSubmission.Status.PENDING,
    )
    approve_submission(submission)
    submission.refresh_from_db()
    assert submission.tool_spec_id is not None

    end = date.today()
    start = end - timedelta(days=7)
    result = rollup_creator_usage(start, end)
    assert result["created"] + result["updated"] >= 1
    assert CreatorUsageStat.objects.filter(submission=submission).exists()
