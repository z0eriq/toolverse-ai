from __future__ import annotations

import os

from .base import *  # noqa: F401,F403

DEBUG = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


def _require_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise RuntimeError(
            f"Production settings require {name} to be set. "
            "Run `python manage.py validate_production` before deploy."
        )
    return value


# Fail-fast production validation
_secret = _require_env("SECRET_KEY")
if _secret in {"change-me", "insecure-dev-key", "ci-secret-key-not-for-production"} or len(
    _secret
) < 32:
    raise RuntimeError(
        "SECRET_KEY must be a strong random string (32+ chars) in production."
    )
SECRET_KEY = _secret

_allowed = _require_env("ALLOWED_HOSTS")
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()]
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must list at least one host in production.")

_require_env("REDIS_URL")
CELERY_BROKER_URL = _require_env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND") or CELERY_BROKER_URL

# Database: DATABASE_URL or discrete POSTGRES_* vars
if not (os.getenv("DATABASE_URL") or "").strip():
    for key in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST"):
        _require_env(key)
