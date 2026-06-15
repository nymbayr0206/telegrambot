---
name: social-media-automation
description: "Approval-first social media content automation: brand guide, content calendar, AI image/video assets, Telegram previews, and publishing/scheduling only after explicit approval."
version: 2.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [social-media, content-calendar, approval-workflow, image-generation, video-generation, publishing]
---

# Social Media Automation

For cron-based daily carousel automation (two architectures: LLM-driven + shell script, or script-only Python + KIE API), see `references/cron-carousel-autopost.md`.

## Brand Onboarding Workflow

Use this section when setting up a new brand in the system for the first time — creating the directory structure, saving the logo, registering in the brand registry, collecting info, and seeding templates.

### 1. Create Directory Structure

Base path: `/opt/data/social-content/brands/<slug>/`

```bash
mkdir -p /opt/data/social-content/brands/<slug>/{assets/logos,templates,source-materials,scripts,references,output}/
```

Standard slug: lowercase, no spaces, Mongolian cyrillic → latin (ирээдүймэд → ireeduimed).

### 2. Save Logo

When user sends an image saying "logo" or "save it as logo":

```bash
cp /path/to/source /opt/data/social-content/brands/<slug>/assets/logos/logo-<slug>.<ext>
```

Save in both .jpg and .png (the .png is actually a JPEG copy for flexibility — note this in a comment).

**⚠️ Telegram renames uploaded files** to auto-generated names like `img_<hash>.jpg`. Do NOT tell the user "you named them X" — explain Telegram's renaming and ask them to describe each image.

### 3. Register in Brand Registry

File: `/opt/data/social-content/brands/brand-registry.json`

```json
{
  "name": "Брэнд Нэр",
  "slug": "brand-slug",
  "workspace": "/opt/data/social-content/brands/brand-slug",
  "default_language": "mn",
  "approval_required": true,
  "created_at": "2026-06-05"
}
```

Add via Python:

```python
import json
with open('/opt/data/social-content/brands/brand-registry.json', 'r') as f:
    registry = json.load(f)
registry[slug] = { ... }
with open('...', 'w') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)
    f.write('\n')
```

### 4. Collect Remaining Info

After logo + registration, prompt for:
- **Contact phone**
- **Address**
- **Brand description** — what does this brand do? (products, services, niche)
- **Content types needed** — social poster, news poster, carousel, etc.
- **Knowledge base** — any reference materials, source docs

Store info as memory and optionally as a text file in `brand-guide.md`.

### 5. Template Setup (if user provides a design template)

```bash
mkdir -p /opt/data/social-content/brands/<slug>/templates/<template-name>/
cp /path/to/reference-image /opt/data/social-content/brands/<slug>/templates/<template-name>/<template-name>-reference.jpg
```

#### 5a. Document Fixed vs Dynamic Elements

Create `templates/<template-name>/template-spec.md`:

- **🔒 FIXED (ABSOLUTELY NEVER change):** Logo, background, layout structure, contact info, brand name.
- **✅ DYNAMIC (only these can change):** HEADLINE, BODY CONTENT, ILLUSTRATION.

#### 5b. Upload to Hosting Service for KIE

Templates used with KIE image-to-image need public URLs:

```bash
# Upload to catbox.moe (72h expiry)
curl -s -F "reqtype=fileupload" -F "time=72h" \
  -F "fileToUpload=@<template-path>.jpg" \
  https://litterbox.catbox.moe/resources/internals/api.php
# Returns: https://litter.catbox.moe/xxxxxx.jpg
```

Save the URL in template-spec.md and in a knowledge base README.

#### 5c. Create Knowledge Base Entry

```bash
mkdir -p /opt/data/knowledge_bases/<brand>-<template>/
```

Create `README.md` with template metadata, fixed vs dynamic breakdown, online URLs, brand info, and trigger phrases.

#### 5d. KIE Generation Rule for Fixed Templates

When generating with a template reference via `gpt-image-2-image-to-image`, the model frequently treats the reference as "style inspiration" and redesigns the logo and layout. Use this proven prompt structure:

```
CRITICAL - TEMPLATE PRESERVATION:
The FIRST image is the TEMPLATE. It has a FIXED layout that MUST be preserved EXACTLY:
- [Logo]: DO NOT change, move, or regenerate
- [Branding bar/background]: DO NOT change
- [Footer/contact]: DO NOT change
- The overall layout MUST remain identical to the template

ONLY change these [N] things from the template:
1. [First dynamic element]
2. [Second dynamic element]
```

## Reference Files

