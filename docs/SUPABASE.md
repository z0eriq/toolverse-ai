# Supabase setup — ToolVerse AI

Project URL (web env): `https://kxtcxncucwvbepmqkcgf.supabase.co`

## What’s already done in code

- Packages: `@supabase/supabase-js`, `@supabase/ssr`
- Clients: `apps/web/src/utils/supabase/{client,server,middleware}.ts`
- Auth: login / register / logout use **Supabase Auth** (session cookies)
- Callback: `/auth/callback` (email confirm / OAuth PKCE)
- Middleware: refreshes session + redirects unauthenticated users away from
  `dashboard`, `favorites`, `history`, `workspace`, `workflows`, `creator`, `admin`
- SQL migration file: `supabase/migrations/20260720120000_toolverse_profiles.sql`
- Vercel env: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`

Django JWT remains in the codebase for API calls later; the **web session** is Supabase.

---

## Steps you must do in the Supabase Dashboard

### 1) Confirm you are on the correct project

Open [Supabase Dashboard](https://supabase.com/dashboard) → project **`kxtcxncucwvbepmqkcgf`**.

> Note: Cursor’s Supabase MCP may be linked to a *different* project. Do not run ToolVerse SQL there.

### 2) Run the database migration

1. SQL Editor → New query  
2. Paste the full contents of  
   `supabase/migrations/20260720120000_toolverse_profiles.sql`  
3. Run  
4. Table Editor should show `profiles` and `usage_monthly` with RLS on

### 3) Configure Auth URLs

Authentication → URL Configuration:

| Setting | Value |
|--------|--------|
| Site URL | `https://tool-verse.online` |
| Redirect URLs | `https://tool-verse.online/auth/callback` |
| | `http://localhost:3000/auth/callback` |

### 4) Email confirmation (recommended for production)

Authentication → Providers → Email:

- Keep **Confirm email** enabled for production, **or** disable temporarily for local testing only.
- With confirmation on: after register, user sees “check your email”, then lands on `/auth/callback`.

### 5) (Optional) Google / GitHub OAuth

Providers → enable → add Client ID/Secret → add same redirect URLs as above.  
UI buttons can be added later; callback route is already ready.

### 6) Redeploy web (after env + migration)

Vercel already has the env vars. Redeploy `toolverse-web` so production uses the latest auth code.

---

## Local verify

```bash
cd apps/web
npm run dev
```

1. Open `/en/auth/register` → create account  
2. Confirm email (if enabled) → should reach dashboard  
3. Sign out / sign in  
4. Visit `/en/dashboard` while logged out → redirect to login  

---

## Later (not blocking launch of auth)

1. Re-link Cursor Supabase MCP to project `kxtcxncucwvbepmqkcgf`  
2. Bridge Django API to accept Supabase JWT (when API is deployed)  
3. Sync `profiles.role` / premium with billing  
4. Never put `service_role` in `NEXT_PUBLIC_*`
