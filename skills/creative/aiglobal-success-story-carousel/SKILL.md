---
name: aiglobal-success-story-carousel
description: "AI Global branded content (carousels + standalone posters) via KIE image-to-image with uploaded reference images. Primary: KIE input_urls + gpt-image-2-image-to-image. NEVER describe templates textually — always upload reference images. NEVER use Pillow or local compositing."
version: 2.1.0
author: Hermes Agent
metadata:
  hermes:
    tags: [aiglobal, carousel, poster, template, branding, kie-ai, image-to-image]
    related_skills: [ai-global-brand-content, kie-content-maker, social-media-automation]
---

# AI Global Branded Content System (v2.1)

Covers both **student success story carousels** (4-slide) and **standalone posters** using the same KIE image-to-image pipeline.

## Core Philosophy

**Reference images are mandatory, not optional.** NEVER describe a template/background textually — always upload it to KIE file storage and pass via `input_urls`. The user explicitly rejected text-only template descriptions ("temp1 iig ashigla gedeg ni gpt2 ruu yawuulahdaa temp1 iig reference bolgoj yawuulah yostoi").

**Everything through KIE.** Do NOT use Pillow. Do NOT use local compositing. Do NOT generate backgrounds from text prompts alone when a reference template exists.

## Standalone Posters (temp1 Background)

AI Global has ONE standard poster background template at:
`/opt/data/social-content/brands/ai-global/assets/backgrounds/temp1.jpg`

This template (1254x1254, user-provided) is the mandatory background reference for all standalone AI Global posters.

### Poster Prompt Construction

When prompting KIE image-to-image with temp1 as reference:

1. Start prompt with: "Create ONE single 1:1 square poster using the attached reference image as the exact background template. Keep the EXACT same background design, gradient, texture, and layout structure from the reference image. Do NOT change the background — add content ON TOP of the reference background."
2. Add AI Global brand identity: black+gold color scheme, AI Global logo (top), contact "89097454  aiglobal.mn" (bottom)
3. Add data/content sections with clear layout description
4. End with: "Mongolian Cyrillic ONLY. Magazine quality, professional, modern, luxury feel."

### temp1 Poster Content Types

| Type | Prompt Focus |
|------|-------------|
| Salary/Research | Gold title, data sections, statistics in dark boxes |
| Educational | Step-by-step content, icons, learning path |
| Promotional/CTA | Bold headline, offer details, contact info |

### Image Hosting Workaround

When you need a public URL for an image (to upload to KIE or use as API reference), use `litterbox.catbox.moe` (72h expiry):

```bash
curl -s -F "reqtype=fileupload" -F "time=72h" \
  -F "fileToUpload=@path/to/image.jpg" \
  https://litterbox.catbox.moe/resources/internals/api.php
# Returns: https://litter.catbox.moe/xxxxxx.jpg
```

## CRITICAL: No Pillow Compositing

The user explicitly rejected Pillow-composited slides ("huuchin template"). The two-stage approach (KIE background + Pillow overlay) is **DEPRECATED** for this user. Instead:

```
Hermes generates content + uploads reference images to KIE
     then submits gpt-image-2-image-to-image task with input_urls
     then KIE returns complete branded slide (text + photos + layout)
```

See `references/kie-image-to-image-workflow.md` for a full worked example.

## 4-Slide Structure

| Slide | Label | Text Markers | Image Input |
|-------|-------|-------------|-------------|
| 1 | Student Intro | headline, student_name, age, occupation, quote | Student real photo |
| 2 | Before | problem_1, problem_2, problem_3 | KIE generates struggle visual |
| 3 | Transformation | week_1, week_2, week_3 | KIE generates success visual |
| 4 | Results and CTA | metric_1, metric_2, metric_3, cta | KIE generates dashboard visual |

## Workflow: KIE Image-to-Image (Primary, Preferred)

### Step 1: Generate Content

```bash
python3 /opt/data/social-content/brands/ai-global/scripts/generate_success_story.py \
  --student "Батбаатар, 28, мэргэжилтэн" \
  --story "headline|quote|cta|problem1|problem2|problem3|week1|week2|week3|metric1|metric2|metric3" \
  --output ./project/
```

Outputs: `content.json` (marker values), `prompts.json` (slot image prompts)

### Step 2: Upload Reference Images to KIE

Upload the template reference image AND student photo (if real photo exists) to KIE File Storage:

```bash
# Upload template reference
curl -s -X POST 'https://kieai.redpandaai.co/api/file-stream-upload' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -F "file=@assets/references/success-story-template-ref.jpg" \
  -F "uploadPath=images/aiglobal-templates" \
  -F "fileName=template-ref.jpg"

# Upload student photo (if real)
curl -s -X POST 'https://kieai.redpandaai.co/api/file-stream-upload' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -F "file=@student_photo.jpg" \
  -F "uploadPath=images/aiglobal-students" \
  -F "fileName=student.jpg"
```

