# Hermes ↔ Vercel ↔ Make.com Tri-directional Integration Pipeline

When the user has a **Postly-style content management system** running on Vercel (Next.js/Vue.js) and wants Hermes to act as middleware between Vercel (content DB) and Make.com (publishing), use this pattern.

## Architecture

```
Vercel (Postly backend API)
  ↕ GET/POST with x-hermes-secret header
Hermes (cron + Telegram approval)
  ↕ POST multipart webhook
Make.com (image generation + social publish)
  ↕ POST callback to Vercel/Hermes
```

## Direction

Two main directions:

### A. Hermes → Vercel (Hermes calls Vercel)
- Hermes cron polls Vercel API for planned content
- Hermes generates drafts, sends Telegram previews
- Hermes posts approval status back
- **Auth:** `x-hermes-secret` header with `HERMES_AGENT_SECRET`

### B. Vercel → Hermes (Vercel calls Hermes)
- Vercel webhooks send signups, leads, status updates
- **Auth:** `X-Hub-Signature-256` HMAC sha256 signature
- Or: `x-hermes-secret` header

## Endpoint Contract Template

When the user defines endpoint contracts, record them in a structured format:

```yaml
# Hermes → Vercel endpoints (POST with x-hermes-secret)
hermes_to_vercel:
  get_planned:
    method: GET
    url: "{VERCEL_BASE}/api/hermes/postly/planned"
    headers:
      x-hermes-secret: "{SECRET}"
    response: "{ planned_items: [...] }"
  
  post_draft:
    method: POST
    url: "{VERCEL_BASE}/api/hermes/postly/draft"
    headers:
      x-hermes-secret: "{SECRET}"
    body: "{ brand, draft_content, status }"
  
  post_approval_status:
    method: POST
    url: "{VERCEL_BASE}/api/hermes/postly/approval-status"
    headers:
      x-hermes-secret: "{SECRET}"
    body: "{ brand, item_id, approved, feedback }"

# Vercel → Hermes endpoints
vercel_to_hermes:
  lead_webhook:
    method: POST
    url: "{HERMES_BASE}/webhook/lead"
    headers:
      X-Hub-Signature-256: "sha256={HMAC(body, secret)}"
    
  make_callback:
    method: POST
    url: "{VERCEL_BASE}/api/webhooks/make/postly"
    # Called by Make.com after publishing

# Hermes → Make.com endpoint
hermes_to_make:
  publish:
    method: POST
    url: "{MAKE_WEBHOOK_URL}"
    content_type: multipart/form-data
    fields:
      - brand: "{brand}"
      - topic: "{topic}"
      - caption: "{text}"
      - slide1: "@{filepath}"
      - slide2: "@{filepath}"
      # ...
```

## Postly Brand API — Live (since June 2, 2026) [agenticforceweb repo]

The Postly backend lives in the **agenticforceweb** Vercel project (`github.com/aimongoliatushig-cloud/agenticforceweb.git`). The code originated from the `codex/postly-backend-supabase-pooler` branch (commit `6bb2677`) and was merged to `main`.

| Detail | Value |
|---|---|
| Vercel deployment URL | `https://agenticforceweb.vercel.app` (also `www.postly.mn` — same project) |
| User-configured base | `https://agenticforce.com` (⚠️ **NOT** Vercel — see domain table below) |
| API path | `/api/hermes/postly/*` (Hermes-facing) and `/api/postly/*` (admin CRUD) |
| Auth header | `x-hermes-secret: <HERMES_AGENT_SECRET>` |
| Secret source | Vercel env `HERMES_AGENT_SECRET` (= Hermes config `webhook.extra.secret`) |
| DB env var | `SUPABASE_DATABASE_URL` (Supabase pooler) / `DATABASE_URL` (fallback) |
| Seed script | `prisma/seed-postly.mjs` (run via `npm run seed:postly`) |
| Admin UI | `/admin/postly/integrations` (Clerk-protected) |
| Make callback | `POST /api/webhooks/make/postly` (receives Make.com publishing results) |

### ⚠️ CRITICAL: agenticforce.com is NOT Vercel

`agenticforce.com` is a **Hostinger Website Builder** static site. Calling `/api/hermes/postly/*` against it returns Hostinger's 404 page (`"Website Builder 404"`), not a Vercel JSON response. The actual Vercel deployment is at `agenticforceweb.vercel.app` and `www.postly.mn`.

Always verify which domain hosts the real API by checking the response body:
- Vercel API returns JSON (or Next.js HTML 404 page with header/footer)
- Hostinger returns `"Website Builder 404"` with `x-powered-by: HostingerWebsiteBuilder`

