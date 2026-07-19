from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.common.limits import ToolRunLimitExceeded, check_tool_run_limit, increment_tool_run
from apps.subscriptions.services import ensure_free_subscription, ensure_plans

User = get_user_model()


@pytest.mark.django_db
def test_tool_run_limit_blocks_free_user():
    ensure_plans()
    user = User.objects.create_user(email="free@example.com", password="pass12345")
    ensure_free_subscription(user)
    cache.clear()
    for _ in range(50):
        increment_tool_run(user)
    with pytest.raises(ToolRunLimitExceeded):
        check_tool_run_limit(user)
