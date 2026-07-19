# Launch & revenue activation

Activation checklist for ToolVerse AI after deploy. **Nothing auto-publishes** — drafts stay drafts until an explicit approve/`--publish` action.

See also: [DEPLOYMENT.md](./DEPLOYMENT.md).

## 1. Deploy & migrate

```bash
# Production (compose migrate profile — not migrate-on-boot)
./infra/scripts/migrate.sh
./infra/scripts/deploy.sh
```

Confirm `/healthz`, `/readyz`, and `/metricsz`.

## 2. Analytics foundation

- Client UTM capture: `apps/web/src/lib/analytics.ts` stores `utm_*` + `campaign_key` in `sessionStorage` once per session.
- Track helpers: `trackToolComplete`, `trackPremiumIntent`, `trackRevenueEvent`.
- Admin funnel: `GET /api/v1/analytics/funnels/?days=30`
- Track accepts top-level UTM fields and copies from `properties` when missing.

## 3. SEO indexing

After GSC sync (Celery `sync_gsc_daily` or credentials present), `IndexedUrl` rows are upserted from page metrics.

```bash
# List / filter
GET /api/v1/admin/gsc/indexed-urls/?status=indexed&q=/tools/
```

## 4. First 1000 tools (drafts only)

Catalog: `apps/tool_factory/fixtures/expansion_catalog.json` — templates + slug patterns across `pdf`, `image`, `ai`, `calculators`, `developer`, `business` (≥250 structural slots; declared capacity 1000).

```bash
cd apps/api
python manage.py queue_tool_expansion --category pdf --limit 50
python manage.py queue_tool_expansion --summary
```

Creates **draft** `ToolSpec` rows only. Build/publish via Tool Factory admin after review.

### Expanding toward 1000

1. Queue more drafts per category (`--limit` up to 500).
2. Review UI schema / pipeline on each draft.
3. `POST /api/v1/admin/tool-factory/specs/<id>/build/` then publish only when approved.
4. Never run mass publish without human approval.

## 5. Landing pages (drafts only)

```bash
python manage.py generate_landing_batch \
  --kinds tool,tutorial,comparison,industry,use_case \
  --limit 20
# Optional publish (explicit):
# python manage.py generate_landing_batch --kinds tutorial --limit 5 --publish
```

## 6. Monetization

| Step | Action |
|------|--------|
| AdSense | Set `ADSENSE_CLIENT_ID=ca-pub-…`, run `seed_monetization`, check `GET /api/v1/monetization/adsense-ready/` |
| Stripe | Set `STRIPE_SECRET_KEY` + `STRIPE_PRICE_ID_PREMIUM`. Without secret, `POST /api/v1/billing/checkout-session/` returns `{url, status: "stub"}`. |
| Enterprise leads | `POST /api/v1/marketplace/leads/` accepts `company_size`, `intent`, UTM fields. |
| Pricing CTA | Wire UI to `trackPremiumIntent` + checkout session endpoint. |

## 7. Campaign Manager

```bash
python manage.py seed_campaigns
```

Admin API:

- `GET/POST /api/v1/admin/campaigns/`
- `GET /api/v1/admin/campaigns/summary/`
- `GET/POST /api/v1/admin/campaigns/results/`

Link events via `AnalyticsEvent.campaign_key` (same key as `MarketingCampaign.key`).

## 8. Founder Command Center

`GET /api/v1/admin/command-center/?days=30` includes:

- Funnel snapshot
- `adsense_ready`
- `deploy_release` (from `DEPLOY_RELEASE` / `SENTRY_RELEASE` / `GIT_SHA`)
- `open_campaigns`, `indexed_urls_count`, `draft_tool_specs_count`

Admin UI: Command Center tab.

## Approve gates (never auto-publish)

- Tool expansion → **draft** ToolSpecs
- Landing batch → **draft** ProgrammaticPages unless `--publish`
- Growth / SEO autopilot / content autopilot still require explicit approve
- Ad recommendations require accept/dismiss

## Env vars (new)

```
ADSENSE_CLIENT_ID=
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_PRICE_ID_PREMIUM=
STRIPE_SUCCESS_URL=
STRIPE_CANCEL_URL=
DEPLOY_RELEASE=
```
