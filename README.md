# ToolVerse AI

The largest free online tools platform — modular, SEO-first, production-ready.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS v4, Framer Motion, TanStack Query, next-intl |
| Backend | Django 6, DRF, SimpleJWT, Celery, Celery Beat |
| Data | PostgreSQL, Redis |
| Storage | Cloudflare R2 |
| Edge | Cloudflare CDN/WAF, Nginx |
| Ops | Docker Compose, GitHub Actions, Sentry hooks, Prometheus |

## Monorepo layout

```
apps/web          Next.js App Router
apps/api          Django 6 + DRF
packages/tool-sdk Shared tool manifest contracts
packages/api-client Thin TS client (marketplace + mobile)
infra/            Docker + Nginx
```

## Adding a new tool (no core changes)

### Filesystem plugins (code)

1. Backend: create `apps/api/tools/<tool-id>/` with `manifest.json`, `__init__.py` (`plugin`), optional `views.py`
2. Frontend: create `apps/web/src/tools/<tool-id>/` with `manifest.ts`, `Tool.tsx`, `schema.ts`, `index.ts`
3. Run:
   - `python manage.py sync_tools` (API)
   - `npm run generate:tools --workspace=@toolverse/web`
4. Deploy — registry + sitemap + search pick it up automatically

### Dynamic Tool Builder (no code)

1. Sign in as admin → `/admin` → **Tool Builder**
2. Define metadata, `ui_schema`, and `pipeline` (transform / template / ai / http)
3. Publish — creates a `Tool` with `source=dynamic`
4. Runtime: `POST /api/v1/t/dynamic/<slug>/run/`

## Enterprise platform features

| Feature | Endpoint / location |
|---------|---------------------|
| AI providers | `POST /api/v1/ai/complete/`, admin AI usage |
| Async jobs | `POST /api/v1/jobs/`, `GET /api/v1/jobs/<id>/` |
| Recommendations | `GET /api/v1/tools/<slug>/related/` |
| Analytics dashboard | `GET /api/v1/analytics/dashboard/` |
| API marketplace | `/api/v1/marketplace/keys/`, Developers portal |
| SEO | FAQ/HowTo/SoftwareApplication JSON-LD, split sitemaps |

## Growth Engine

| Feature | Endpoint / location |
|---------|---------------------|
| Content Factory (admin) | `/api/v1/admin/content/` — templates, CRUD, publish, regenerate |
| Programmatic SEO | `GET /api/v1/programmatic/`, `GET /api/v1/programmatic/by-path/?path=…`, sitemap |
| Seed programmatic pages | `python manage.py seed_programmatic_pages` (~30 starters) |
| Engagement | `/api/v1/engagement/` — saved outputs, collections, reviews, comments |
| AI Assistant | `POST /api/v1/assistant/chat/` (rate limit scope `assistant`) |
| Growth analytics | `GET /api/v1/analytics/growth/` |
| Locales | `SUPPORTED_LOCALES = en,ar,es,fr,de,pt,zh` (`apps.common.locales`) |
| Tool relationships | `ToolRelationship` enriches `GET /api/v1/tools/<slug>/related/` |

## Traffic / Revenue Engine

| Feature | Endpoint / location |
|---------|---------------------|
| Tool Factory (admin) | `/api/v1/admin/tool-factory/specs/` — CRUD, `POST …/build/`, `POST …/publish/` |
| Seed expansion pack | `python manage.py seed_tool_expansion` (~50 PDF/Images/AI/Developer/Calculators tools) |
| Monetization (public) | `GET /api/v1/monetization/placements/`, `…/affiliates/`, `…/sponsored/` |
| Revenue (admin) | `/api/v1/admin/revenue/` — placements/sponsored/affiliates CRUD + `summary/` |
| Seed ad placements | `python manage.py seed_monetization` |
| Search Console (admin) | `/api/v1/admin/gsc/overview/`, `…/queries/`, `…/pages/` (daily Celery sync) |
| SEO Optimizer (admin) | `POST /api/v1/admin/seo/analyze/`, `GET …/recommendations/`, accept/dismiss |
| Web Push | `POST /api/v1/push/subscribe/` (auth), admin `POST /api/v1/admin/push/test-ping/` |
| Viral meta | `ToolGrowthMeta` OneToOne on `Tool` (`is_viral`, `share_text`, OG/platforms) |

## Global Launch Engine

