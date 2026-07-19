import pytest

from apps.content_factory.models import ContentItem


@pytest.mark.django_db
def test_content_item_status_enum_values():
    assert ContentItem.Status.DRAFT == "draft"
    assert ContentItem.Status.AI_GENERATED == "ai_generated"
    assert ContentItem.Status.HUMAN_REVIEW == "human_review"
    assert ContentItem.Status.APPROVED == "approved"
    assert ContentItem.Status.PUBLISHED == "published"

    item = ContentItem.objects.create(
        title="Test",
        slug="test-content",
        body="Hello",
        status=ContentItem.Status.DRAFT,
    )
    assert item.status == "draft"
    item.status = ContentItem.Status.AI_GENERATED
    item.save()
    item.refresh_from_db()
    assert item.status == ContentItem.Status.AI_GENERATED
