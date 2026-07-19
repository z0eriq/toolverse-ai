import os

from .base import *  # noqa: F401,F403

DEBUG = True

# Allow local SQLite when Postgres is unavailable (set USE_SQLITE=true)
if os.getenv("USE_SQLITE", "false").lower() in {"1", "true", "yes"}:
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }
    CACHES = {  # noqa: F405
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