| Feature | Endpoint / location |
|---------|---------------------|
| Keywords (admin) | `GET /api/v1/admin/keywords/`, `GET …/top/?limit=50` (GSC upsert after sync) |
| Tool opportunities | `GET /api/v1/admin/opportunities/`, `POST …/<id>/queue/` → ToolSpec draft |
| Seed tool templates | `python manage.py seed_tool_templates` (~10 templates) |
| Content Autopilot | `POST/GET /api/v1/admin/autopilot/runs/`, `POST …/<id>/approve/` |
| Authority pages | `python manage.py seed_authority_pages` (`best-ai-tools`, `free-tools-for-students`, …) |
| Newsletter | `POST /api/v1/newsletter/subscribe/` |
| Email campaigns (admin) | `/api/v1/admin/email/campaigns/`, `POST …/<id>/send-test/` (weekly digest beat) |
| Experiments | `GET /api/v1/experiments/assign/?key=`, `POST /api/v1/experiments/track/` |
| Experiment results | `GET /api/v1/admin/experiments/`, `GET …/<id>/results/` |
| Plan limits | `Plan.monthly_tool_runs` / `api_monthly_quota` / `ads_free` / `history_days` (Pro = unlimited) |
| Marketplace orgs | `GET/POST /api/v1/marketplace/orgs/`, `GET …/analytics/` |
| Invoices (admin) | `GET /api/v1/admin/marketplace/invoices/` |
| Export OpenAPI | `python manage.py export_api_docs` → `apps/web/public/openapi.json` |

## GTM Revenue Optimization

| Feature | Endpoint / location |
|---------|---------------------|
| Command Center | `GET /api/v1/admin/command-center/?days=30` (admin tab) |
| Tool performance scores | `GET /api/v1/admin/tool-scores/` (daily Celery) |
| SEO opportunity tasks | `/api/v1/admin/seo/opportunity-tasks/` + generate |
| Growth PM tasks | `/api/v1/admin/growth-agent/tasks/` |
| Launch readiness | `GET/POST /api/v1/admin/launch-readiness/` |
| Creator usage/payouts | `/api/v1/creator/usage/`, `/payouts/`, admin rollup |
| Enterprise leads | `POST /api/v1/marketplace/leads/`, page `/enterprise` |
| Locale hubs | `/l/[lang]`, `seed_locale_hubs`, sitemap entries |
| Referrals | `/api/v1/referrals/me/`, claim, `/r/[code]` |
| Gamification | `/api/v1/gamification/me/`, badges; dashboard strip |

## Launch Scale Layer

| Feature | Endpoint / location |
|---------|---------------------|
| Production validate | `python manage.py validate_production` |
| DB backup | `python manage.py backup_database` (Celery daily when `BACKUP_ENABLED=true`) |
| Health | `/healthz`, `/readyz` (DB + cache + Celery broker) |
| Flower | Compose service on `:5555` (`FLOWER_BASIC_AUTH`) |
| Security checklist | [`SECURITY.md`](SECURITY.md) |
| SEO Health Score | `GET/POST /api/v1/admin/seo/health/`, `POST …/recompute/` |
| Growth AI Agent | `/api/v1/admin/growth-agent/runs/`, `…/insights/` |
| Workflows | `/api/v1/workflows/`, templates, share token, web `/workflows` |
| Community | `/api/v1/community/profiles/<user>/`, `/collections/`, pages `/community`, `/u/[user]` |
| Moderation queue | `GET /api/v1/admin/moderation/queue/` |
| Creator hub | `/api/v1/creator/`, admin approve/reject, web `/creator` |

## Launch / revenue stack

Activation steps: **[docs/LAUNCH.md](docs/LAUNCH.md)** · Deploy runbooks: **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**

| Feature | Endpoint / location |
|---------|---------------------|
| Conversion funnel | `GET /api/v1/analytics/funnels/?days=30` (admin) |
| UTM track | `POST /api/v1/analytics/track/` (`utm_*`, `campaign_key`) |
| Indexed URLs | `GET /api/v1/admin/gsc/indexed-urls/` |
| Queue tool drafts | `python manage.py queue_tool_expansion --category pdf --limit 50` |
| Landing batch | `python manage.py generate_landing_batch --kinds tool,tutorial,… --limit 20` (draft) |
| AdSense ready | `GET /api/v1/monetization/adsense-ready/` |
| Checkout (Stripe or stub) | `POST /api/v1/billing/checkout-session/` |
| Campaigns | `/api/v1/admin/campaigns/`, `…/summary/`, `seed_campaigns` |
| Command Center extras | funnel, adsense_ready, deploy_release, open_campaigns, indexed_urls, draft specs |

