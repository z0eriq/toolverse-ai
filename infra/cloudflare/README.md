# Cloudflare optimization checklist for ToolVerse AI
#
# DNS
# - Proxied (orange cloud) A/AAAA/CNAME to origin
# - Enable HTTP/2 + HTTP/3
#
# Caching
# - Cache Everything for /_next/static/* (long TTL; origin sends max-age=31536000, immutable)
# - Bypass cache for /api/* and authenticated HTML when needed
# - Respect Cache-Control from Next.js and Nginx
#
# Tool pages CDN
# - Tool HTML (`/{locale}/tools/{category}/{slug}`) is public SEO content — edge-cache
#   with a short TTL (e.g. 60–120s) + stale-while-revalidate, or Cache Everything +
#   origin Cache-Control / Cloudflare Cache Rules keyed on path
# - Bypass or lower TTL when `Cookie` / `Authorization` is present
# - Satellite pages (`…/faq`, `…/how-to`, etc.) can share the same rule as tool pages
# - API tool list/detail already Redis-cached at origin (60s list / 120s detail)
#
# Security
# - WAF managed rules + bot fight mode
# - TLS 1.2+ only; Always Use HTTPS
# - HSTS enabled at Cloudflare + origin
#
# R2
# - Create bucket `toolverse`
# - Set R2_* env vars on API
# - Public URL via custom domain or r2.dev
#
# Performance
# - Early Hints / Polish optional
# - Argo Smart Routing optional for API origin