Response includes `downloadUrl` -- save these for Step 3.

### Step 3: Submit Image-to-Image Task

```python
payload = {
    "model": "gpt-image-2-image-to-image",
    "input": {
        "prompt": "Full slide description with ALL content text embedded...",
        "input_urls": [template_url, photo_url],  # from Step 2
        "aspect_ratio": "1:1"
    }
}
```

POST to `https://api.kie.ai/api/v1/jobs/createTask`

**Prompt construction** -- per slide, the prompt must describe:

- **Format:** "1:1 square social media carousel slide"
- **Brand style:** "Light cream/off-white background (#FAFAF8), Italian minimal aesthetic, gold accent (#D7AB46), charcoal text (#1A1A1A)"
- **Fixed layout:** Top-left gold pill badge, top-right AI Global logo, bottom-left contact, gold bottom divider
- **Slide-specific text:** ALL Mongolian text content embedded at exact layout positions
- **Image placement:** "RIGHT SIDE (38%): Place the attached student photo in a rounded rectangle with thin gold border"
- **Style constraints:** "Mongolian Cyrillic text ONLY. Magazine quality, professional, clean."

**Prompt template for Slide 1** -- Student Introduction:

```
Create ONE separate 1:1 square social media carousel slide.
Use the attached reference image for style guidance.
This is Slide 1 of 4 -- Student Introduction.
Layout: light cream/off-white background, Italian minimal aesthetic, clean airy style.
Top-left: small gold pill badge saying "🏆 Амжилтын түүх".
Top-right: small AI Global luxury logo (black+gold, square, about 15% width).
Bottom-left: gray text "📞 89097454  🌐 aiglobal.mn".
Bottom: thin gold divider line.
LEFT SIDE (55%): Large bold headline "HEADLINE" in dark charcoal, 3 lines max.
Below: student name "NAME" in gold, then age "AGE" in gray, then occupation "OCCUPATION" in gray.
Quote: "QUOTE" in italic gray.
RIGHT SIDE (38%): Place the attached Mongolian man/student photo in a rounded rectangle with thin gold border.
Magazine quality, professional, clean.
Mongolian Cyrillic text ONLY. NO English text.
```

### Step 4: Poll and Download

```python
GET /api/v1/jobs/recordInfo?taskId=<taskId>
# Wait until data.state == "success"
# Parse data.resultJson -- JSON-encoded string -> resultUrls[0]
# Convert via POST /api/v1/common/download-url
# Download final image
```

Observed generation time: ~50-100s per slide.

### Step 5: Repeat for Slides 2-4

For slides without a real student photo (B, C, D), the KIE image-to-image model generates the people/visuals from the prompt description. `input_urls` can contain just the template reference (fewer images = less cost).

## Student Description Format

```
"Тэмүүлэн, 22, оюутан"
"Батбаатар, 28, программист"
"Номин, 20, оюутан, эм"     (add "эм" for female)
```

Fields: `name, age, occupation` (optionally ", эм" for gender)

**Parser pitfall - Mongolian substring collision:**
The parser previously detected "Тэмүүлэн" as female because it contains the substring "эм". This is FIXED -- gender keywords now use whole-word matching only. If the parser fails, manually patch `occupation` in content.json after generation.

## Content Format (pipe-delimited)

Minimal (3 fields): `headline|quote|cta`
Full (12 fields): `headline|quote|cta|problem1|problem2|problem3|week1|week2|week3|metric1|metric2|metric3`

## Credit Cost

| Item | Credits |
|------|---------|
| Per slide (image-to-image) | 1 |
| Total per 4-slide carousel | 4 |

Observed gen time: ~50-100s per slide.

## DEPRECATED: Pillow Compositing Renderer

The Pillow-based compositing system at `templates/aiglobal_success_story_v1/render.py` is **DEPRECATED**. Do NOT use it for new content. It exists only as a reference.

## File Locations

| Component | Path |
|-----------|------|
| Content generator | `scripts/generate_success_story.py` |
| Template schema (reference) | `templates/aiglobal_success_story_v1/template.json` |
| ~~Renderer (DEPRECATED)~~ | ~~`templates/aiglobal_success_story_v1/render.py`~~ |
| ~~Slot image generator (DEPRECATED)~~ | ~~`scripts/generate_slot_images.py`~~ |
| Brand guide | `brand-guide.md` |
| Logo | `assets/logos/logo-ai-global.jpg` |
| Poster background template (temp1) | `assets/backgrounds/temp1.jpg` |
| Reference template image | `assets/references/success-story-template-ref.jpg` |
| Carousel prompt instructions | `carousel-prompt-instructions.md` |

