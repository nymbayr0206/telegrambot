---
name: news-poster
description: AI Global news/success story poster using news-post-1 template. Fixed AI TECH NEWS bar + footer + logo-overlay. Dynamic headline, person/event photo, body text.
version: 1.3.0
author: Hermes Agent
tags:
  - ai-global
  - news-poster
  - success-story
  - template
  - kie-ai
trigger: user says news post, news poster, create news poster, success story poster
---

# News Poster Skill

## Overview

Use this skill when the user asks to create a poster using the **"news post 1"** template. The template is a 1:1 square (1254x1254) gold-background poster with fixed AI Global branding. It serves TWO content types:

| Type | Content | Example |
|------|---------|---------|
| **AI News** | Latest AI/tech news with article photo | Apple Poke AI agent, Meta WhatsApp AI |
| **Success Story** | Real person story about using AI, with person's photo | Alex Finn ($300K ARR with zero coding) |

Both use the exact same template layout — only the content changes.

## Template Location

```
/opt/data/social-content/brands/ai-global/templates/news-post-1/
```

## Template Assets

| Asset | URL |
|-------|------|
| Template ref (tmpfiles) | https://tmpfiles.org/wlw66eagSUkd/template-reference.jpg |
| Spec documentation | template-spec.md |
| KIE image-to-image requires `/dl/` URLs | Yes — convert `tmpfiles.org/w` → `tmpfiles.org/dl/w` or KIE fails |

## Template Structure — Fixed vs Dynamic

### 🔒 FIXED (ABSOLUTELY NEVER change):
- **Top logo** — AI Global logo. NEVER regenerate or modify. Send the logo as the 3rd `input_urls` reference image to KIE (see Step 4 Preferred Method). Fallback: overlay the logo from `/opt/data/social-content/brands/ai-global/assets/logos/logo-ai-global-transparent.png` using Pillow (top-right, 15% of actual output width).
- **"AI TECH NEWS"** branding bar text — NEVER alter the lettering, font, or position.
- **Footer bar** — Phone: 8909 7454, Address: Ayud tower 601 TooT, Web: www.aiglobal.mn. NEVER change.

### ✅ DYNAMIC (can change freely each time):
- **HEADLINE** — Bold text (y=18-24%). WHITE + DARK CHARCOAL combo on gold.
- **NEWS IMAGE** — Main article image in the middle frame (y=25-68%).
- **BODY TEXT** — 2-3 short lines (y=70-88%).
- **Background texture/gradient** — The gold area texture CAN vary. Not fixed.

## Workflow

### Step 1: Fetch Content (Two Modes)

**Mode A — AI News:** Fetch from RSS feeds (TechCrunch AI, Ars Technica, HN Show). See `references/real-person-ai-stories.md` for full source list.
**Mode B — Success Stories:** Fetch real-person AI stories from Hacker News Show HN RSS (`https://hnrss.org/show`), Substack vibe coding newsletters, or Indie Hackers. Filter for personal narrative + specific person name + revenue/metrics.

For success stories, also find the person's real photo:
1. Find their Twitter/X profile from the article
2. Extract profile image URL from their X page
3. Download larger version (remove `_normal`, `_bigger`, `_200x200` suffixes)
4. Upload to tmpfiles.org for KIE reference

### Step 2: Get News Image + Upload to Hosting

1. Download og:image with proper Referer header (`-H 'Referer: https://techcrunch.com/'` for TechCrunch, `-H 'Referer: https://arstechnica.com/'` for Ars)
2. Convert to PNG with Pillow if needed
3. Upload to **catbox.moe** (preferred — more reliable for KIE): `curl -s -F "reqtype=fileupload" -F "time=72h" -F "fileToUpload=@image.png" https://litterbox.catbox.moe/resources/internals/api.php`
4. Extract URL from response (returns raw URL string like `https://litter.catbox.moe/xxxxxx.png`)
5. This URL works DIRECTLY in KIE `input_urls` — no conversion needed
6. Verify reachable: `curl -s -o /dev/null -w "%{http_code}" "URL"` — should return 200
7. **Fallback:** If catbox.moe is down, use tmpfiles.org with `/dl/` conversion (see Known Issues)