The user may configure `AGENTICFORCE_BASE_URL=https://agenticforce.com` (expecting DNS proxying), but this session confirmed it does NOT proxy to Vercel. Use `agenticforceweb.vercel.app` for direct API access.

### Deployment Verification

First, find the actual Vercel deployment URL — do NOT assume the custom domain works:

```bash
# Step 1: Identify the actual Vercel deployment
echo "=== Check custom domain ==="
curl -sI "https://agenticforce.com" | grep -i "x-powered-by\|platform\|server"
# If this shows "HostingerWebsiteBuilder" → the domain is NOT Vercel

echo "=== Check Vercel preview domain ==="
curl -sI "https://agenticforceweb.vercel.app" | grep -i "x-powered-by\|server"
# If this shows "vercel" → this is the real deployment

# Step 2: Test the API (use actual Vercel domain)
response=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "x-hermes-secret: {SECRET}" \
  "https://agenticforceweb.vercel.app/api/hermes/postly/brands")

if [ "$response" = "401" ]; then
  echo "Postly backend IS deployed — secret is wrong (401 is correct auth response)"
elif [ "$response" = "200" ]; then
  echo "Postly backend IS deployed and authenticated"
elif [ "$response" = "404" ]; then
  echo "Postly backend NOT deployed yet (Vercel hasn't rebuilt)"
  echo "Check: git log -1 @{push} — did the push go through?"
else
  echo "Unexpected: $response — may be Hostinger, not Vercel"
fi
```

### Prisma Models (actual backend — NOT simplified JSON-column models)

The real Postly backend uses relational tables, not JSON blobs:

- **`CompanyProfile`** — the brand/company (one per brand). Fields: `companyName`, `businessType`, `activityDirection`, `email`
- **`BrandGuideline`** — one-to-one with CompanyProfile. Fields: `toneOfVoice`, `brandColors` (String[]), `fonts` (String[]), `language`, `tagline`
- **`BrandTemplate`** — reusable visual templates. Fields: `name`, `type` (CAROUSEL/POSTER/REEL), `config` (Json)
- **`ProductService`** — products/plans. Fields: `name`, `description`, `price`, `benefits` (String[]), `status`
- **`ContentPlan`** — monthly schedule. Fields: `month` (String like "2026-06"), `status`, `strategyNote`, `totalCarousels`, `totalReels`, `totalPosts`
- **`ContentItem`** — individual post. Fields: `contentType` (CAROUSEL/POSTER/REEL), `category`, `title`, `caption`, `headline`, `imagePrompt`, `creativeDirection`, `status` (PLANNED/WAITING_APPROVAL/APPROVED/SENT_TO_MAKE/POSTED/REJECTED), `scheduledAt`, `agentName`, `telegramMessageId`, `revisionNote`
- **`ContentAsset`** — generated media files. Fields: `source` (MAKE/HERMES), `assetType` (IMAGE/VIDEO), `fileUrl`, `status`
- **`ApprovalRequest`** — approval round. Fields: `status` (APPROVED/REJECTED/REVISION), `reviewer`, `note`, `source` (TELEGRAM/ADMIN)
- **`PostingJob`** — publish attempt. Fields: `platform`, `status`, `makeWebhookResponse` (Json)
- **`PostingLog`** — publish audit trail. Fields: `platform`, `status`, `response` (Json)
- **`SocialAccount`** — linked platform. Fields: `platform`, `accountId`, `status`
- **`MakeIntegration`** — Make.com config per brand. Fields: `webhookUrl`, `scenarioName`, `status`
- **`PostlyAgentLog`** — Hermes audit log. Fields: `agentName`, `action`, `status`, `message`, `rawPayload` (Json)

### Hermes-Facing API Reference

All endpoints require `x-hermes-secret: <HERMES_AGENT_SECRET>` header.

#### GET /api/hermes/postly/brands?q=\<name\>

Search/fetch brands with full context. Response uses snake_case keys from the Prisma models.

```bash
curl -s -H "x-hermes-secret: {SECRET}" \
  "https://agenticforce.com/api/hermes/postly/brands?q=Postly"
```

**Response shape:**
```json
{
  "brands": [{
    "company_id": "clx...",
    "brand_name": "Postly",
    "business_type": "AI Content Marketing",
    "activity_direction": "B2B",
    "email": "admin@postly.mn",
    "brand_guideline": { "toneOfVoice": "...", "brandColors": [...], "fonts": [...], ... },
    "products": [{ "name": "Starter Plan", "price": "390,000₮/сар", ... }],
    "templates": [{ "name": "Default Carousel", "type": "CAROUSEL", ... }],
    "content_plans": [{
      "id": "clx...",
      "month": "2026-06",
      "status": "active",
      "content_items": [{ "id": "clx...", "contentType": "POSTER", "status": "PLANNED", ... }]
    }],
    "content_counts": { "total": 5, "planned": 5, "approved": 0, "posted": 0 },
    "make_integration": { "webhookUrl": null, "scenarioName": "...", "status": "configured" },
    "social_accounts": [{ "platform": "Facebook", "status": "active" }]
  }]
}
```

