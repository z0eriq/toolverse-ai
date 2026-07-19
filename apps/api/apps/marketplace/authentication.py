"""
API key authentication for the ToolVerse marketplace.

Wire into settings (parent / deploy config):

    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework_simplejwt.authentication.JWTAuthentication",
            "apps.marketplace.authentication.ApiKeyAuthentication",
        ),
        ...
    }

    API_KEY_PEPPER = os.getenv("API_KEY_PEPPER", SECRET_KEY)
"""

from __future__ import annotations

from django.utils import timezone
from rest_framework import authentication, exceptions

from apps.marketplace.models import ApiKey, hash_api_key


class ApiKeyAuthentication(authentication.BaseAuthentication):
    """Authenticate requests via the ``X-API-Key`` header."""

    header_name = "HTTP_X_API_KEY"

    def authenticate(self, request):
        raw = request.META.get(self.header_name, "").strip()
        if not raw:
            return None

        digest = hash_api_key(raw)
        try:
            api_key = ApiKey.objects.select_related("user").get(key_hash=digest)
        except ApiKey.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("Invalid API key") from exc

        if api_key.is_revoked:
            raise exceptions.AuthenticationFailed("API key has been revoked")

        if not api_key.user.is_active:
            raise exceptions.AuthenticationFailed("User account is disabled")

        ApiKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())
        request.api_key = api_key  # type: ignore[attr-defined]
        return (api_key.user, api_key)