All under: `/opt/data/social-content/brands/ai-global/`

## Hermes Master Instruction

### When the user says "Create a student success story" (carousel):

1. **NEVER** redesign the template
2. **NEVER** use Pillow or local compositing
3. **ONLY** generate marker values + construct full-slide prompts
4. Upload reference template + student photo to KIE file API
5. Submit `gpt-image-2-image-to-image` task with `input_urls`
6. Use template style: **aiglobal_success_story_v1**
7. Test slide 1 first, get approval before doing slides 2-4

### When the user says "Create a poster" (standalone):

1. **Upload temp1** to KIE file storage (assets/backgrounds/temp1.jpg)
2. **Construct prompt** with template preservation directive + AI Global brand identity + content sections + Mongolian language constraint
3. **Submit** `gpt-image-2-image-to-image` task with `input_urls: [temp1_kie_url]`
4. **Poll** every 6s until state=success (~60-90s)
5. **Download** with `curl -L -o output.png "resultUrl"`
6. Send to user for approval

## Pitfalls

1. **No Pillow** -- User explicitly rejected it. KIE image-to-image is the only approved pipeline.
2. **KIE_API_KEY** -- Must be set in shell environment, not available in `execute_code`. Use `terminal` for all KIE calls. Current key: `d1f13da610fc8052e19f6167e79a3c5f`.
3. **SSL verification** -- KIE API calls need `ssl._create_unverified_context()` on this server.
4. **File upload may be restricted** -- KIE file upload endpoints (`/api/file-base64-upload`, `/api/file-stream-upload`) may return 403/404 depending on API key permissions. If upload fails, fall back to GPT Image 2 **text-to-image** (`gpt-image-2-text-to-image`) with a descriptive prompt that replicates the temp1 aesthetic (dark tech background, gold-toned accents) plus all poster content. Or use FFmpeg drawtext as emergency fallback (see Pitfall 16).
5. **input_urls format** -- Requires uploaded URLs (tempfile.aiquickdraw.com). Data URLs (data:image/jpeg;base64,...) cause "File type not supported" errors.
6. **Test one slide first** -- Always generate slide 1, send preview, get approval before slides 2-4.
7. **Mongolian text in prompts** -- The model handles embedded Cyrillic text in JSON prompts. Always QA the output text.
8. **Real student photos** -- If the user provides a real photo, upload it and include in `input_urls`. KIE will place it in the layout.
9. **Never describe templates textually** -- Upload the reference image to KIE file storage first, then pass via `input_urls`. Describing temp1 in text ("dark blue gradient", "modern layout") produces unbranded output the user will reject ("manai branded tohirohgui bna").
10. **temp1 is the only AI Global poster template** -- Do NOT create alternative backgrounds. Always use temp1.jpg as the reference for standalone posters. Located at `/opt/data/social-content/brands/ai-global/assets/backgrounds/temp1.jpg`.
11. **Always specify AI Global brand in prompts** -- When generating a poster with temp1, explicitly include AI Global logo, black+gold color scheme, and contact info in the prompt text. Without this, the output lacks brand identity.
12. **Download URL endpoint may fail** -- `POST /api/v1/common/download-url` can return 422 with "url不能为空". If this happens, try downloading the `resultUrls[0]` URL directly with `curl -L`, which usually works.
13. **KIE download via curl** -- The direct tempfile.aiquickdraw.com URLs often need `-L` (follow redirects) to download successfully. Use `curl -L -o output.png "URL"`.
14. **Generation time** -- Single poster: ~60-90s via poll loop (6s intervals). This is normal for GPT Image 2 image-to-image. GPT Image 2 text-to-image is slower at ~290s.
15. **KIE API model names** -- Use these exact names:
    - Text-to-image: `gpt-image-2-text-to-image` (works, returns `resultUrls`)
    - Image-to-image: `gpt-image/1.5-image-to-image` (needs `input_urls` array, `aspect_ratio` like "1:1", `quality`: "medium"/"high")
    - ElevenLabs TTS: `elevenlabs/text-to-speech-multilingual-v2` (Mongolian via `language_code: "mn"`, returns `resultUrls`)
    - Status check: `GET /api/v1/jobs/recordInfo?taskId=<id>` (returns `data.state`, `data.resultJson`)
