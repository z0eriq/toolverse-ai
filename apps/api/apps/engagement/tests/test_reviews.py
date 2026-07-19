import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.engagement.models import ToolReview
from apps.tools_registry.models import Category, Tool

User = get_user_model()


@pytest.mark.django_db
def test_engagement_review_create():
    user = User.objects.create_user(email="reviewer@example.com", password="pass12345")
    category = Category.objects.create(
        slug="developer",
        name={"en": "Developer"},
        description={"en": "Dev"},
    )
    tool = Tool.objects.create(
        tool_id="json-formatter",
        slug="json-formatter",
        category=category,
        name={"en": "JSON Formatter"},
        description={"en": "Format JSON"},
        is_active=True,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    res = client.post(
        "/api/v1/engagement/reviews/",
        {
            "tool_id": tool.tool_id,
            "rating": 5,
            "title": "Great",
            "body": "Works perfectly for my workflows.",
        },
        format="json",
    )
    assert res.status_code == 201
    assert res.data["success"] is True
    assert res.data["data"]["rating"] == 5
    assert res.data["data"]["status"] == ToolReview.Status.PENDING
    assert ToolReview.objects.filter(user=user, tool=tool).count() == 1
