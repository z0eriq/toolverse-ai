#!/usr/bin/env sh
# Rollback to previous release tag recorded by deploy.sh.
# Usage: ./infra/scripts/rollback.sh [optional-explicit-tag]
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

TARGET="${1:-}"
if [ -z "$TARGET" ] && [ -f .deploy-previous ]; then
  TARGET="$(cat .deploy-previous)"
fi

if [ -z "$TARGET" ]; then
  echo "No previous release recorded. Pass an explicit image/git tag." >&2
  exit 1
fi

echo "==> Rolling back to $TARGET"

# Prefer git checkout when TARGET looks like a git ref; otherwise recreate from current compose.
if git rev-parse --verify "$TARGET" >/dev/null 2>&1; then
  git checkout "$TARGET" -- docker-compose.prod.yml infra/docker apps/api apps/web || true
fi

docker compose -f docker-compose.prod.yml up -d --no-deps --force-recreate api web worker beat nginx

ATTEMPTS=30
i=0
while [ "$i" -lt "$ATTEMPTS" ]; do
  if curl -fsS "http://127.0.0.1/healthz" >/dev/null 2>&1 \
    && curl -fsS "http://127.0.0.1/readyz" >/dev/null 2>&1; then
    echo "$TARGET" > .deploy-release
    echo "==> Rollback healthy ($TARGET)"
    exit 0
  fi
  i=$((i + 1))
  sleep 2
done

echo "!! Rollback health gate failed" >&2
exit 1