**Never auto-publish:** expansion + landing batch create drafts only unless you pass `--publish` / approve in admin.

## Market Domination

Approve-gated growth: agents and autopilot **propose** changes; humans approve. Nothing auto-publishes to production without an explicit approve action.

| Feature | Endpoint / location |
|---------|---------------------|
| Growth actions | `GET /api/v1/admin/growth-agent/actions/`, `POST …/<id>/approve/`, `POST …/<id>/reject/` |
| SEO Autopilot | `POST /api/v1/admin/seo/autopilot/scan/`, `GET …/issues/`, `POST …/issues/<id>/apply\|dismiss/` |
| Ad recommendations | `GET/POST /api/v1/admin/revenue/ad-recommendations/`, accept/dismiss; `GET …/ad-performance/` |
| Competitors | `/api/v1/admin/competitors/domains/`, `…/opportunities/`, `POST …/recompute/` |
| Backlinks | `/api/v1/admin/backlinks/targets/`, `…/campaigns/`, `…/opportunities/`, `POST …/<id>/status/` |
| Programmatic batch | `python manage.py generate_programmatic_batch --type use_case\|industry\|comparison --limit 10` (draft by default) |
| Seed competitors | `python manage.py seed_competitors` |
| Generate SDK | `python manage.py generate_sdk` → `packages/api-client` |
| Mobile tools | `GET /api/v1/mobile/tools/?compact=1` — send `X-Client-Platform: ios\|android\|web` |
| Public pages | `/use-cases/[slug]`, `/industries/[slug]`, `/compare/[slug]` (API slugs `use/…`, `industry/…`, `compare/…`) |
| Admin UI | Admin tabs: Growth Agent (actions), SEO (autopilot issues), Revenue (ad recs), Competitors, Backlinks |
| TS SDK | Workspace package `@toolverse/api-client` — marketplace + mobile thin client |

### Approve gates (never auto-publish)

- Growth Agent **actions** stay `proposed` until `approve` (or `reject`).
- SEO Autopilot **issues** stay `open` until `apply` or `dismiss`.
- Content Autopilot runs require `approve` before publish.
- `generate_programmatic_batch` creates **draft** pages unless `--publish` is passed.
- Ad optimization recommendations require accept/dismiss — they do not mutate placements automatically.

### Commands

```bash
cd apps/api
set USE_SQLITE=true   # optional for local
python manage.py generate_programmatic_batch --type use_case --limit 12
python manage.py generate_programmatic_batch --type industry --limit 10
python manage.py generate_programmatic_batch --type comparison --limit 10
python manage.py seed_competitors
python manage.py generate_sdk
```

### Mobile header

Clients should send `X-Client-Platform` (e.g. `ios`, `android`, `web`, `extension`). The API logs it for analytics; `@toolverse/api-client` sets it automatically. Mobile and extension clients use dedicated throttle scopes (`mobile` / `extension`).

Monthly invoice stubs: Celery beat `generate-invoices-from-usage-monthly` → `ApiInvoiceStub` drafts from `ApiUsage`.

## Local development

### Prerequisites

- Node.js 20+
- Python 3.12+
- PostgreSQL 16 + Redis 7 (or Docker Compose)
- Optional: Docker Desktop for full stack

### 1. Environment

```bash
cp .env.example .env
cp apps/web/.env.example apps/web/.env.local
```

### 2. API (SQLite quick start)

```bash
cd apps/api
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# Unix:   source .venv/bin/activate
pip install -r requirements.txt
set USE_SQLITE=true   # Windows PowerShell: $env:USE_SQLITE="true"
python manage.py migrate
python manage.py seed_plans
python manage.py sync_tools
python manage.py runserver 8000
```

### 3. API (PostgreSQL + Redis)

Start Postgres/Redis, then omit `USE_SQLITE` and use values from `.env`.

Celery (separate terminals):

```bash
celery -A config.celery worker -l info
celery -A config.celery beat -l info
```

### 4. Web

```bash
# from repo root
npm install
npm run generate:tools --workspace=@toolverse/web
npm run dev --workspace=@toolverse/web
```

