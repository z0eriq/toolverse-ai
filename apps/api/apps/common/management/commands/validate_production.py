from __future__ import annotations

import os

from django.core.management.base import BaseCommand, CommandError


REQUIRED_KEYS = (
    "SECRET_KEY",
    "ALLOWED_HOSTS",
    "REDIS_URL",
    "CELERY_BROKER_URL",
)


class Command(BaseCommand):
    help = "Validate environment variables required for production deployment"

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Fail if SECRET_KEY looks like a development placeholder",
        )

    def handle(self, *args, **options):
        errors: list[str] = []
        for key in REQUIRED_KEYS:
            if not (os.getenv(key) or "").strip():
                errors.append(f"Missing required env: {key}")

        secret = (os.getenv("SECRET_KEY") or "").strip()
        if options["strict"] or os.getenv("DJANGO_SETTINGS_MODULE", "").endswith(
            "production"
        ):
            if len(secret) < 32:
                errors.append("SECRET_KEY must be at least 32 characters")
            if secret in {
                "change-me",
                "insecure-dev-key",
                "ci-secret-key-not-for-production",
                "change-me-to-a-long-random-string-in-production",
            }:
                errors.append("SECRET_KEY must not be a known development placeholder")

        has_db_url = bool((os.getenv("DATABASE_URL") or "").strip())
        has_pg = all(
            (os.getenv(k) or "").strip()
            for k in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST")
        )
        if not has_db_url and not has_pg and not (
            os.getenv("USE_SQLITE", "").lower() in {"1", "true", "yes"}
        ):
            errors.append(
                "Provide DATABASE_URL or POSTGRES_* vars (or USE_SQLITE=true for local only)"
            )

        if errors:
            for err in errors:
                self.stderr.write(self.style.ERROR(err))
            raise CommandError(f"Production validation failed ({len(errors)} issue(s))")

        self.stdout.write(self.style.SUCCESS("Production environment validation passed"))
