# Postly Backend Setup Flow

## Prerequisite Check: Look for Existing Branches First

**CRITICAL:** Before creating any Postly API routes from scratch, always check if the code already exists in another branch. This session's first attempt created duplicate routes because the real Postly backend was sitting in `codex/postly-backend-supabase-pooler` unnoticed.

```bash
cd /opt/data/repos/agenticforceweb
git fetch origin
git branch -a | grep -i "postly\|backend\|codex"
git log --oneline origin/codex/postly-backend-supabase-pooler -5
```

## Merge Flow

```bash
cd /opt/data/repos/agenticforceweb

# 1. Check out the Postly branch
git checkout -b verify-postly origin/codex/postly-backend-supabase-pooler

# 2. Switch back to main
git checkout main

# 3. Merge (reverts of conflicting code first if needed)
git revert <your-duplicate-commit-hash> --no-edit  # if you created duplicate routes
git merge origin/codex/postly-backend-supabase-pooler --no-edit

# 4. Push
git push origin main
```

## Environment Variables

The Postly backend requires on Vercel:

| Variable | Value Source |
|---|---|
| `SUPABASE_DATABASE_URL` | Supabase project connection string (pooler) |
| `DATABASE_URL` | Same as SUPABASE_DATABASE_URL (fallback) |
| `HERMES_AGENT_SECRET` | Must match Hermes config.yaml `webhook.extra.secret` |
| `HERMES_BASE_URL` | `http://<VPS_IP>:8644` |
| `HERMES_WEBHOOK_URL` | `http://<VPS_IP>:8644/webhooks/website-signup` |

## Prisma Migrations

The branch includes 3 migrations. Apply after deploy:

```bash
npx prisma migrate deploy
```

List: `ls prisma/migrations/`

Expected:
- `202605310001_agenticforce_base_schema` — base tables
- `202606010001_postly_backend_foundation` — Postly models
- `202606010002_postly_admin_integrations` — admin UI support

## Seed Data

```bash
npx prisma db seed
```

Or via API (after deploy):
```bash
curl -X POST -H "x-hermes-secret: {SECRET}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "https://agenticforce.com/api/hermes/postly/seed"
```

## Verification

```bash
# Check response IS JSON (not HTML)
curl -s -H "x-hermes-secret: {SECRET}" \
  "https://agenticforce.com/api/hermes/postly/brands" | head -1
# Should return: {"brands":[...]} or {"error":"... (JSON, not HTML)}
```

## Domain Mapping

| What | Where |
|---|---|
| Vercel app | `www.postly.mn` → `agenticforceweb.vercel.app` |
| Static site | `agenticforce.com` (Hostinger, not Vercel) |
| Old Postly frontend | `postly.vercel.app` (unrelated Vue.js SPA) |

The user configures `AGENTICFORCE_BASE_URL=https://agenticforce.com`. Whether DNS forwards `/api/*` to Vercel depends on proxy rules. Check by inspecting response: JSON body = Vercel, HTML body (containing "Website Builder" or "hcdn") = Hostinger.