- `references/brand-asset-onboarding.md` — workflow for receiving client brand assets (logos, references, backgrounds) when a client sends image files. Covers naming conventions (descriptive filenames for recall), fallback when vision is unavailable, duplicate detection via MD5, subdirectory organization, and brand-guide.md updates.
- `references/ocr-text-extraction.md` — OCR text extraction from client images (flyers, posters, business cards) using the free OCR.space API when no local OCR libraries are available. Covers Python stdlib approach, Mongolian Cyrillic handling, common OCR errors to correct, and fallback strategies.
- `references/approval-first-social-publishing.md` — reusable pending-approval pattern for generated social assets before Make.com/Facebook/Instagram/webhook publishing; includes Supernova daily carousel rule.
- `references/openai-vision-image-review.md` (in kie-content-maker skill) — OpenAI GPT-4o vision review for carousel image QA. Integrate after asset compositing and before user delivery.
- `references/client-telegram-approval-workflow.md` — when the user's own clients (not the user themselves) need to review and approve content via the shared Telegram bot. Covers client registration (Telegram @username → brand mapping), sending previews to client chats, recognising client approval/rejection responses, and notifying the user.
- `references/supernova-carousel-brand-guidelines.md` — Supernova-specific carousel visual rules: 1:1 1080x1080, GPT Image 2 preferred, logo/phone placements, red/blue typography, Mongolian QA notes, Telomer Effect ebook campaign.
- `references/make-carousel-autopost-webhook.md` — reusable multipart Make.com webhook payload pattern for sending 4 carousel images plus metadata, with state advancement and UTC scheduling notes.
- `references/postly-backend-setup-flow.md` — step-by-step Postly backend setup: branch merge, Prisma migrations, env vars, domain mapping, and verification. **Always check if the Postly backend code exists in a branch before creating routes from scratch.**
- `references/ffmpeg-veo-video-merge.md` — merge Veo 3.1 Fast multi-scene MP4 clips into one continuous Reel using FFmpeg (concat, crossfade transitions, ASS subtitle burn-in with custom fonts and glow effects, word-by-word caption syncing).
- `references/deployment-platform-identification.md` — diagnostic technique for distinguishing Vercel, Hostinger, and Vue.js SPA deployments by response body fingerprint. Essential when a domain resolves but API routes return 404.
- `references/book-to-social-series.md` — workflow for turning books/PDFs into approval-first social content series.
- `references/supernova-healthcare-carousel.md` — Supernova-specific healthcare carousel layout, logo/font/color rules, ebook-to-carousel planning.
- `references/ai-global-brand-guidelines.md` — AI Global brand-specific carousel layout rules: top-left content type labels (Боловсрол, Салбарын мэдээ, Сургалт, Амжилтын түүх), top-right logo anchor, bottom-left contact line (phone + website), no slide counter rule, Manrope font, black/gold/white color scheme, 4-slide carousel structure (hook → explain → deepen → CTA), full June 2026 posting calendar with 7 carousels + 4 reels.
- `references/cron-carousel-autopost.md` — complete cron-job orchestration pattern: state file, webhook config, script path constraints, LLM-driven (no_agent=false) and script-only (no_agent=true) patterns, KIE.AI direct API usage, error recovery, Supernova 18-carousel example, and the two-stage brand overlay approach.
- `references/supernova-two-stage-carousel-overlay.md` (in kie-content-maker skill) — brand carousel two-stage with Pillow compositing.
- `templates/supernova-carousel-overlay-v3.py` — Pillow compositing template for two-stage carousel generation (background from KIE + local overlay of brand logo, hex colors, Mongolian text, phone capsule, ribbons). CLI usage: --background, --logo, --slide, --title, --subtitle, --phone, --tagline, --output.

Use this skill when the user wants Hermes to act as a social media manager, create posts/scripts/captions, generate image or video assets through APIs, store drafts, preview content, or publish/schedule to social platforms.

## Core rule: approval-first publishing

Never publish, schedule, or send a social post to an external account unless the user has explicitly approved the exact content and target platform/time.

Valid approval examples:
- "Approved, post it"
- "Zuvshuurluu, postlo"
- "Schedule this for tomorrow 10:00"

If the approval is ambiguous, ask for confirmation. Drafting, generating media, saving files, and sending previews are allowed without publishing approval.

**Exception — pre-approved cron series:** When the user has agreed to a multi-part series (e.g. 18 Supernova carousels) and cron is configured to auto-publish daily, the approval-first rule is relaxed for the cron job itself. The user approved the series plan; the cron just executes it.

### Client approval via Telegram

When the user says "my client wants to review content" or introduces a client by Telegram @username, use `references/client-telegram-approval-workflow.md`. The pattern:

1. User introduces client → register Telegram @username → brand mapping in memory
2. Generate content as usual, save under the brand's workspace
3. Send preview to the client via `send_message(target="telegram:<chat_id>", ...)` with slides and approval prompt
4. Client responds "Approve" / "Revise" / "Cancel" via the bot
5. On approve → publish (Make.com webhook) and notify the user. On revise → ask for specifics, redo, re-preview. On cancel → archive and notify user.

**Authorizing a new client/communicator:**

New users (clients, team members) cannot message the bot until authorized. Two methods:

**Method A — `allowed_chats: ''` (open to all):** Set `telegram.allowed_chats: ''` in config.yaml. Any Telegram user can message the bot and trigger a pairing code. This is the simplest setup for client-facing bots.

**Method B — Pairing code (default):** The user tells the new person to message the bot (`@Sara01_bot`). The bot responds with a 8-character pairing code (e.g. `39RV62JH`). The user shares that code with the operator (you), who approves it:

