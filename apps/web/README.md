# ToolVerse AI Web

Next.js 15 App Router frontend for ToolVerse AI.

## Setup

```bash
# from monorepo root
npm install
cp apps/web/.env.example apps/web/.env.local
npm run generate:tools --workspace=@toolverse/web
npm run dev --workspace=@toolverse/web
```

## Scripts

- `dev` — development server (Turbopack)
- `build` — generate tools registry + production build
- `start` — start production server
- `lint` — ESLint
- `typecheck` — TypeScript
- `generate:tools` — rebuild `src/tools/tools.generated.ts`
- `test` — Vitest
