#!/usr/bin/env sh
# Zero-downtime-ish production deploy for Docker Compose.
# Pattern: migrate once → rebuild → rolling recreate of api/web → health gate → tag release.
# Usage: ./infra/scripts/deploy.sh [release-tag]
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

RELEASE_TAG="${1:-$(date -u +%Y%m%d%H%M%S)}"
RELEASE_FILE=".deploy-release"
PREVIOUS=""
if [ -f "$RELEASE_FILE" ]; then
  PREVIOUS="$(cat "$RELEASE_FILE")"
fi

echo "==> Deploy release=$RELEASE_TAG (previous=${PREVIOUS:-none})"

# Record previous tag for rollback before mutating stack
if [ -n "$PREVIOUS" ]; then
  echo "$PREVIOUS" > .deploy-previous
fi

./infra/scripts/migrate.sh

echo "==> Building images"
docker compose -f docker-compose.prod.yml build api web worker beat

echo "==> Rolling recreate (api first, then edge)"
docker compose -f docker-compose.prod.yml up -d --no-deps --force-recreate api
sleep 5
docker compose -f docker-compose.prod.yml up -d --no-deps --force-recreate worker beat
docker compose -f docker-compose.prod.yml up -d --no-deps --force-recreate web
docker compose -f docker-compose.prod.yml up -d --no-deps nginx

echo "==> Health gate"
ATTEMPTS=30
i=0
while [ "$i" -lt "$ATTEMPTS" ]; do
  if curl -fsS "http://127.0.0.1/healthz" >/dev/null 2>&1 \
    && curl -fsS "http://127.0.0.1/readyz" >/dev/null 2>&1; then
    echo "==> Healthy"
    echo "$RELEASE_TAG" > "$RELEASE_FILE"
    echo "==> Deployed $RELEASE_TAG"
    exit 0
  fi
  i=$((i + 1))
  sleep 2
done

echo "!! Health gate failed — run ./infra/scripts/rollback.sh" >&2
exit 1