### Step 3: Prepare ALL Posters' Captions Upfront

Before generating any poster image, prepare the Mongolian captions for ALL posters in the batch. This user preference (Battushig, June 9, 2026):

- Write **~50 words per caption** in Mongolian Cyrillic
- Each caption: concise hook + key fact + 2-3 relevant hashtags
- Present all N captions to the user alongside the **first poster image only**
- Only generate remaining posters after user approves the first one

Example format:
```
1️⃣ [Topic] — Subtitle
> ~50-word Mongolian caption with emoji and hashtags

2️⃣ [Topic 2] — Subtitle
> ~50-word Mongolian caption...
```

### Step 4: Generate via KIE

### ⭐ PREFERRED METHOD: Send Logo as 3rd Reference Image (June 9, 2026 — User-Corrected)

**This is the user's preferred approach.** Send THREE images in `input_urls`: template + article/news photo + logo. Tell KIE to preserve the logo from the third reference.

**Process:**
1. Upload template, article image, AND logo to catbox.moe
2. Include ALL THREE in `input_urls: [template_url, article_url, logo_url]`
3. In prompt: "The AI Global logo at top-right must match the THIRD reference image (logo.png). Keep the logo exactly the same at the top-right position."
4. **Do NOT overlay the logo with Pillow afterward** — the user explicitly rejected this: *"logo must be sent to kie"* and *"Dont need to overlay our logo"*

**Why this works now:** When the logo is sent as a standalone image in `input_urls` with explicit "match this" instructions, GPT Image 2 preserves it far better than asking it to keep the logo that's embedded in the template reference. The model treats the logo image as a "character reference," not a style element to reinterpret.

#### The 3-Image Prompt Pattern**

```text
Create ONE 1:1 square social media news poster. THREE reference images provided.

CRITICAL - TEMPLATE PRESERVATION:
The FIRST image is the TEMPLATE. It has a FIXED layout that MUST be preserved EXACTLY:
- The AI Global logo at top-right must match the THIRD reference image (logo.png). Keep the logo exactly the same at the top-right position.
- "AI TECH NEWS" branding bar: DO NOT change the text, font, or position
- Dark footer bar at bottom: DO NOT change "8909 7454", "Ayud tower 601 TooT", "www.aiglobal.mn"
- Gold/amber background: DO NOT change the color
- The overall layout, spacing, and proportions MUST remain identical to the template

ONLY change these THREE things from the template:
1. HEADLINE text (in the headline area, y=18-24%)
2. The image inside the middle rectangular frame (y=25-68%) — replace with the SECOND reference image
3. BODY text below the image (y=70-88%)

HEADLINE: "[WHITE PART]" in WHITE text + "[DARK PART]" in DARK CHARCOAL text.

IMAGE PLACEMENT: Place the [description] photo from the SECOND image into the existing rectangular frame in the middle of the template. The frame is already on the template — just fill it with the new image.

BODY TEXT (short lines):
"[Line 1]"
"[Line 2]"
"[Line 3]"

Style: Professional news poster. Mongolian Cyrillic text ONLY. Premium finish.
```

**JSON structure:**
```json
{
  "model": "gpt-image-2-image-to-image",
  "input": {
    "prompt": "...",
    "input_urls": [
      "https://litter.catbox.moe/xxxxxx.jpg",  // template
      "https://litter.catbox.moe/yyyyyy.png",  // article photo
      "https://litter.catbox.moe/zzzzzz.png"   // logo
    ],
    "aspect_ratio": "1:1"
  }
}
```

### ⚠️ FALLBACK: Two-Stage (NO LOGO + Pillow Overlay)

Use ONLY if the 3-image approach produces a distorted logo. This was the original method, but the user has explicitly rejected it as the primary approach.

#### Stage 1: Generate WITHOUT a logo
Include `"IMPORTANT - NO LOGO: The top area of the template has NO LOGO. Do NOT add, invent, or place any logo in the top area. Leave it as empty gold background."`