#### GET /api/hermes/postly/planned

Fetch all items with status `PLANNED`, each with brand + plan context.

**Response:** `{ "items": [{ ...ContentItem with nested company, contentPlan, template ... }], "templates": [...] }`

Response key is `"items"` (NOT `"planned"`). Each item has nested `company` (with brandGuideline, productsServicesPostly, socialAccounts), `contentPlan`, and `template` (nullable).

#### POST /api/hermes/postly/draft

Save a Hermes-generated draft. Updates the existing ContentItem record.

```bash
curl -s -X POST \
  -H "x-hermes-secret: {SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "contentItemId": "clx...",
    "title": "Post title",
    "headline": "Attention headline",
    "caption": "Full caption in Mongolian",
    "imagePrompt": "English image generation prompt",
    "creativeDirection": "Visual direction notes",
    "status": "WAITING_APPROVAL",
    "agentName": "Hermes"
  }' \
  "https://agenticforce.com/api/hermes/postly/draft"
```

#### POST /api/hermes/postly/approval-status

Record Telegram approval/rejection. Appends to approval history.

```json
{
  "contentItemId": "clx...",
  "telegramChatId": "optional",
  "telegramMessageId": "optional",
  "status": "APPROVED | REJECTED | REVISION",
  "revisionNote": "optional"
}
```

#### GET /api/hermes/postly/approved

Fetch items with status `APPROVED`, ready for Make.com publishing.

**Response:** `{ "items": [...], "makePayloads": [...] }`

Response keys are `"items"` and `"makePayloads"` (NOT `"approved"`).

#### POST /api/hermes/postly/sent-to-make

Record Make.com handoff and update status to `SENT_TO_MAKE`.

```json
{
  "contentItemId": "clx...",
  "makeWebhookResponse": {},
  "status": "SENT_TO_MAKE"
}
```

#### POST /api/hermes/postly/logs

Log operational events. Creates a `PostlyAgentLog` record.

```json
{
  "event": "fetch_planned",
  "brandId": "optional",
  "itemId": "optional",
  "status": "success | error",
  "message": "Processed 5 planned items from Postly",
  "metadata": {}
}
```

#### GET /api/hermes/postly/db-health

Health check that verifies DB connectivity (admin use).

**Response:** `{ ok: true, dbConnected: true, ... }`

### Content Item Status Flow

```
PLANNED → WAITING_APPROVAL → APPROVED → SENT_TO_MAKE → POSTED
               ↓
           REJECTED
```

### Setting Up the Pipeline

#### Step 1: Merge the Postly branch into main

The Postly backend code lives in branch `codex/postly-backend-supabase-pooler`. Do NOT create routes from scratch — merge this branch:

```bash
cd /opt/data/repos/agenticforceweb
git fetch origin
git checkout main
git merge origin/codex/postly-backend-supabase-pooler --no-edit
git push origin main
```

#### Step 2: Apply Prisma migrations

Once deployed, Vercel's `postinstall` hook runs `prisma generate`. The migrations must be applied manually or via Vercel deploy hook:

```
npx prisma migrate deploy
```

Migrations present:
- `202605310001_agenticforce_base_schema` — base tables (User, Article, etc.)
- `202606010001_postly_backend_foundation` — CompanyProfile + all Postly models
- `202606010002_postly_admin_integrations` — admin integrations UI support

#### Step 3: Set Vercel environment variables

```
SUPABASE_DATABASE_URL=postgresql://...@.../postgres?sslmode=require
DATABASE_URL=postgresql://...@.../postgres?sslmode=require
HERMES_AGENT_SECRET=<same as Hermes config.yaml webhook.extra.secret>
HERMES_BASE_URL=http://72.62.197.97:8644
HERMES_WEBHOOK_URL=http://72.62.197.97:8644/webhooks/website-signup
```

#### Step 4: Set Hermes environment

In `/opt/data/.env` (or passed to cron job):

```
AGENTICFORCE_BASE_URL=https://agenticforce.com
HERMES_AGENT_SECRET=<same secret>
```

#### Step 5: Seed test data (one-time)