```bash
/opt/hermes/.venv/bin/hermes pairing approve telegram <CODE>
```

Output: `Approved! User @username (USER_ID) on telegram can now use the bot~`

The pairing code approach is preferred when the user wants explicit invite-based control. Only users who have been sent a pairing code by the bot and had it approved can interact.

The bot's `allowed_chats` must be empty (all chats allowed) in config.yaml for new clients to reach the agent via Method A. For Method B, the default allowlist settings work — the pairing process bypasses the allowlist.

## Standard workflow

1. **Brand guide** — establish durable facts: company, audience, tone, visual style, languages, prohibited claims, CTA patterns.

2. **Content plan** — create a 7-day or 30-day calendar organized by content pillars.

   **⚠️ User's preferred content planning engagement process (propose → agree → calendar → generate):**

   Do NOT skip to building a full calendar or generating assets. The user wants this structured flow:

   a. **Propose content type counts** — e.g. "7 carousels (4 slides each) + 4 reels". State the totals upfront.
   b. **Allocate purposes per content type** — for each carousel and each reel, propose a specific purpose/pillar (educational, product showcase, testimonial, conversion CTA, BTS, etc.). Present in a clear allocation table.
   c. **Wait for user review and agreement** — the user must explicitly agree to the allocations before you proceed. Do not skip to the calendar or generation.
   d. **Build the calendar** — only after agreement, propose specific dates for both "Generate" (when to create assets) and "Publish" (when to post). Align with course launches, events, and enrollment deadlines.
   e. **Only then generate assets** — proceed to step 3+ only after the calendar is agreed.

   **Common pitfall:** Proposing a full detailed calendar with content titles, dates, and strategies in one go without first getting agreement on the high-level allocation is premature. The user wants to shape the allocation first, then drill into the schedule.

3. **Draft** — write the post caption, hook, script/storyboard, hashtags, and CTA.
4. **Generate assets** — use configured image/video APIs or built-in image/video tools; save outputs locally.
5. **Preview** — send the user a Telegram preview with text, asset(s), platform(s), and proposed timing.
6. **Revise or approve** — incorporate edits; only continue to publishing on explicit approval.
7. **Publish/schedule** — use platform API credentials if configured; record published URLs and metadata.
8. **Report** — maintain a simple log of drafts, approvals, published content, and performance metrics when available.

## Pre-code checklist

Before creating any new code files, API routes, or scripts:

1. **Check existing branches** — `git branch -a` may show a feature branch with the work already done
2. **Check existing API endpoints** — a test `curl` against the target URL may reveal the API already exists
3. **Check response shapes** — don't assume response keys. Make a test call first and inspect the actual JSON
4. **Check if the repo has docs** — look for `docs/` directory with integration guides
5. **Check if the task is in a different branch** — search for `codex/` or `feat/` or `feature/` branches

Creating code that already exists wastes time and requires reverting before the real work can begin.

## Recommended workspace

Default durable workspace for a single brand:

```text
/opt/data/social-content/
  brand-guide.md
  setup-checklist.md
  calendar/
  drafts/
  assets/images/
  assets/videos/
  approved/
  published/
  reports/
```

For multiple brands on the same server, prefer a brand registry and one isolated workspace per brand:

```text
/opt/data/social-content/brands/
  brand-registry.json
  <brand-slug>/
    brand-guide.md
    assets/
      logos/
      fonts/
      references/
      backgrounds/
    source-materials/
      ebooks/
      docs/
    carousel-plans/
    automation/
      daily-carousel-state.json
      make-webhook.json
    drafts/
    generated/
      cron/
    approved/
    published/
    reports/
    scripts/
```

See `references/multi-brand-carousel-workspace.md` for the full multi-brand + ebook-carousel pattern.

Do not assume these paths exist; create them when starting an implementation. If the user has a project repo or preferred workspace, use that instead.

## Brand guide checklist

Collect or maintain:

- Company name, website, and social links
- Industry and location
- Products/services
- Target customers and decision makers
- Customer pain points
- Value proposition and proof points
- Brand personality and tone of voice
- Languages, especially Mongolian vs English vs bilingual
- Words/phrases to use and avoid
- Visual identity: logo, colors, fonts, photography/illustration style
- Competitors or reference brands
- Monthly goal: awareness, leads, sales, hiring, education, CRM nurturing

Store detailed brand rules in a file/skill, not only memory. Memory should hold only compact, durable facts.

## Content pillars

Good starting pillars:

1. Educational
2. Problem to solution
3. Product/service explanation
4. Case study/example
5. Behind-the-scenes
6. FAQ / objection handling
7. Lead-generation offer
8. Trust-building / proof
9. AI, technology, or business insights
10. Campaigns or time-sensitive offers

## Draft metadata format

Every generated post should have machine-readable metadata near the draft:

```yaml
id: 2026-05-23-example-post
status: draft
platforms:
  - facebook
  - instagram
content_type: image_post
language: mn
caption: ""
hashtags: []
asset_files: []
approval_status: pending
approved_by: ""
approved_at: ""
publish_time: ""
published_urls: []
```

