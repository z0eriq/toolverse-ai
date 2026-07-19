from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.email_growth.models import NewsletterSubscriber


@pytest.mark.django_db
def test_newsletter_subscribe():
    client = APIClient()
    url = reverse("newsletter-subscribe")
    resp = client.post(url, {"email": "reader@example.com", "locale": "en"}, format="json")
    assert resp.status_code == 201
    assert resp.data["success"] is True
    assert NewsletterSubscriber.objects.filter(email="reader@example.com").exists()
    # Idempotent re-subscribe
    resp2 = client.post(url, {"email": "reader@example.com"}, format="json")
    assert resp2.status_code == 201
    assert NewsletterSubscriber.objects.filter(email="reader@example.com").count() == 1
