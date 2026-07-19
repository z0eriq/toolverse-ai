# ToolVerse AI — Security Checklist

Use this checklist before every production deploy.

## Secrets & config

- [ ] `SECRET_KEY` is unique, random, 32+ characters (not a placeholder)
- [ ] `DEBUG=false` and `DJANGO_SETTINGS_MODULE=config.settings.production`
- [ ] `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` match the public domain
- [ ] Database and Redis credentials are not committed; `.env` is gitignored
- [ ] `API_KEY_PEPPER` differs from development
- [ ] `python manage.py validate_production` passes

## Transport & cookies

- [ ] HTTPS terminated (Cloudflare / Nginx) with HSTS enabled
- [ ] `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` true in production
- [ ] Security headers middleware / CSP reviewed (`SecurityHeadersMiddleware`)

## Auth & API

- [ ] JWT access/refresh lifetimes appropriate; refresh rotation enabled
- [ ] Rate limits / throttles enabled for auth, AI, and tool run endpoints
- [ ] Marketplace API keys hashed at rest; shown once on create
- [ ] Upload validation (`validate_upload`) rejects unexpected MIME/size

## Abuse & audit

- [ ] `BlockedIP` / audit log reviewed for false positives
- [ ] Admin role accounts use strong passwords / SSO where available
- [ ] Flower (Celery UI) is not publicly exposed without basic auth

## Observability

- [ ] `SENTRY_DSN` + `NEXT_PUBLIC_SENTRY_DSN` configured with correct environment/release
- [ ] `/readyz` returns 200 (database, cache, celery broker)
- [ ] Prometheus `/metrics` scraped privately (not public)

## Data

- [ ] `BACKUP_ENABLED=true` and backup restore drill documented
- [ ] R2 / object storage credentials scoped least-privilege

## Dependencies

- [ ] CI `pip-audit` / `npm audit` reviewed for high/critical findings
- [ ] Dependabot PRs triaged weekly