#### Stage 2: Overlay real logo with Pillow
Logo file: `/opt/data/social-content/brands/ai-global/assets/logos/logo-ai-global-transparent.png`

**⚠️ CRITICAL: Use actual image dimensions, not template dimensions.**
KIE outputs 1024×1024, NOT the template's 1254×1254. Always compute position dynamically:

```python
from PIL import Image

logo = Image.open('/opt/data/social-content/brands/ai-global/assets/logos/logo-ai-global-transparent.png')
img = Image.open('generated.png').convert('RGBA')
w, h = img.size  # ALWAYS use actual image size (KIE outputs 1024×1024)

logo_w = int(w * 0.15)  # 15% of actual width
logo_h = int(logo.size[1] * (logo_w / logo.size[0]))
logo_resized = logo.resize((logo_w, logo_h), Image.LANCZOS)
pos_x = w - logo_w - 20  # top-right
pos_y = 12

img.paste(logo_resized, (pos_x, pos_y), logo_resized)
img.convert('RGB').save('final.jpg', 'JPEG', quality=92)
```

#### Fallback Two-Stage Prompt

```text
Create ONE 1:1 square social media news poster. TWO reference images provided.

CRITICAL - TEMPLATE PRESERVATION:
The FIRST image is the TEMPLATE. It has a FIXED layout that MUST be preserved EXACTLY:
- [Fixed element 1]: DO NOT change, move, or regenerate
- [Fixed element 2]: DO NOT change the text, font, or position
- [Fixed element 3]: DO NOT change
- [Background]: DO NOT change the color
- The overall layout, spacing, and proportions MUST remain identical to the template

ONLY change these THREE things from the template:
1. HEADLINE text (in the headline area, y=18-24%)
2. The image inside the middle rectangular frame (y=25-68%) — replace with the SECOND reference image
3. BODY text below the image (y=70-88%)

HEADLINE: "[WHITE PART]" in WHITE text + "[DARK PART]" in DARK CHARCOAL text.

IMAGE PLACEMENT: Place the [description] photo from the SECOND image into the existing rectangular frame in the middle of the template. The frame is already on the template — just fill it with the new image.

BODY TEXT (short lines):
"[Line 1]"
"[Line 2]"
"[Line 3]"

Style: Professional news poster. Mongolian Cyrillic text ONLY. Premium finish.
```

**Curl submission:**
```bash
curl -s --location "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @prompt.json
```

### Step 5: Poll & Download
- Poll `GET /api/v1/jobs/recordInfo?taskId=<id>` every 10s
- On success, `data.resultJson` is a JSON string: `{"resultUrls":["https://tempfile.aiquickdraw.com/..."]}`
- Convert to signed download URL via `POST /api/v1/common/download-url` with `{"url":"KIE_URL"}`
- `data` in response is a **string** (the signed URL), not a dict
- Download with curl and save as both .png and .jpg

### Step 6: Deliver
- MEDIA: path to the .jpg file
- Include source article URL for reference

### Step 7: Publish via Make.com Webhook (Optional)

After generating posters and delivering to Telegram, if the user asks to **publish to social media** (Instagram, Facebook), use the Make.com webhook with **public media URLs** (Instagram requires URLs, not file uploads).

**Webhook URL:** `https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e`

**MANDATORY:** Always include the `content_type` argument to route the Make.com scenario:
- Poster/news poster → `content_type=poster`
- Reel/video → `content_type=reel`
- Carousel (4-slide) → `content_type=carousel`

**⚠️ Pitfall — "send to make" shorthand can mean poster OR reel:** When the user says "send to make" / "send again to mle" without specifying, they may refer to the most recently discussed content item OR a previous batch. The Make.com webhook uses `content_type` to route to different publishing scenarios (reel → Instagram Reels, poster → carousel/feed post). Sending the wrong type causes the wrong scenario to fire. **Best practice:** If the last content discussed was a reel AND posters were previously discussed but not sent, default to posters. If unsure, rephrase to confirm: "posters or reels?"

