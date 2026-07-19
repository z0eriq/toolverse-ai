#!/usr/bin/env sh
# Run database migrations as a one-shot job (safe for multi-replica deploys).
# Usage: ./infra/scripts/migrate.sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "==> Validating production environment"
docker compose -f docker-compose.prod.yml run --rm --no-deps api \
  python manage.py validate_production --strict

echo "==> Applying migrations"
docker compose -f docker-compose.prod.yml run --rm --no-deps api \
  python manage.py migrate --noinput

echo "==> Migrations complete"
