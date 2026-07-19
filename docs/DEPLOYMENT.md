# Production deployment

ToolVerse AI ships with a compose-based production stack designed for **migrate-once, roll replicas, health-gate, rollback**.

## Architecture

| Concern | Mechanism |
|---------|-----------|
| Zero-downtime-ish | Recreate `api` with gunicorn `--graceful-timeout`; nginx keeps serving while new container passes `readyz` |
| Migrations | One-shot `migrate` profile / `infra/scripts/migrate.sh` — **never** on every API boot |
| Health | `/healthz` liveness, `/readyz` readiness (DB + cache + Celery broker), `/metricsz` process counters |
| Rollback | `infra/scripts/rollback.sh` uses `.deploy-previous` from last successful deploy |
| CD | `.github/workflows/deploy.yml` (workflow_dispatch + optional SSH secrets) |

## Deploy

```bash
# On the production host (repo checked out, .env present)
chmod +x infra/scripts/*.sh
export APP_RELEASE=$(git rev-parse --short HEAD)
./infra/scripts/deploy.sh "$APP_RELEASE"
```

Manual migrate only:

```bash
docker compose -f docker-compose.prod.yml --profile migrate run --rm migrate
# or
./infra/scripts/migrate.sh
```

## Rollback

```bash
./infra/scripts/rollback.sh          # previous release
./infra/scripts/rollback.sh <tag>    # explicit git/image tag
```

## Health monitoring

- `GET /healthz` — process up
- `GET /readyz` — database, cache, Celery broker
- `GET /metricsz` — lightweight JSON counters (events 24h, open growth actions, release)
- Compose `healthcheck` on `api` and `web`
- Flower (ops profile): `docker compose -f docker-compose.prod.yml --profile ops up -d flower`

## GitHub Actions

1. Pass CI on the commit.
2. Actions → **Deploy** → `workflow_dispatch`.
3. Optional secrets: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`, `DEPLOY_PATH`.

Without SSH secrets the workflow still documents the contract and records the release tag for operators.

## Pre-flight

```bash
cd apps/api
python manage.py validate_production --strict
```