Open http://localhost:3000

### 5. Docker Compose (full stack)

```bash
cp .env.example .env
docker compose up --build
```

- Web: http://localhost:3000  
- API: http://localhost:8000  
- Nginx: http://localhost  
- Docs: http://localhost:8000/api/docs/

## Auth

- JWT access + refresh (`/api/v1/auth/register|login|refresh|logout|me/`)
- Roles: `user`, `admin`
- Premium via `Subscription` + `Plan` (`free` / `premium`)

## Key API routes

- `GET /api/v1/tools/` — list / search tools
- `GET /api/v1/tools/<slug>/related/` — recommendations
- `GET /api/v1/categories/`
- `GET /api/v1/sitemap/tools/`
- `GET/POST /api/v1/favorites/`
- `GET/POST /api/v1/history/`
- `GET /api/v1/subscriptions/plans/`
- `GET /api/v1/admin/metrics/` (admin)
- `GET/POST /api/v1/admin/tools/dynamic/` — Tool Builder
- `POST /api/v1/ai/complete/` — multi-provider AI
- `POST /api/v1/jobs/` — async jobs
- `GET/POST /api/v1/marketplace/keys/` — API marketplace
- `GET /api/v1/analytics/dashboard/` — admin analytics
- `GET /api/v1/analytics/growth/` — growth metrics (impressions, conversion, languages, sources)
- `GET /api/v1/programmatic/` — programmatic SEO pages
- `GET /api/v1/programmatic/by-path/?path=best/pdf-tools`
- `POST /api/v1/assistant/chat/` — tool recommendation assistant
- `/api/v1/engagement/` — saved outputs, collections, reviews, comments
- `/api/v1/admin/content/` — Content Factory (admin)
- `POST /api/v1/t/<tool-id>/...` — filesystem plugins
- `POST /api/v1/t/dynamic/<slug>/run/` — dynamic tools

## Testing & CI

```bash
# API
cd apps/api
pytest

# Web
npm run typecheck --workspace=@toolverse/web
npm run lint --workspace=@toolverse/web
npm run test --workspace=@toolverse/web
```

GitHub Actions runs lint/tests on push and PR (`.github/workflows/ci.yml`).

## Production notes

- Set `DEBUG=false`, strong `SECRET_KEY`, real Postgres/Redis
- Configure Cloudflare DNS + cache rules; point R2 env vars for uploads/OG assets
- Use `docker-compose.prod.yml`
- Optional: `SENTRY_DSN` / `NEXT_PUBLIC_SENTRY_DSN`
- AdSense: set `NEXT_PUBLIC_ADSENSE_ENABLED=true` and client ID (slots already reserved)

## Accessibility & SEO

- Skip link, landmarks, focus styles, RTL (`ar`)
- Dynamic sitemap, robots, JSON-LD, Open Graph (`/api/og`)
- Per-tool metadata from manifests

## Performance

- **API Redis cache** — tool list (60s) and detail (120s) via `apps.tools_registry.cache`; soft-fail if Redis is down
- **ORM** — `select_related` / `prefetch_related` on engagement and tools queries
- **`cache_page_safe`** — `apps.common.cache.cache_page_safe` for view-level caching that tolerates backend outages
- **Web** — `loading.tsx` skeletons (home + tool pages); `DynamicToolRuntime` loaded with `next/dynamic` (`ssr: false`)
- **Static assets** — `Cache-Control: public, max-age=31536000, immutable` for `/_next/static/*` in `next.config.ts`
- **CDN** — see `infra/cloudflare/README.md` for tool-page edge caching guidance

## Security

- **JWT** + API key auth (marketplace); Argon2 password hashing
- **AuditLog** — `apps.common.models.AuditLog` + `log_audit()` on marketplace key create/revoke, content publish, engagement moderate
- **Security headers** — `SecurityHeadersMiddleware` (CSP for JSON API, Referrer-Policy, X-Content-Type-Options)
- **Rate limits** — DRF throttles including scopes `auth`, `tool`, `ai`, `jobs`, `marketplace`, `assistant`
- **Uploads** — `apps.common.security.validate_upload(file, allowed_types, max_bytes)`
- **Abuse** — `BlockedIP` model + `BlockedIPMiddleware` (soft 403; never fails open into an outage)
- Nginx / Cloudflare WAF layer in production (see infra docs)

## License

Proprietary — ToolVerse AI