## Cron-job orchestration (automated daily brand posts)

Three architectures — choose based on data source, generation backend, and approval requirements.

### Architecture C: External DB-driven (Supabase/Postgres) with Approval Gate

Use this architecture when the user manages their content schedule in an **external database** (Supabase, Postgres, etc.) instead of local state files, and wants a **human approval step** between generation and publishing.

**⚠️ ALWAYS CHECK FOR EXISTING CODE BEFORE CREATING:** Before writing any new API routes, models, or integration code, check all remote branches in the repo first — `git branch -a | grep <feature>`. The Postly backend already existed in `codex/postly-backend-supabase-pooler` and building a duplicate from scratch required reverting. Merge the existing branch instead.

**⚠️ VERIFY THE API CONTRACT WITH A TEST CALL:** Before writing integration code, make a raw `curl` call to confirm the endpoint exists and learn its actual response keys:
```bash
# Without auth → should be 401 if endpoint exists
curl -s -w "\nHTTP: %{http_code}" "$BASE/api/hermes/postly/planned"
# With auth → should be 200 with actual data shape
curl -s -H "x-hermes-secret: $SECRET" "$BASE/api/hermes/postly/planned" | python3 -m json.tool | head -20
```
The response keys may not be what you expect (e.g., `{ "items": [...] }` not `{ "planned": [...] }`). Learn from the live API, not from assumptions.

**Flow:**
```
User populates Supabase table (brand, post_date, content, template_id)
    ↓
Cron job queries Supabase for "today's unscheduled posts"
    ↓
Generates poster via KIE.AI GPT Image 2
    ↓
Sends Telegram preview → USER APPROVAL REQUIRED
    ↓
User approves → Webhook fires (Make.com / custom endpoint) → publishes
```

**Implementation steps:**