16. **FFmpeg drawtext fallback for Cyrillic posters** -- When KIE image-to-image is unavailable, create poster images with FFmpeg drawtext:
    - **CRITICAL: Use `textfile=` not `text='...'`** — Cyrillic text containing colons (`:`) conflicts with FFmpeg's drawtext option separator. Always write Cyrillic text to a `.txt` file and pass via `textfile=/path/to/text.txt`.
    - Font: `/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf` (has good Cyrillic support)
    - Use `-frames:v 1` for single image output, `-i "$BG"` for background
    - Chain multiple drawtext filters with comma separator
    - Box backgrounds: `box=1:boxcolor=black@0.5:boxborderw=10`
    - Color names like `yellow`, `lime`, `aqua`, `hotpink`, `gold` work as shortcut values
    - Output as PNG: large but lossless; or MP4 if video needed
    - Output dimensions default to input; use `scale=1080:1920` for 9:16 video posts
    - Example pattern: `ffmpeg -y -i background.jpg -frames:v 1 -vf "drawtext=textfile=title.txt:fontfile=<font>:fontsize=36:fontcolor=yellow:box=1:boxcolor=black@0.7:x=(w-text_w)/2:y=60,drawtext=textfile=data.txt:fontfile=<font>:fontsize=28:fontcolor=white:x=80:y=350" output.png`
    - **For video reels from static images** (single image → 20s reel with audio + lighting effects), see `references/ffmpeg-reel-from-image.md` for the complete recipe.
17. **Make.com webhook delivery** -- AI Global content is sent to Facebook via Make.com webhook:
    - URL: `https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e`
    - **Always send as multipart form-data**, NOT JSON base64 (payload too large).
    - **MANDATORY: Always include `content_type` argument** — tells Make.com what kind of content it is:
      - **Poster/news poster** → `-F "content_type=poster"`
      - **Reel/video** → `-F "content_type=reel"`
      - **Carousel (4-slide)** → `-F "content_type=carousel"`
    - Example for posters:
      ```bash
      curl -s -X POST "$WEBHOOK_URL" \
        -F "image1=@poster1.jpg;type=image/jpeg" \
        -F "image2=@poster2.jpg;type=image/jpeg" \
        -F "image3=@poster3.jpg;type=image/jpeg" \
        -F "image4=@poster4.jpg;type=image/jpeg" \
        -F "caption1=..." -F "caption2=..." \
        -F "caption3=..." -F "caption4=..." \
        -F "total_posters=4" -F "source=hermes_agent" \
        -F "brand=AI Global" \
        -F "content_type=poster"
      ```
    - Example for reels:
      ```bash
      curl -s -X POST "$WEBHOOK_URL" \
        -F "video=@reel.mp4;type=video/mp4" \
        -F "caption=..." \
        -F "source=hermes_agent" \
        -F "brand=AI Global" \
        -F "content_type=reel"
      ```
    - Make.com accepts 4 posters maximum in one request
    - Response "Accepted" means it was received. Check Facebook to confirm delivery.
    - **Instagram reels need a public video URL, not a file upload.** If Make.com rejects the video file upload with "URL field likely sent a bad or missing video link", upload the mp4 to a hosting service and send `video_url` instead:
      ```bash
      # PREFERRED: Upload to catbox.moe / litterbox (reliable direct URL, 72h expiry)
      VIDEO_URL=$(curl -s -F "reqtype=fileupload" -F "time=72h" \
        -F "fileToUpload=@reel.mp4" \
        https://litterbox.catbox.moe/resources/internals/api.php)
      echo "$VIDEO_URL"

      # FALLBACK: Upload to tmpfiles.org (sometimes fails for Instagram)
      UPLOAD=$(curl -s -F "file=@reel.mp4" https://tmpfiles.org/api/v1/upload)
      VIDEO_URL=$(echo "$UPLOAD" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['url'])")

      # Send URL instead of file
      curl -s -X POST "$WEBHOOK_URL" \
        -F "video_url=$VIDEO_URL" \
        -F "caption=..." \
        -F "source=hermes_agent" \
        -F "brand=AI Global" \
        -F "content_type=reel"
      ```
      - **catbox.moe is preferred** — returns HTTP 200 with proper `video/mp4` content-type; Make.com/Instagram accepts it.
      - **tmpfiles.org fails sometimes** — Make.com may reject its URLs as "bad or missing video link" for Instagram posts.

## Reference Files

- `references/batbaatar-live-run.md` -- Full worked example of the first live run (Batbaatar, May 2026). Contains exact KIE requests, upload commands, polling pattern, and lessons.
- `references/kie-image-to-image-workflow.md` -- Detailed reference for the image-to-image pattern with input_urls, file upload, and prompt construction.
- `references/make-com-webhook-pattern.md` — Multipart form-data delivery protocol for Make.com webhook (AI Global posters → Facebook). Includes single-request (4-in-1) and per-poster patterns.
- `references/temp1-poster-workflow.md` — Exact workflow for creating standalone AI Global posters using temp1.jpg as background reference. Contains prompt templates, polling pattern, and what failed on the first attempt.
- `references/ffmpeg-reel-from-image.md` — Complete recipe for creating short reels from a single static image: Ken Burns zoom, lighting effects, audio overlay, AI Global watermark.
