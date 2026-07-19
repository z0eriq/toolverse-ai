## مسار Vercel (الواجهة مجاناً)

الواجهة منشورة على: https://toolverse-web-three.vercel.app  
الدومين مربوط في المشروع — أضف في Cloudflare:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | `@` | `76.76.21.21` | DNS only |
| A | `www` | `76.76.21.21` | DNS only |

التفاصيل: [docs/VERCEL.md](../docs/VERCEL.md)

---

# ربط tool-verse.online على Cloudflare

المستودع على GitHub: https://github.com/z0eriq/toolverse-ai

ToolVerse يحتاج **أصل (Origin)** يشغّل Docker Compose (API + Web + Postgres + Redis). Cloudflare يدير DNS/CDN/WAF أمام هذا الأصل.

## 1. أضف الدومين إلى Cloudflare

1. [Cloudflare Dashboard](https://dash.cloudflare.com) → **Add a site** → `tool-verse.online`
2. اختر خطة Free على الأقل
3. غيّر Nameservers عند المسجّل إلى ما يعطيك Cloudflare (مثل `*.ns.cloudflare.com`)
4. انتظر Active

## 2. سجّلات DNS (بعد تشغيل السيرفر)

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | `@` | `<IP السيرفر>` | Proxied (برتقالي) |
| A | `www` | `<IP السيرفر>` | Proxied |
| A | `api` | `<IP السيرفر>` | Proxied (اختياري subdomain للـ API) |

أو CNAME إلى hostname السيرفر إن وُجد.

## 3. SSL/TLS في Cloudflare

- **SSL/TLS** → mode: **Full (strict)** بعد تثبيت شهادة على Nginx/Let's Encrypt
- Always Use HTTPS: On
- Minimum TLS: 1.2

## 4. نشر التطبيق على VPS

```bash
git clone https://github.com/z0eriq/toolverse-ai.git
cd toolverse-ai
cp .env.example .env
# عدّل SECRET_KEY, POSTGRES_*, ALLOWED_HOSTS=tool-verse.online,www.tool-verse.online
# NEXT_PUBLIC_APP_URL=https://tool-verse.online
# NEXT_PUBLIC_API_URL=https://tool-verse.online/api/v1
chmod +x infra/scripts/*.sh
./infra/scripts/migrate.sh
./infra/scripts/deploy.sh
```

افتح المنافذ 80/443 على السيرفر. Nginx في `docker-compose.prod.yml` يستقبل الحركة خلف Cloudflare.

## 5. Cache Rules (موصى به)

- Cache `/_next/static/*` بقوة (TTL طويل)
- Bypass `/api/*`
- HTML للصفحات العامة: TTL قصير 60–120s

راجع أيضاً `infra/cloudflare/README.md`.
