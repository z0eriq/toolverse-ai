# نشر ToolVerse على Vercel (+ Cloudflare DNS)

Vercel يستضيف **واجهة Next.js** (`apps/web`) مجاناً على الخطة Hobby.

> الـ API (Django + Postgres + Redis + Celery) **لا يعمل على Vercel**.  
> الموقع يعمل كواجهة؛ الأدوات/تسجيل الدخول تحتاج API لاحقاً (Railway / Render / VPS).

## 1) نشر من المستودع

المستودع: https://github.com/z0eriq/toolverse-ai

**Production URL (جاهز):** https://toolverse-web-three.vercel.app

المشروع على Vercel: `toolverse-web` (Root: `apps/web`)

أو من الجهاز (CLI):

```bash
cd apps/web
npx vercel --prod
```

## 2) ربط الدومين `tool-verse.online`

### في Vercel
Project → **Settings → Domains** → أضف:
- `tool-verse.online`
- `www.tool-verse.online`

انسخ القيمة التي يطلبها Vercel (غالباً `cname.vercel-dns.com` أو A `76.76.21.21`).

### في Cloudflare (DNS)
بعد أن يصبح الدومين **Active** على Cloudflare، أضف (لا تحوّل Nameservers إلى Vercel — ابقَ على Cloudflare):

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | `@` | `76.76.21.21` | **DNS only** (رمادي) أولاً |
| CNAME | `www` | `cname.vercel-dns.com` | DNS only |

احذف أي A/CNAME قديمة تتعارض.

بعد نجاح الشهادة في Vercel يمكن تجربة Proxied (برتقالي)؛ إن فشلت SSL اترك **DNS only**.

SSL في Cloudflare: **Full**.


## 3) التحقق

- افتح `https://tool-verse.online`
- Vercel Dashboard → Deployments → Ready

## 4) الـ API لاحقاً (مجاني/رخيص)

خيارات شائعة لـ Django:
- Railway / Render (Hobby)
- Oracle Cloud Always Free VPS + Docker

ثم حدّث `NEXT_PUBLIC_API_URL` في Vercel وأعد النشر.