#### Two Delivery Formats: JSON Array (Batch Posters) & Multipart (Single Items)

Both formats work with the same webhook URL. The Make.com scenario accepts both:

**Format A — JSON array (batch poster delivery, tested June 2026):** Clean for sending multiple posters at once with URLs:

```bash
WEBHOOK="https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e"

# Upload images to tmpfiles.org and get direct /dl/ URLs first
up1=$(curl -s -F "file=@poster1.jpg" https://tmpfiles.org/api/v1/upload)
img1=$(echo "$up1" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['url'])")
# Convert page URL to direct download URL: tmpfiles.org/w → tmpfiles.org/dl/w

curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
  \"content_type\": \"poster\",
  \"images\": [
    \"$img1\",
    \"$img2\",
    \"$img3\",
    \"$img4\"
  ],
  \"caption\": \"🔥 Unified caption text for all 4 slides...\n\n1️⃣ Slide 1 title\n2️⃣ Slide 2 title\n3️⃣ Slide 3 title\n4️⃣ Slide 4 title\n\n#AI #TechNews #AIGlobal\"
}"
```

**Format B — Multipart (single poster, tested for carousels/individual posts):**

```bash
curl -s -X POST "https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e" \
  -F "content_type=poster" \
  -F "image1_url=$img_url" \
  -F "caption1=..." \
  -F "total_posters=1" \
  -F "source=hermes_agent" \
  -F "brand=AI Global"
```

**For Reels/Videos — JSON POST with video_url (tested June 2026):** Instagram reels need a publicly accessible video URL. Upload to tmpfiles.org (preferred — handles 1.2MB+ MP4s without size limits):

```bash
# Upload video
upload=$(curl -s -F "file=@reel.mp4" https://tmpfiles.org/api/v1/upload)
page_url=$(echo "$upload" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['url'])")
# Extract direct download URL from the tmpfiles page
direct_url=$(curl -s "$page_url" | grep -oP 'https://tmpfiles.org/dl/[^"<>]+' | head -1)

# Send to Make.com
curl -s -X POST "https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e" \
  -H "Content-Type: application/json" \
  -d "{
  \"content_type\": \"reel\",
  \"video_url\": \"$direct_url\",
  \"caption\": \"Optional caption text\"
}"
```

Response: `"Accepted"` on success for all formats.

For the full Make.com delivery reference (batch posting, 4-in-1 posters, etc.), see the `aiglobal-success-story-carousel` skill's Pitfall #17.

## Known Issues

### KIE Internal Error 500 on Some Images
Some article images consistently fail with `"failCode": 500, "failMsg": "Internal Error, Please try again later."` on gpt-image-2-image-to-image even after retries. The Coralogix founders photo was one such case. Fix: switch to a different article/image entirely. The robot photo from Ars Technica worked on first retry.

### KIE Downscales Output to 1024×1024 (Not 1254×1254)
The template reference is 1254×1254, but KIE's `gpt-image-2-image-to-image` model downscales the output to **1024×1024** regardless of input size (confirmed June 9, 2026). **⚠️ CRITICAL: The Pillow logo overlay code MUST use `img.size` dynamically.** Hardcoding 1254-based coordinates (e.g. `pos_x = 1254 - logo_w - 20`) places the logo off-screen on 1024-wide images. Always use:

```python
w, h = img.size  # KIE outputs 1024×1024
pos_x = w - logo_w - 20
```

See Step 4 Stage 2 for the correct dynamic-position overlay code.

### tmpfiles.org is Unreliable for KIE — Use catbox.moe Instead
`tmpfiles.org` URLs are inconsistent for KIE `input_urls`. They may return `"Image fetch failed"` (failCode 400) on some KIE jobs while working on others. **catbox.moe litterbox is more reliable** (confirmed June 9, 2026 — worked on first attempt after tmpfiles.org failed 3 times):

