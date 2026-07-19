import hashlib

import pytest
from django.contrib.auth import get_user_model

from apps.marketplace.models import ApiKey, generate_api_key, hash_api_key

User = get_user_model()


@pytest.mark.django_db
def test_api_key_create_returns_plaintext_and_stores_hash(settings):
    settings.API_KEY_PEPPER = "test-pepper"
    user = User.objects.create_user(email="dev@example.com", password="password123")

    key, plaintext = ApiKey.create_for_user(user, name="CI key", scopes=["tools:read"])

    assert plaintext.startswith("tv_")
    assert key.key_prefix == plaintext[:8]
    assert key.key_hash == hash_api_key(plaintext)
    assert key.key_hash != plaintext
    assert len(key.key_hash) == 64
    # Peppered SHA-256
    expected = hashlib.sha256(f"test-pepper:{plaintext}".encode()).hexdigest()
    assert key.key_hash == expected
    assert ApiKey.objects.filter(pk=key.pk).exists()
    # Plaintext must not be persisted
    stored = ApiKey.objects.get(pk=key.pk)
    assert plaintext not in (stored.key_hash, stored.key_prefix, stored.name)


@pytest.mark.django_db
def test_generate_api_key_prefix_length():
    plaintext, prefix, digest = generate_api_key()
    assert len(prefix) == 8
    assert plaintext.startswith(prefix)
    assert digest == hash_api_key(plaintext)