1. **Supabase setup** — User provides Supabase project URL + anon/service_role key. Expected table structure (adapt to user's schema):

```sql
CREATE TABLE content_schedule (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand TEXT NOT NULL,          -- 'ai-global', 'postly', 'supernova'
  post_date DATE NOT NULL,
  post_time TIME,              -- optional, for scheduled post times
  content_type TEXT,           -- 'carousel', 'single', 'story'
  topic TEXT,                  -- short title
  body_text TEXT,              -- the Mongolian copy for the post
  template_id TEXT,            -- which background/template to use
  image_slot_prompts JSONB,    -- optional: per-slot KIE prompts
  status TEXT DEFAULT 'pending', -- pending → generated → approved → published
  kie_task_ids JSONB,          -- track KIE generation task IDs
  generated_assets JSONB,      -- local file paths of generated images
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

2. **Cron job creation** — LLM-driven pattern (approval gate requires agent reasoning):
   ```python
   cronjob(
     action="create",
     name="Brand Supabase content pipeline",
     schedule="0 6 * * *",  # check daily
     deliver="origin",
     skills=["social-media-automation", "kie-content-maker"],
     prompt="""1. Query Supabase `content_schedule` table for rows with status='pending' and post_date=today
2. For each pending row: read brand, topic, body_text, template_id
3. Generate poster via KIE.ai GPT Image 2 (gpt-image-2-text-to-image or image-to-image)
4. Save to /opt/data/social-content/brands/<brand>/generated/pending/<id>/
5. Update Supabase row: status='generated', generated_assets=<paths>
6. Send Telegram preview with clear approval buttons/prompt
7. Do NOT publish — wait for user approval""",
     enabled_toolsets=["terminal", "file", "skills"],
   )
   ```

3. **Approval handling** — The user reviews the preview and responds. On approval (e.g. "Approve" or "Zuvshuurei"):
   - Read the row from Supabase for the matching brand/topic
   - Update status to 'approved'
   - Send to webhook (Make.com or custom endpoint) with multipart images + metadata
   - Update status to 'published' and set published_at

4. **Webhook publishing** — On approval, use curl multipart POST to the user's webhook URL. The webhook URL can be stored in a `webhook_config` table or a local config file.

```bash
curl -s -X POST "$WEBHOOK_URL" \
  -F "brand=$BRAND" \
  -F "topic=$TOPIC" \
  -F "post_date=$DATE" \
  -F "body_text=$BODY" \
  -F "slide1=@/path/to/slide-01.jpg"
```

5. **Key differences from Architecture A/B:**

| Aspect | A (LLM-driven) | B (Script-only) | C (DB-driven + Approval) |
|--------|---------------|-----------------|--------------------------|
| Data source | Local state file | Local state file | **External Supabase DB** |
| Content plan | Local markdown | Local markdown | **In DB table** |
| Approval | Pre-approved series | Pre-approved series | **Approval gate per post** |
| Publishing | Auto after generation | Auto after generation | **Webhook after user says yes** |
| Multi-brand | Separate workspaces | Separate workspaces | **Single DB, brand column** |

**Pitfalls:**
- Supabase service_role key has admin access — use row-level security or an anon key with restricted permissions
- Approval is asynchronous — the cron may generate and wait hours for the user to approve. Don't block the next tick on previous unapproved posts
- Store the webhook URL in an env var or local config, not in the DB (it's infrastructure config, not content data)
- If the user has multiple brands, the DB `brand` column maps to the workspace under `/opt/data/social-content/brands/<brand>/`
- Always use the user's local timezone (Asia/Ulaanbaatar for this user) when querying "today's posts" — UTC comparison will miss/misalign dates. In Supabase queries: `post_date = CURRENT_DATE AT TIME ZONE 'Asia/Ulaanbaatar'`

Both Architecture A and B are documented in full at references/cron-carousel-autopost.md.

### Architecture A: LLM-driven (no_agent: false, uses FAL.ai for image generation)

The Hermes agent generates slides via FAL.ai image_generate tool, then runs a publish script.

1. Create brand automation files:
   - automation/daily-carousel-state.json — state: series_total, next_carousel, completed, last_run
   - automation/make-webhook.json — webhook URL and field definitions
   - carousel-plans/<source>-4-slide-carousel-plan.md — N. Topic format topic list
   - scripts/ — publish scripts (copy to ~/.hermes/scripts/ for cron)

2. Cron job creation:
   - Attach social-media-automation as skills
   - no_agent: false — agent reads state, generates slides, runs publish script
   - script: <filename> — ONLY relative filename in ~/.hermes/scripts/. Absolute paths rejected.
   - Set model/provider explicitly so the job survives provider changes.
   - enabled_toolsets: ["terminal", "file", "skills"]

3. Prompt structure:
   - Read state for next_carousel
   - Look up topic from carousel-plans/
   - Generate 4 GPT Image 2 slides via image_generate tool (FAL.ai)
   - Save to generated/cron/carousel-NN/
   - Run script (webhook send + state advance)
   - Approval-first relaxed for cron — user pre-approved the series

4. Error recovery:
   - Script exits non-zero -> state not advanced -> next tick retries same carousel
   - Script should check for existing slides before re-sending

### Architecture B: Script-only (no_agent: true, uses KIE.AI API directly)

A single self-contained Python script handles everything: generating slides via KIE.AI GPT Image 2 with a pre-built slide template system, downloading, and sending to Make.com. No LLM tokens consumed. Choose this when the user has KIE_API_KEY (not FAL_KEY).

See `references/cron-carousel-autopost.md` section "Pre-generated slide template system (Architecture B)" and "Full self-contained Python script pattern" for implementation details including KIE API quirks (doubly-stringified resultJson, download URL response shape, per-slide failure handling, permalink archival).

1. Create same automation files (state, webhook, plan).

2. Write a Python script in ~/.hermes/scripts/ that:
   - Reads state file, looks up topic from plan
   - Generates 4 slides via POST https://api.kie.ai/api/v1/jobs/createTask with model gpt-image-2-text-to-image
   - Polls each via GET /api/v1/jobs/recordInfo until state=success (~3 min/slide)
   - Parses resultJson (a stringified JSON, not a dict) for resultUrls[0]
   - Downloads via POST /api/v1/common/download-url then saves immediately (KIE URLs expire fast)
   - Converts PNG to JPG with convert or cp
   - Sends multipart to Make.com via curl subprocess
   - Advances state on HTTP 200

3. Cron job creation:
   ```python
   cronjob(
     action="create",
     name="Brand daily carousel via KIE",
     schedule="0 1 * * *",
     deliver="origin",
     script="brand_daily_carousel.py",
     no_agent=True,
   )
   ```

4. Key pitfalls:
   - Write JSON payload to temp file or use @file syntax to avoid curl Cyrillic escaping
   - KIE download URLs expire quickly — save immediately after getting them
   - **`/api/v1/common/download-url` response shape:** `{"code":200, "msg":"success", "data":"<signed-url>"}` — `data` is a **string**, not a dict. Parse as `signed_url = json.loads(resp.read())["data"]`. Do NOT call `.get("downloadUrl")` on it — the original KIE tempfile URL returns 403 without signed params.
   - Use python3 -u or sys.stdout.reconfigure() for unbuffered output in cron context
   - KIE recordInfo resultJson is a stringified JSON string, parse it explicitly
   - If converting PNG to JPG, check that convert (ImageMagick) exists; fall back to cp
   - Use absolute paths in the script since it runs from ~/.hermes/scripts/

## Veo 3.1 Fast Multi-Scene Reel Merging

When generating a multi-part story video via Veo 3.1 Fast (e.g. Postly's 3-scene "struggle → discovery → freedom" arc), the output is N separate MP4 clips (~8s each). Merge them into one continuous Reel before publishing.

### Workflow

1. **Generate** N scenes via Veo 3.1 Fast sequentially (pass seeds/IDs for character continuity)
2. **Verify** all clips share the same codec/resolution/audio format
3. **Merge** using FFmpeg concat demuxer (lossless `-c copy`, no re-encode needed when formats match)
4. **Add captions** via drawtext filter or subtitle burn-in for Mongolian/Cyrillic text
5. **Review** with the user or client in Telegram before publishing

### Typical Veo Scene Properties

- Resolution: 720×1280 (9:16 vertical)
- Codec: h264, Audio: aac
- Duration: ~8s per scene
- Veo output includes audio (`has_audio: true` in the manifest)

### Merge Command (lossless concat)

```bash
echo "file '/path/scene-01.mp4'" > /tmp/concat.txt
echo "file '/path/scene-02.mp4'" >> /tmp/concat.txt
echo "file '/path/scene-03.mp4'" >> /tmp/concat.txt
ffmpeg -f concat -safe 0 -i /tmp/concat.txt -c copy merged-reel.mp4 -y
```

For full details including caption overlay, audio replacement, and crossfade transitions, see `references/ffmpeg-veo-video-merge.md`.

### Word-by-Word Mongolian Captions with ASS Subtitles

When the user wants captions that show **2-4 words at a time** (synced with narration/voiceover) using a **custom font** with a **glow effect**, use the ASS (Advanced SubStation Alpha) subtitle format — not SRT.

**Workflow:**
1. Download the custom font to `/opt/data/fonts/` (e.g. Nunito from Google Fonts)
2. Create an `.ass` file with a `[V4+ Styles]` section specifying the font, color, and glow parameters
3. Write short `Dialogue` lines for each word chunk (~1.5s apart)
4. Pass the `.ass` file to FFmpeg's `subtitles` filter with `fontsdir`

**Key ASS parameters for turquoise glow on white text:**
- `Fontname=Nunito-Bold` — custom font
- `PrimaryColour=&H00FFFFFF` — white fill
- `OutlineColour=&HC0D45E` — turquoise border (BGR format: #5ED4C0 → C0D45E)
- `Outline=6, BorderStyle=1` — wide outline
- Inline `{\blur3}` override — blurs the outline for soft glow

**Why ASS > SRT for brand content:** ASS supports per-line font overrides, glow/blur effects, precise positioning, and karaoke-style word highlighting — all needed when a client requests visually polished captions. SRT is limited to plain text at fixed positions.

See `references/ffmpeg-veo-video-merge.md` section "Step 4: Add Word-by-Word Captions with Glow" for the complete ASS template and rendering command.

## Google OAuth scope management for Sheets + Drive

**Critical pitfall: scope replacement, NOT merging.** Google OAuth consent prompts replace the token's existing scopes; they do not add to them. If the user first authorizes `spreadsheets` scope, then later authorizes `drive.file` via a new consent URL, the second auth REPLACES the token — the Sheets API stops working (401 error).

**Fix:** Generate ONE authorization URL with ALL needed scopes:\n```\nscope=https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file\n```\nSave the combined token. The final token JSON should list both scopes. If you discover mid-session that a scope is missing, generate a new combined-scope URL, ask the user to re-authorize, and overwrite the old token. Do NOT try to merge two separate tokens — OAuth doesn't allow incremental scope addition via refresh.

### PKCE code_verifier gotcha

When generating OAuth authorization URLs programmatically, modern Google OAuth requires **PKCE** (Proof Key for Code Exchange). The `google_auth_oauthlib` Flow generates a `code_challenge` (from a `code_verifier`) inside the authorization URL. When the user later pastes the redirect URL containing the authorization code, you MUST use the **same Flow instance** (or the saved `code_verifier`) to exchange the code — otherwise you get `InvalidGrantError: Missing code verifier`.

**Pattern that fails:** Generating a URL in one call and trying to `fetch_token(code=...)` in a separate call with a fresh Flow instance. The fresh instance has a different `code_verifier` (or none), causing the PKCE mismatch.

**Pattern that works (manual PKCE via requests):** Generate the `code_verifier` and `code_challenge` yourself, save them alongside the URL, then exchange the code using requests.post to the token endpoint with the saved `code_verifier`:

```python
import secrets, hashlib, base64, requests

code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode()

# Generate URL with these PKCE values
auth_url = f'{cfg[\"auth_uri\"]}?...&code_challenge_method=S256&code_challenge={code_challenge}'

# Save code_verifier to a file
json.dump({'code_verifier': code_verifier, 'client_id': ..., 'client_secret': ...}, f)

# Later, exchange code:
resp = requests.post('https://oauth2.googleapis.com/token', data={
    'code': user_code,
    'client_id': saved['client_id'],
    'client_secret': saved['client_secret'],
    'redirect_uri': 'http://localhost',
    'grant_type': 'authorization_code',
    'code_verifier': saved['code_verifier'],  # MUST match the one used in auth_url
})
```

**Alternative (Flow instance persistence):** If using `google_auth_oauthlib.flow.Flow`, keep the Flow object alive in the same process — do not serialize/deserialize it. Saving the Flow with `pickle` fails (`AttributeError: Can't get local object 'OAuth2Session.__init__.<locals>.<lambda>'`). Instead, generate the URL, pass it to the user, then immediately call `flow.fetch_token(code=...)` in the same execution before the instance is destroyed.

**Common symptom:** user authorizes successfully (gets a `code=` in the redirect URL) but the token exchange fails with a PKCE error. Fix: ensure the same code_verifier is used for both URL generation and token exchange.

## API credential setup

Prefer environment variables or Hermes .env; do not hardcode secrets in skills, scripts, or drafts.

Image generation:

```env
IMAGE_PROVIDER=
IMAGE_API_BASE_URL=
IMAGE_API_KEY=
IMAGE_MODEL=
```

Video generation:

```env
VIDEO_PROVIDER=
VIDEO_API_BASE_URL=
VIDEO_API_KEY=
VIDEO_MODEL=
```

Meta / Facebook / Instagram:

```env
META_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=
INSTAGRAM_BUSINESS_ID=
```

LinkedIn:

```env
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_ORGANIZATION_ID=
```

TikTok and X/Twitter credentials vary; inspect the provider docs and use the narrowest permissions possible.

## Post-publish cleanup policy

After content is successfully published via webhook, decide whether to delete local generated files. Rules derived from this user's preferences:

- **Under 500 MB total storage** across all brands → auto-delete published carousel/image/video files after successful publish. This keeps disk usage low without asking.
- **At or above 500 MB total** → do NOT auto-delete. Ask the user: *"Published content has accumulated. Should I delete older published files?"* Wait for explicit approval before removing anything.
- Check total storage before each cleanup run using the script at `/opt/data/scripts/cleanup_published_content.py`. Dry-run with no args; execute with `--execute` flag.

The cleanup script:
1. Scans all brand `generated/` directories for `metadata.yaml` files with `status: published`
2. Calculates total storage across all brands
3. If under 500 MB: deletes published directories automatically
4. If 500 MB+: reports totals and refuses to delete — signals caller to ask user

This policy exists in memory so Hermes remembers it across sessions. Update it if the user changes the threshold.

## Make.com webhook: multipart with Cyrillic form fields (carousels)

**For JSON poster/reel delivery (current format), see `references/instagram-make-url-delivery.md` — covers both the legacy `images`-array format and the current `file_name`+`data` objects + `instagram_urls` format (June 2026+).**

Confirmed working pattern for sending 4 carousel slides to a Make.com webhook that expects `multipart/form-data`:

```bash
curl -s -X POST "https://hook.us1.make.com/..." \
  -F "brand=supernova" \
  -F "campaign=Telomer Effect Ebook Carousel Series" \
  -F "carousel_number=3" \
  -F "topic=Урт теломерын хүч" \
  -F "language=mn" \
  -F "format=1:1 square carousel" \
  -F "caption=Теломер — эсийн залуу байдлын толь..." \
  -F "slide1=@/path/to/slide-01.jpg" \
  -F "slide2=@/path/to/slide-02.jpg" \
  -F "slide3=@/path/to/slide-03.jpg" \
  -F "slide4=@/path/to/slide-04.jpg"
```

Key points:
- Cyrillic/Mongolian text in form fields works correctly with `-F` (no encoding issues)
- `@filename` for file attachments sends raw binary
- The `@` syntax requires absolute paths when the script runs from a different directory
- Make.com returns `"Accepted"` with HTTP 200 on success
- Multipart content type is inferred automatically; explicit `--header` for content-type is NOT needed (and breaks multipart boundary parsing)

## Platform notes

- **Facebook Page:** typically needs Meta Graph API page token and pages_manage_posts, pages_read_engagement, and pages_show_list permissions.
- **Instagram Business:** account must be Business/Creator and connected to a Facebook Page; publishing uses Meta Graph API and often requires media container creation + publish.
- **LinkedIn Page:** requires organization ID and organization social posting permissions.
- **TikTok:** publishing APIs can be restrictive; verify app/account access before promising automation.
- **X/Twitter:** use the xurl skill/tooling when available for X-specific workflows.

## MVP progression

Start small unless the user explicitly asks for full integration:

1. **MVP 1:** brand guide, 7-day calendar, 3 draft posts, generated images, Telegram previews, local storage; no posting.
2. **MVP 2:** add video generation and one short Reel/TikTok-style video.
3. **MVP 3:** add platform publishing/scheduling with approval-first safeguards and published URL logging.

## User-specific defaults

For Battushig's Telegram workflow, assume Mongolian-language collaboration is welcome and that social posts should be previewed in Telegram before publishing. The durable rule is approval-first: AI creates, user approves, AI posts.

When the user names a brand, use that brand's workspace under /opt/data/social-content/brands/<brand>/ and update its brand-guide.md, assets/, and carousel-plans/ rather than mixing assets into a generic folder.

## Book/PDF repurposing

When the user uploads a book, report, or long PDF and asks for social posts from its most important facts or ideas, use a copyright-safe repurposing workflow: extract the TOC/sample pages, build a 10-post pilot or 24-30 post full series, paraphrase rather than copying long excerpts, and turn each idea into caption + carousel + short video script + visual prompt. See references/book-to-social-series.md.

For branded Mongolian carousel series, keep slide copy short enough for deterministic overlay: prefer 1-2 headline lines plus 2 concise bullets; if a slide has 3 bullets, reduce body font size and verify in a contact sheet before sending. Add auto-fit headline logic and compact phone capsules to avoid clipped Cyrillic text or phone numbers.

If the user dislikes the local font/overlay look and wants the carousel to match a provided reference poster's font style, phone frame, logo placement, and colors, generate one complete final poster per slide with KIE GPT Image 2 (`gpt-image-2-text-to-image`) instead of forcing local system fonts. For Battushig's brand carousels, treat GPT Image 2 as the default final-poster model across brands when exact typography/style matters. Prompt explicitly for `ONE separate 1:1 square slide, not a collage and not four slides in one image`; if the user requested separate images, send only the individual slide files, not a contact sheet. Because GPT Image 2 renders the text, manually QA Mongolian spelling, prices, and phone numbers before posting.

**⚠️ CRITICAL: GPT Image 2 prompt-only generation invents brand logos.** Even with very detailed prompts specifying exact color hexes, logo description, tagline text, and brand name, the model always produces a made-up logo. This was confirmed across 4+ test slides and further refined prompts — every single one had a fake/imagined logo that bore no resemblance to the real one.

**However, prompt enrichment DOES improve color consistency and layout fidelity.** When the user chooses to stick with prompt-only generation (option 2), the following prompt elements ARE effective:
- Exact hex color codes (#F20B2E for red, #1768B5 for blue, etc.)
- Detailed layout structure (top-left white capsule for title, blue ribbon slide counter, large white content panel, bottom-right phone pill with red outline, red/blue wave footer)
- Typography rules (heavy rounded bold sans-serif, dark navy for text, red for emphasis)
- A long reusable BRAND_PROMPT string that gets prepended to every slide prompt

What DOESN'T work despite any prompt detail:
- The actual brand logo — the model invents its own every time
- Exact text placement on complex layouts — the model may shift elements
- Consistent Mongolian/Cyrillic spelling — always QA visually before publishing

**Decision tree when the user says "logo/branding is wrong":**

1. **If the user says "improve the prompt" or "add more detail" (Option 2)** → Do it. Enrich the prompt with exact hex colors, layout structure, logo description, slide content roles. Test one slide. If the user still complains about the logo, switch to two-stage. Logos will still be invented, but colors and layout will improve.

2. **If the user immediately says "this is wrong, fix it" without asking for prompt fixes** → Propose the two-stage approach directly: "GPT Image 2 prompt-only generation can't use real brand assets. I'll switch to generating clean backgrounds and overlaying the actual logo and brand colors locally."

3. **If the user says "use the logo I sent" (sending a JPG/PNG file)** → Still two-stage. Prompt-only models cannot embed a specific image. Save the image to assets/logos/, use it in the Pillow overlay pipeline. Explain: "I saved your logo. Now I'll generate text-free backgrounds and overlay it with the exact brand colors."

Two-stage deterministic pattern:
1. **Stage 1 — Background generation**: Prompt KIE GPT Image 2 or Nano Banana 2 for a text-free background (`NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS`) with negative space reserved for logo, title, and phone.
2. **Stage 2 — Pillow compositing**: Overlay actual brand logo (from assets/logos/), exact hex colors, Mongolian text, slide numbers, phone capsule, and designed frames locally.

For a concrete count request like how many 4-image carousel posters can this ebook make, inspect the PDF table of contents: count major sections/chapters for the recommended campaign and detailed subsections for an expanded campaign. Report both carousel count x 4 slides = total images, and save the plan in the brand workspace when a brand is specified.

## References

- `references/hermes-vercel-make-trideirectional-pipeline.md` — Tri-directional Hermes ↔ Vercel ↔ Make.com integration pipeline for Postly-style content management. Endpoint contract templates, API-first query rule (don't search local files — query Vercel API), Make.com multipart webhook pattern, Telegram approval flow with cron state management, **deployment verification** (www.postly.mn now points to agenticforceweb, not Postly backend).
- `scripts/verify-postly-api-status.sh` — quick domain mapping check script for all Postly domains; run with `bash scripts/verify-postly-api-status.sh <x-hermes-secret>`.
- templates/brand-guide.md — starter brand guide to copy into a workspace.
- templates/draft-metadata.yaml — metadata block for post drafts.
- templates/supernova-carousel-overlay-template.py — reusable Pillow overlay template for Supernova v2 carousels.
- `references/supabase-db-driven-pipeline.md` — Architecture C: external Supabase/Postgres DB-driven social content pipeline with approval gate. Full table schema, query patterns, timezone handling, status lifecycle, and error recovery.
- references/cron-carousel-autopost.md — full cron orchestration with Architecture A and B.
- references/multi-brand-carousel-workspace.md — multi-brand layout and ebook-to-4-slide-carousel.
- references/supernova-gpt-image-2-carousel-workflow.md — GPT Image 2 carousel poster generation.
- `references/make-carousel-autopost-webhook.md` — multipart Make.com webhook pattern.
- `references/instagram-make-url-delivery.md` — Instagram delivery via Make.com requires public image URLs, not file uploads. Covers freeimage.host upload API, legacy multipart format, current `file_name`+`data` objects + `instagram_urls` JSON format (June 2026+), video/reel delivery, and the "send to make" ambiguity pitfall (infer most recently discussed content batch, not last action taken).
