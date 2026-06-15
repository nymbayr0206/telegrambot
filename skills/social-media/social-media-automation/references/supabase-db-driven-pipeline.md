# Supabase-Driven Social Content Pipeline

## Architecture Overview

```
Supabase DB (Postgres)
  └── content_schedule table
        ├── brand, post_date, topic, body_text
        ├── template_id, image_slot_prompts
        └── status: pending → generated → approved → published
              │
              ▼
        Cron job (daily check)
              │
              ├── Query WHERE status='pending' AND post_date=today
              ├── For each row:
              │     ├── Read brand → load brand assets
              │     ├── Generate poster via KIE.AI GPT Image 2
              │     └── Save to local workspace
              │
              ▼
        Telegram Preview → User reviews
              │
              ├── User says "Approve" / "Zuvshuurei"
              │     └── Send to webhook → publish
              │
              └── User says "Revise" / "Change X"
                    └── Re-generate, re-preview
```

## Supabase Connection

### Anon key vs Service Role key

| Key | Use | Risk |
|-----|-----|------|
| `anon` (public) | RLS-protected queries only | Low if RLS is configured |
| `service_role` | Full admin access | Any leak = full DB access |

For cron jobs: prefer the `anon` key with RLS policies that restrict the cron's IP, or use a `service_role` key stored in an env var (not in scripts).

### Connection from cron scripts

```bash
# Env vars (set in ~/.hermes/.env)
SUPABASE_URL="https://xxxxx.supabase.co"
SUPABASE_ANON_KEY="eyJ..."
```

Python query pattern:
```python
import os, json, urllib.request, ssl

ssl_ctx = ssl._create_unverified_context()
headers = {
    "apikey": os.environ["SUPABASE_ANON_KEY"],
    "Authorization": f"Bearer {os.environ['SUPABASE_ANON_KEY']}"
}

# Use REST API (Supabase's auto-generated REST endpoint)
url = f"{os.environ['SUPABASE_URL']}/rest/v1/content_schedule"
query = "status=eq.pending&post_date=eq.2026-06-02&order=post_time.asc"
req = urllib.request.Request(f"{url}?{query}", headers=headers)
resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=15)
rows = json.loads(resp.read().decode())

for row in rows:
    brand = row["brand"]
    topic = row["topic"]
    body = row["body_text"]
    # ... generate poster, save, update status
```

### Timezone handling

**CRITICAL:** For this user (Mongolia, UTC+8), compare `post_date` against the local date, not UTC:

```python
import datetime
# Get today's date in Mongolia timezone
mongolia_tz = datetime.timezone(datetime.timedelta(hours=8))
today = datetime.datetime.now(mongolia_tz).strftime("%Y-%m-%d")
# Query: post_date=eq.{today}
```

Or use PostgreSQL's `AT TIME ZONE` via a custom endpoint or raw SQL:
```sql
SELECT * FROM content_schedule 
WHERE post_date = CURRENT_DATE AT TIME ZONE 'Asia/Ulaanbaatar'
  AND status = 'pending';
```

## Suggested Supabase Table Schema

```sql
CREATE TABLE content_schedule (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand TEXT NOT NULL CHECK (brand IN ('ai-global', 'postly', 'supernova', 'custom')),
  post_date DATE NOT NULL,
  post_time TIME DEFAULT NULL,
  content_type TEXT DEFAULT 'carousel' CHECK (content_type IN ('carousel', 'single', 'story', 'video')),
  
  -- Content
  topic TEXT NOT NULL,              -- Short headline
  body_text TEXT,                    -- Mongolian copy / post caption
  image_slot_prompts JSONB,          -- Optional: per-slot KIE prompts (array of 4 strings)
  template_id TEXT DEFAULT 'default', -- Background template
  
  -- Status tracking
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'generating', 'generated', 'approved', 'published', 'failed')),
  kie_task_ids JSONB,               -- Array of KIE task IDs for tracking
  generated_assets JSONB,           -- {slide1: "/path/to/slide1.jpg", ...}
  
  -- Publishing
  webhook_payload_id TEXT,          -- ID returned by webhook
  published_at TIMESTAMPTZ,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Index for daily cron query
CREATE INDEX idx_content_schedule_daily 
  ON content_schedule (post_date, status);
```

## Status Lifecycle

```
pending ──→ generating ──→ generated ──→ approved ──→ published
   │                           │              │
   └──→ failed                 └──→ user      └──→ user says
                                says "revise"     "approve"
                                → back to
                                  pending
```

## Approval Flow (via Telegram)

After generation completes and assets are saved locally, send a preview:

> 🖼 **Шинэ пост бэлэн** — {brand}
> 📅 {post_date}
> 📝 {topic}
> 
> [MEDIA:/path/to/generated/slide-01.jpg]
> 
> ✅ Approve / 🔄 Revise / ❌ Cancel

User approves → run webhook POST, update status to 'published'.
User revises → update status back to 'pending', note the feedback.
User cancels → update status to 'cancelled' or delete the row.

## Multi-Brand Workspace Mapping

Each Supabase row's `brand` field maps to:
```
/opt/data/social-content/brands/<brand>/
  brand-guide.md
  assets/logos/
  assets/backgrounds/
  templates/
  generated/pending/<content_schedule_id>/
  scripts/
```

## Webhook Config

Store the webhook URL outside the DB (env var or local config file):
```bash
PUBLISH_WEBHOOK_URL="https://hook.us1.make.com/..."
```

On approval:
```bash
curl -s -X POST "$PUBLISH_WEBHOOK_URL" \
  -F "brand=$BRAND" \
  -F "topic=$TOPIC" \
  -F "post_date=$POST_DATE" \
  -F "body_text=$BODY_TEXT" \
  -F "slide1=@$SLIDE1" \
  -F "slide2=@$SLIDE2"
```

## Error Recovery

- If KIE generation fails → set status='failed', keep error in a `error_log` field
- If webhook returns non-200 → keep status='approved', retry on next tick (or manual retry)
- If Supabase is unreachable → skip the tick, log the error. Avoid repeated retries within short intervals
- If user doesn't approve for days → posts stay in 'generated' status. No auto-cleanup — preserve for manual review