```bash
cd /opt/data/repos/agenticforceweb
npx prisma db seed
# OR via API:
curl -X POST -H "x-hermes-secret: {SECRET}" \
  "https://agenticforce.com/api/hermes/postly/seed" \
  -H "Content-Type: application/json" \
  -d '{"brandName":"Postly"}'
```

The seed script (`prisma/seed-postly.mjs`) creates a Postly brand with 3 products, 5 planned content items, and June 2026 content plan.

#### Step 6: Create Hermes cron job

LLM-driven (not script-only — needs reasoning for content generation):

```python
cronjob(
  action="create",
  name="Postly content pipeline",
  schedule="every 5 min",
  deliver="local",
  skills=["social-media-automation"],
  enabled_toolsets=["terminal", "web"],
  prompt="""Fetch planned items from AgenticForce API →
            generate title/headline/caption/imagePrompt/creativeDirection in Mongolian →
            save draft as WAITING_APPROVAL →
            log operation""",
)
```

#### Step 7: Telegram approval flow

When user approves/rejects in Telegram:
1. POST `/api/hermes/postly/approval-status` with status + item ID
2. If APPROVED → ready for Make.com publishing
3. If REJECTED/REVISION → can re-generate

### Domain Architecture Summary

| Domain | Platform | Hosts |
|---|---|---|
| `agenticforce.com` | Hostinger Website Builder | Static marketing site (frontend only) |
| `www.postly.mn` | **Vercel** (agenticforceweb) | Next.js app + Postly API routes |
| `postly.vercel.app` | Vercel (separate) | Vue.js SPA frontend (unrelated) |
| `agenticforceweb.vercel.app` | Vercel | Same app as www.postly.mn, auto-deployed from GitHub |

**Important:** `agenticforce.com` returns Hostinger-branded 404s for API routes. The actual Postly API serves from `www.postly.mn` (the Vercel project). The user configures `AGENTICFORCE_BASE_URL=https://agenticforce.com` but the true backend is on the Vercel project. If the user has DNS proxy rules, they may forward `/api/*` to Vercel — verify by checking the response body (JSON = Vercel, HTML = Hostinger).

## Checking Brand Data: API First, Not Local Files

**CRITICAL RULE:** When the user asks about brand content, planned items, or brand profiles, **do NOT search local files first**. Query the Postly backend API directly:

```bash
curl -s -H "x-hermes-secret: {SECRET}" \
  "https://agenticforce.com/api/hermes/postly/brands?q={brand_name}"
```

Only fall back to local file search if:
1. The API returns 404 (endpoint doesn't exist yet or Vercel hasn't rebuilt)
2. The API explicitly says no data found
3. The user confirms they haven't deployed the backend

**Why:** The user treats the Postly API as the source of truth for brand/content data. Local files are workspace caches, not authoritative. Searching locally first was explicitly corrected.

## Pitfalls

- **x-hermes-secret must match exactly** between Hermes and Vercel — a mismatch gives 401
- **Vercel deploys from GitHub** — pushing to main auto-deploys but takes 1-5 minutes. Check `git log -1 @{push}` to confirm the push was accepted. A 404 in the first minute after push is normal.
- **DO NOT create Postly routes from scratch** — they already exist in the `codex/postly-backend-supabase-pooler` branch. Merge that branch instead.
- **DB env var name changed** — the branch uses `SUPABASE_DATABASE_URL` (not `DATABASE_URL`). Both must be set on Vercel.
- **Vercel SPA apps catch all routes with 200 HTML** — don't confuse "HTTP 200" with "endpoint exists"; inspect the response body
- **Make.com webhook expects multipart/form-data** — use `-F` flags, never `-H "Content-Type: multipart..."` (breaks boundary parsing)
- **Cron runs in UTC** — use `Asia/Ulaanbaatar` for date comparisons when querying "today's content"
- **Domain-to-Vercel-project mapping can change** — always verify by checking the response body before trusting API results. Vercel 404 pages include header/footer HTML; Hostinger 404 pages say "Website Builder 404".
- **Never assume a custom domain points to Vercel** — `agenticforce.com` resolved to Hostinger Website Builder, not the Vercel app. Always verify with `curl -sI <url>` and check `x-powered-by` or server headers.
- **Before writing API integration code, check existing branches first** — the Postly backend already existed in `codex/postly-backend-supabase-pooler`. Creating duplicate routes from scratch wastes time and requires reverting.
- **API response keys may not match your assumptions** — the `/planned` endpoint returns `{ "items": [...] }` not `{ "planned": [...] }`. Always check the actual response shape first by making a test call.
- **Do not print shared secrets in logs or response output** — use `x-hermes-secret` header value but never echo it in terminal output, error messages, or delivery content.