```bash
# Upload to catbox.moe (72h expiry, 100% reliable for KIE)
url=$(curl -s -F "reqtype=fileupload" -F "time=72h" \
  -F "fileToUpload=@/path/to/image.png" \
  https://litterbox.catbox.moe/resources/internals/api.php)
# Returns: https://litter.catbox.moe/xxxxxx.png
# Use this URL DIRECTLY in KIE input_urls — no conversion needed
```

**Decision:** Default to catbox.moe for all KIE image-to-image input_urls. Only fall back to tmpfiles.org if catbox.moe is down.

### tmpfiles.org URL Format (Fallback Only)
If using tmpfiles.org, the upload response returns `https://tmpfiles.org/wXXXXXXX/filename.png`. **KIE gpt-image-2-image-to-image FAILS with the regular `w/` format** returning `"Image fetch failed..."` (confirmed June 9, 2026).

**Fix:** Convert to `/dl/` format:
- From: `https://tmpfiles.org/wywKZMBrc0Nd/apple-siri-news.png`
- To: `https://tmpfiles.org/dl/wywKZMBrc0Nd/apple-siri-news.png`

Suffix replacement rule: `tmpfiles.org/w` → `tmpfiles.org/dl/w`.

## Production Run — June 9, 2026

| # | Topic | Type | Article Source | Task ID | Credits | Output File |
|---|-------|------|---------------|---------|---------|-------------|
| 1 | Apple Siri AI — WWDC 2026 overhaul | AI News | TechCrunch | `97433cd0b96b77d304316505f707c426` | 6 | poster1_apple_siri_final_v2.jpg |
| 2 | Google I/O 2026 — Gemini Spark AI Agent | AI News | Google Blog | `266b03e04424f1c2caf7f195254d1452` | 6 | poster2_google_final.jpg |
| 3 | OpenAI Lockdown Mode — prompt injection protection | AI News | TechCrunch | `f807745faeb1213a58ca9ab837dfe506` | 6 | poster3_openai_final.jpg |
| 4 | Google Gemma 4 — open-weight models | AI News | Google Blog | `509327c74a1a1aa76628af8c57b537ac` | 6 | poster4_gemma_final.jpg |

**New workflow validated:** Used 3-image approach (template + article photo + logo in `input_urls`) — user accepted all 4. No Pillow overlay needed. catbox.moe hosting (tmpfiles.org was unreliable).

## Production Run — June 5-6, 2026

| # | Topic | Type | Article Source | Task ID | Credits | Output File |
|---|-------|------|---------------|---------|---------|-------------|
| 1 | Apple approves Poke as first AI agent on Messages for Business | AI News | TechCrunch | `4d6797d6e3ccebbabaa7d06c8f77980f` | 6 | test_post_1_v2.png |
| 2 | Meta WhatsApp AI agent available globally | AI News | TechCrunch | `ce29d6c665d1f8cadffe8e1ce36bad0a` | 6 | redo_whatsapp.png |
| 3 | Humanoid robots going viral - skeptic's guide | AI News | Ars Technica | `917f31c0c1a43d7491f3235e4aac6840` | 6 | redo_robots.png |
| 4 | Google Gemma 4 12B runs on laptops | AI News | Ars Technica | `2412976b5d29e55f8a3bd79fbe2ebece` | 6 | redo_gemma.png |
| 5 | Alex Finn — $300K ARR with zero coding experience | Success Story | Substack (John Ellison) | `319dd01a9d9f3f982a613107fe9665c1` | 6 | alex_finn_slide1.png |

All outputs are 1024×1024 PNG/JPG at `/opt/data/social-content/brands/ai-global/templates/news-post-1/`. (KIE downscales the 1254×1254 template reference to 1024×1024 — this is consistent and expected.)

## Related Skills

- `kie-content-maker` — KIE API integration patterns (task submission, polling, download, image-to-image)
- `rss-news-pipeline` — RSS feed fetching and article extraction
- `ai-global-brand-content` — broader AI Global brand content templates
- `aiglobal-success-story-carousel` — alternative KIE pipeline for 4-slide carousels, also contains the full Make.com webhook delivery reference (Pitfall #17)
