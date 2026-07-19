from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")
load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = os.getenv("SECRET_KEY", "insecure-dev-key-change-me")
DEBUG = os.getenv("DEBUG", "true").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "corsheaders",
    "django_filters",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_prometheus",
    # Local apps
    "apps.common",
    "apps.users",
    "apps.tools_registry",
    "apps.favorites",
    "apps.history",
    "apps.subscriptions",
    "apps.blog",
    "apps.analytics",
    "apps.admin_api",
    "apps.ai_providers",
    "apps.jobs",
    "apps.recommendations",
    "apps.marketplace",
    "apps.content_factory",
    "apps.programmatic_seo",
    "apps.engagement",
    "apps.assistant",
    "apps.tool_factory",
    "apps.monetization",
    "apps.campaigns",
    "apps.search_console",
    "apps.seo_optimizer",
    "apps.keywords",
    "apps.tool_intelligence",
    "apps.email_growth",
    "apps.experiments",
    "apps.workflows",
    "apps.creator_hub",
    "apps.growth_agent",
    "apps.referrals",
    "apps.gamification",
    "apps.launch_readiness",
    "apps.competitor_intel",
    "apps.backlinks",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "apps.common.middleware.SecurityHeadersMiddleware",
    "apps.common.middleware.BlockedIPMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.common.middleware.RequestLoggingMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "toolverse"),
        "USER": os.getenv("POSTGRES_USER", "toolverse"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "toolverse_secret"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    "sync-tools-hourly": {
        "task": "apps.tools_registry.tasks.sync_tools_task",
        "schedule": 3600.0,
    },
    "cleanup-history-daily": {
        "task": "apps.history.tasks.cleanup_old_history",
        "schedule": 86400.0,
    },
    "rebuild-tool-affinities-daily": {
        "task": "apps.recommendations.tasks.rebuild_tool_affinities",
        "schedule": 86400.0,
    },
    "rollup-analytics-daily": {
        "task": "apps.analytics.tasks.rollup_analytics_daily",
        "schedule": 86400.0,
    },
    "cleanup-jobs-daily": {
        "task": "apps.jobs.tasks.cleanup_old_jobs",
        "schedule": 86400.0,
    },
    "sync-gsc-daily": {
        "task": "apps.search_console.tasks.sync_gsc_daily",
        "schedule": 86400.0,
    },
    "recompute-tool-opportunities-daily": {
        "task": "apps.tool_intelligence.tasks.recompute_tool_opportunities_daily",
        "schedule": 86400.0,
    },
    "recompute-keywords-daily": {
        "task": "apps.keywords.tasks.recompute_keywords_from_gsc",
        "schedule": 86400.0,
    },
    "send-weekly-digest": {
        "task": "apps.email_growth.tasks.send_weekly_digest",
        "schedule": 604800.0,
    },
    "backup-database-daily": {
        "task": "apps.common.tasks.backup_database_daily",
        "schedule": 86400.0,
    },
    "recompute-seo-health-daily": {
        "task": "apps.seo_optimizer.tasks.recompute_seo_health_daily",
        "schedule": 86400.0,
    },
    "run-growth-agent-daily": {
        "task": "apps.growth_agent.tasks.run_growth_agent_daily",
        "schedule": 86400.0,
    },
    "recompute-tool-scores-daily": {
        "task": "apps.tool_intelligence.tasks.recompute_tool_scores_daily",
        "schedule": 86400.0,
    },
    "generate-seo-opportunity-tasks-weekly": {
        "task": "apps.seo_optimizer.tasks.generate_seo_opportunity_tasks_weekly",
        "schedule": 604800.0,
    },
    "run-readiness-checks-daily": {
        "task": "apps.launch_readiness.tasks.run_readiness_checks_daily",
        "schedule": 86400.0,
    },
    "run-seo-autopilot-daily": {
        "task": "apps.seo_optimizer.tasks.run_seo_autopilot_daily",
        "schedule": 86400.0,
    },
    "generate-invoices-from-usage-monthly": {
        "task": "apps.marketplace.tasks.generate_invoices_from_usage_monthly",
        "schedule": 2592000.0,
    },
}

CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if o.strip()
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "apps.marketplace.authentication.ApiKeyAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.StandardPagination",
    "PAGE_SIZE": 24,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("RATE_LIMIT_ANON", "60/minute"),
        "user": os.getenv("RATE_LIMIT_USER", "120/minute"),
        "auth": "10/minute",
        "tool": "30/minute",
        "ai": "20/minute",
        "jobs": "30/minute",
        "marketplace": "60/minute",
        "assistant": "20/minute",
        "mobile": os.getenv("RATE_LIMIT_MOBILE", "90/minute"),
        "extension": os.getenv("RATE_LIMIT_EXTENSION", "60/minute"),
    },
    "EXCEPTION_HANDLER": "apps.common.exceptions.custom_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", "15"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME_DAYS", "7"))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ToolVerse AI API",
    "DESCRIPTION": "REST API for the ToolVerse AI platform",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.request": {"level": "WARNING", "propagate": True},
        "toolverse": {"level": "INFO", "propagate": True},
    },
}

# Cloudflare R2
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "toolverse")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "")
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL", "")

# AdSense / Stripe monetization
ADSENSE_CLIENT_ID = os.getenv("ADSENSE_CLIENT_ID", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_PRICE_ID_PREMIUM = os.getenv("STRIPE_PRICE_ID_PREMIUM", "")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "https://toolverse.ai/pricing?checkout=success")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "https://toolverse.ai/pricing?checkout=cancel")
DEPLOY_RELEASE = os.getenv("DEPLOY_RELEASE", os.getenv("SENTRY_RELEASE", os.getenv("GIT_SHA", "")))

SENTRY_DSN = os.getenv("SENTRY_DSN", "")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", os.getenv("ENVIRONMENT", "development"))
SENTRY_RELEASE = os.getenv("SENTRY_RELEASE", os.getenv("GIT_SHA", ""))
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1") or "0.1")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        environment=SENTRY_ENVIRONMENT,
        release=SENTRY_RELEASE or None,
        send_default_pii=False,
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.0") or "0.0"),
    )

# Database backups (Celery beat / management command)
BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "false").lower() in {"1", "true", "yes"}
BACKUP_DIR = os.getenv("BACKUP_DIR", str(BASE_DIR / "backups"))

TOOLS_DIR = BASE_DIR / "tools"

# Locales (frontend i18n + content / programmatic SEO). See apps.common.locales.
from apps.common.locales import DEFAULT_LOCALE as DEFAULT_LOCALE  # noqa: E402
from apps.common.locales import SUPPORTED_LOCALES as SUPPORTED_LOCALES  # noqa: E402

# AI providers
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
AI_DEFAULT_PROVIDER = os.getenv("AI_DEFAULT_PROVIDER", "openai")
AI_FALLBACK_PROVIDERS = os.getenv("AI_FALLBACK_PROVIDERS", "openrouter,deepseek")
AI_OPENROUTER_REFERER = os.getenv("AI_OPENROUTER_REFERER", "https://toolverse.ai")
API_KEY_PEPPER = os.getenv("API_KEY_PEPPER", SECRET_KEY)

# Google Search Console
GSC_CREDENTIALS_JSON = os.getenv("GSC_CREDENTIALS_JSON", "")
GSC_CREDENTIALS_FILE = os.getenv("GSC_CREDENTIALS_FILE", "")
GSC_SITE_URL = os.getenv("GSC_SITE_URL", "https://toolverse.ai/")

# Web Push (VAPID)
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", "mailto:admin@toolverse.ai")

# Content Autopilot — when False, runs stop at human_review
AUTOPILOT_AUTO_PUBLISH = os.getenv("AUTOPILOT_AUTO_PUBLISH", "false").lower() in {
    "1",
    "true",
    "yes",
}
