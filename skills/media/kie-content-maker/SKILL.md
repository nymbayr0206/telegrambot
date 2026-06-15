---
name: kie-content-maker
description: Use when creating social/content assets through KIE.AI APIs, especially Nano Banana 2 posters/images, Veo 3.1 Fast videos, and ElevenLabs TTS/audio. Covers prompt preparation, safe credential handling, task submission, polling, downloads, and packaging outputs for review.
version: 1.5.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [kie-ai, content-generation, posters, video, tts, nano-banana, veo, elevenlabs]
    related_skills: [youtube-content, social-media-automation, baoyu-infographic, popular-web-designs]
---

# KIE Content Maker

## Overview

Use this skill to turn a content request into generated media assets via KIE.AI. The main workflow is:

1. Clarify or infer the asset brief.
2. Build strong prompts/scripts.
3. Submit generation jobs to KIE.AI with `Authorization: Bearer $KIE_API_KEY`.
4. Poll task status until complete.
5. Convert generated KIE URLs to temporary download URLs when needed.
6. *(Optional)* Run automated quality review via OpenAI GPT-4o vision (`scripts/review_image.py`) — catches text errors, logo issues, layout problems before user delivery.
7. Save outputs locally and present paths/links for user review.

Never hardcode the user's API key into files, prompts, logs, skills, or memory. Store it in an environment variable such as `KIE_API_KEY` or a secrets manager. If the key was provided in chat, use it only for the current action and recommend rotating it if it was exposed in an unsafe place.

## Related Skills

- `ai-global-brand-content` — template-driven brand content system for AI Global (industry updates, success stories, tips, course intros, promotions). Generates markers + image prompts, then sends to KIE via text-to-image or image-to-image. Companion reference at `references/full-prompt-pattern-industry-update.md` for the full-prompt text-to-image approach.
- `brand-book-creator` — one-page brand book from a logo: analyzes colors, suggests fonts, generates 3 poster backgrounds (educational, industry leader, sales) via GPT Image 2, composites into one image with Pillow. Same KIE API + GPT Image 2 workflow, different output type.
- `aiglobal-success-story-carousel` — concrete implementation of the template-driven pattern for AI Global. Contains content generator, slot image generator, and Pillow compositing renderer for `aiglobal_success_story_v1`.

## When to Use

Use this skill when the user asks to:

- Build a **template-driven carousel system** where a fixed layout is populated by variable markers + image slots — see `references/template-driven-carousel-architecture.md` and `references/mongolian-content-generator-patterns.md` for content generation patterns.
- Generate posters, ad creatives, thumbnails, social graphics, or product visuals with Nano Banana 2.
- Generate short videos with Veo 3.1, especially `veo3_fast` / Fast-style production.
- Generate narration, voiceover, dialogue, or audio using ElevenLabs models through KIE.AI.
- Build a multi-asset content pack: poster + video + voiceover + caption/script.
- Automate content generation via cron jobs using script-only (no_agent:true) pattern.
- Set up daily carousel automation that generates images and publishes via webhook.

Do not use this skill for:

- Native Hermes `image_generate` requests where the user did not mention KIE.AI.
- Direct ElevenLabs official API work outside KIE.AI.
- Social posting/publishing approval logic by itself; use `social-media-automation` alongside this skill.

## Credential Handling

Preferred setup:

```bash
export KIE_API_KEY='your_key_here'
```

Before using the API in shell commands:

```bash
test -n "$KIE_API_KEY" || { echo 'KIE_API_KEY is not set'; exit 1; }
```

Curl headers:

```bash
-H "Authorization: Bearer $KIE_API_KEY" \
-H "Content-Type: application/json"
```

Do not paste the literal key into reusable scripts, skill files, Git commits, or final answers.

## Core Endpoints

Base URL:

```text
https://api.kie.ai
```

Common job endpoint for marketplace models:

```text
POST /api/v1/jobs/createTask
GET  /api/v1/jobs/recordInfo
```

Veo 3.1 endpoints:

```text
POST /api/v1/veo/generate
GET  /api/v1/veo/record-info
POST /api/v1/veo/get-1080p-video
POST /api/v1/veo/get-4k-video
POST /api/v1/veo/extend
```

Common API:

```text
GET  /api/v1/chat/credit
POST /api/v1/common/download-url
```

Download URLs are temporary; KIE docs note generated download links may expire quickly, so download/cache outputs promptly.

## GPT Image 2 Image-to-Image Through KIE

Use the marketplace endpoint `POST /api/v1/jobs/createTask` with model `gpt-image-2-image-to-image` when you need to send reference images for consistent layout, brand style, or real portrait photos.

This model accepts `input_urls` — a list of image URLs that the model sees as visual context.

### Request Shape

```json
{
  "model": "gpt-image-2-image-to-image",
  "input": {
    "prompt": "Full slide description with ALL text content embedded at layout positions...",
    "input_urls": [
      "https://tempfile.redpandaai.co/kieai/.../template-ref.jpg",
      "https://tempfile.redpandaai.co/kieai/.../student-photo.jpg"
    ],
    "aspect_ratio": "1:1"
  }
}
```

### Step 1: Upload Images to KIE File Storage

Before using `input_urls`, upload images via the file stream upload endpoint (NOT the same domain as the API):

```bash
curl -s -X POST 'https://kieai.redpandaai.co/api/file-stream-upload' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -F "file=@/path/to/image.jpg" \
  -F "uploadPath=images/brand-name" \
  -F "fileName=descriptive-name.jpg"
```

Response:
```json
{
  "success": true,
  "data": {
    "fileName": "template-ref.jpg",
    "downloadUrl": "https://tempfile.redpandaai.co/kieai/.../template-ref.jpg",
    "fileSize": 210150,
    "mimeType": "image/jpeg"
  }
}
```

Save the `downloadUrl` — it goes into `input_urls` in Step 2.

### Step 2: Submit Image-to-Image Task

- Polling endpoint: same `GET /api/v1/jobs/recordInfo?taskId=<id>`
- Response parsing: same as text-to-image (data.state, data.resultJson)
- Observed generation time: ~50-100s per slide (often faster than text-to-image)

### Prompt Construction for Image-to-Image

The prompt must be fully self-contained with ALL text content. The model places the input images (at `input_urls`) into the layout based on your description.

Structure:
- **Format** declaration: "1:1 square social media carousel slide"
- **Reference instruction**: "Use the attached reference image for style guidance"
- **Slide label**: "Slide 1 of 4 - Student Introduction"
- **Brand style**: Light cream background, gold accents, charcoal text, Italian minimal aesthetic
- **Fixed layout**: Top-left badge, top-right logo, bottom-left contact, bottom gold divider
- **Per-slide text**: ALL Mongolian Cyrillic content at exact layout positions
- **Image placement**: "RIGHT SIDE (38%): Place the attached photo in a rounded rectangle with thin gold border"
- **Constraints**: "Mongolian Cyrillic text ONLY. Magazine quality, professional, clean."

### Example (Slide 1 — Student Intro)

```
Create ONE separate 1:1 square social media carousel slide.
Use the attached reference image for style guidance.
This is Slide 1 of 4 — Student Introduction.
Layout: light cream/off-white background, Italian minimal aesthetic, clean airy style.
Top-left: small gold pill badge saying "🏆 Амжилтын түүх".
Top-right: small AI Global luxury logo (black+gold, square, about 15% width).
Bottom-left: gray text "📞 89097454  🌐 aiglobal.mn".
Bottom: thin gold divider line.
LEFT SIDE (55%): Large bold headline "AI-г ойлгодоггүй байсан хүн agent бүтээсэн" in dark charcoal, 3 lines max.
Below: student name "Батбаатар" in gold, then age "28" in gray, then occupation "IT-ийн мэргэжилтэн" in gray.
Quote: "Би өмнө нь AI-г огт ойлгодоггүй байсан" in italic gray.
RIGHT SIDE (38%): Place the attached Mongolian man photo in a rounded rectangle with thin gold border.
Magazine quality, professional, clean.
Mongolian Cyrillic text ONLY. NO English text.
```

### When to Use Image-to-Image vs Text-to-Image

| Use Case | Model | Why |
|----------|-------|------|
| Consistent branded template with real photos | `gpt-image-2-image-to-image` | Reference template + real photo as input |
| No reference image needed | `gpt-image-2-text-to-image` | Text-only, simpler |
| User rejected Pillow compositing | `gpt-image-2-image-to-image` | Everything through KIE |
| Industry updates with no real photos | `gpt-image-2-text-to-image` | Pure text content |

### Multi-Image Image-to-Image via tmpfiles.org or catbox.moe (Bypassing KIE Upload)

KIE's file upload endpoint (`/api/file-stream-upload`) may be unreachable (403/404) from this server. Use **tmpfiles.org** or **catbox.moe** as free image hosting intermediaries instead:

#### Option A: tmpfiles.org (no expiry known, but may be unreliable)

1. Upload images via `curl -s -F "file=@/path/to/image.jpg" https://tmpfiles.org/api/v1/upload`
2. Extract the public URL from response JSON: `data.url` (format: `https://tmpfiles.org/wXXXXXXX/filename.jpg`). KIE's `gpt-image-2-image-to-image` accepts this URL format **directly** in `input_urls` — no need to convert to `/dl/XXXXXXX/filename.jpg`. Both formats work, but the upload URL is simpler to derive.
3. Verify the URL returns HTTP 200: `curl -s -o /dev/null -w "%{http_code}" 'https://tmpfiles.org/wXXXXXXX/filename.jpg'`
4. Pass ALL image URLs in `input_urls` array to gpt-image-2-image-to-image

**Critical pattern — Real person photos in branded posters:**

When the user provides an actual photo of a specific person (instructor, student, spokesperson) and says "use this image as [person's name]":

1. Upload BOTH the brand template AND the person's photo to tmpfiles.org
2. Use `gpt-image-2-image-to-image` with both URLs in `input_urls: [template_url, person_photo_url]`
3. In the prompt, explicitly state: "Place the person photo from the second image as the instructor portrait" — otherwise the AI generates a random face instead of using the real photo
4. Describe the exact layout position (circular frame, left side, etc.) for the real photo

**Example prompt addition for real photo placement:**
```
"Use the dark background from the first image (template). Place the person photo from the second image in a professional circular portrait frame on the left side. Use the person's ACTUAL face as the instructor photo."
```

**Verification:** The AI may composite faces poorly or ignore the real photo entirely — always verify the output has the correct person's face. If the AI generated a random face instead, resubmit with stronger explicit placement instructions.

#### Option B: catbox.moe (72h expiry, more reliable for this server)

```bash
curl -s -F "reqtype=fileupload" -F "time=72h" \
  -F "fileToUpload=@/path/to/image.jpg" \
  https://litterbox.catbox.moe/resources/internals/api.php
# Returns: https://litter.catbox.moe/xxxxxx.jpg
```

- **72-hour expiry** — URLs must be re-uploaded before each session if >3 days old
- **100% reliable** for this server (tested June 5, 2026 on multiple uploads)
- **KIE accepts directly** in `input_urls` — no conversion needed
- **Check before use:** `curl -s -o /dev/null -w "%{http_code}" "URL"` — if not 200, re-upload

## GPT Image 2 Text-to-Image Through KIE

Use the marketplace endpoint `POST /api/v1/jobs/createTask` with model `gpt-image-2-text-to-image`.

Minimal request (no `callBackUrl` required — polling works without it):

```json
{
  "model": "gpt-image-2-text-to-image",
  "input": {
    "prompt": "Create ONE separate 1:1 square social media carousel slide..."
  }
}
```

Observed generation time: highly variable — ~2-5 minutes per slide (12-30 polls x 10s interval). One observed run took 29 polls (~290s). Set 30+ polls minimum. Each slide generates independently. For a 4-slide carousel, generate and poll sequentially (not parallel) to avoid rate limits — total ~8-20 minutes.

**Faster observed times for simpler prompts:** When generating photorealistic scenes (not branded carousel slides with embedded text), GPT Image 2 can complete in ~80-110 seconds (8-12 polls x 10s). The simpler the prompt, the faster the generation.

### Retry Pattern for "Internal Error" Failures

GPT Image 2 is prone to non-deterministic `"failCode": "500", "failMsg": "Internal Error, Please try again later."` failures. This appears to be a server-side transient — the exact same prompt may succeed on retry. However, some prompts consistently fail regardless of retries.

**Pattern for retrying:**

1. After a `"fail"` state with `"Internal Error"`, immediately submit a new task with a **simplified prompt** — shorter description, fewer constraints, no aspect_ratio if possible (defaults seem to work better)
2. The original prompt's failure is often prompt-specific (maybe content policy or complexity threshold). Change the subject matter significantly when retrying.
3. Observed success rate: ~50-75% on first try for simpler scenes (photorealistic portrait, abstract tech) vs ~25% for complex multi-element prompts
4. For a 4-image set, budget for 5-6 submission attempts total to account for ~1-2 failures

**Working example (failed → retried):**
- ❌ Failed: `"Futuristic city skyline at night with neon lights and AI data streams, cinematic wide shot transformed to 9:16 vertical, cyberpunk aesthetic"`
- ✅ Succeeded: `"Abstract technology background with glowing digital network connections, blue and gold data flow, modern tech aesthetic, 9:16 vertical, high quality"`

Add `callBackUrl` only if you want asynchronous delivery; without it, polling `/api/v1/jobs/recordInfo` works identically.

For carousel publishing workflows, generate and send four **separate** slide images rather than an all-in-one contact sheet. Still QA every Mongolian/Cyrillic word before publishing (see Pitfall 11).

### Full-Prompt Template Pattern (Text-to-Image)

When no dedicated KIE template endpoint exists, write a **single comprehensive prompt** that embeds the template layout description + all text markers + hero visual description. This is distinct from image-to-image (which uses reference photos) — pure text-to-image with structured layout instructions.

**Trigger:** User says "pass everything to KIE" or "use full prompt" for a branded slide.

**Prompt structure:**
```
Create a ONE single 1:1 square social media carousel slide poster for [BRAND].

THEME: [CONTENT TOPIC]

BRAND STYLE:
- Background: [COLOR], [STYLE DESCRIPTION]
- Typography: [FONT], [TEXT COLOR], [ACCENT COLOR]
- Style: Premium, modern, educational

LAYOUT (top to bottom):
- TOP-LEFT: [BADGE]
- TOP-RIGHT: [LOGO]
- HEADLINE: "[TEXT]"
- SUBHEADLINE: "[TEXT]"
- TRENDS/VISUALS...
- FOOTER: [DIVIDER / CONTACT]
- CTA: "[TEXT]"
```

For Mongolian text, use **latin transliteration** in JSON — handles better than raw Cyrillic. Write prompt to a JSON file and submit via `curl -d @file.json` to avoid shell UTF-8 mangling.

**Observed generation time:** ~290 seconds (29 polls x 10s), not the ~2 minutes previously documented. Set 30+ polls minimum.

**Working example:** `ai-global-brand-content` skill → `references/full-prompt-pattern-industry-update.md` — contains the exact prompt template and real markers from a production run (May 31, 2026).

#### User-Provided Template: Describe in Prompt, Don't Pillow-Composite

When the user says "I have a background template, use this for posters" and sends a JPEG/PNG, the correct approach for AI Global (who rejected Pillow compositing) is:

1. Save the user's template to `assets/backgrounds/<name>.jpg` in the brand directory
2. Study the file's dimensions and dominant colors (use terminal + Python struct to parse JPEG header since DeepSeek has no vision)
3. Write a **detailed text-to-image prompt** that describes the template style: colors, layout zones, card elements, shadows, footer bars, typography feel
4. Use `gpt-image-2-text-to-image` with `aspect_ratio` matching the template's aspect ratio
5. Do NOT use image-to-image (requires uploading to KIE file storage). Do NOT use Pillow compositing (user rejected it).

This approach produced a working poster for AI Global with "temp1.jpg" (1254x1254, black+gold+professional layout). The poster was generated as a single KIE task and included salary infographic data, certification badges, and brand contact info.

**When to use vs image-to-image:**
| Approach | When | Model |
|----------|------|-------|
| Full-prompt text-to-image | Layout + text, no real photo references needed | `gpt-image-2-text-to-image` |
| Image-to-image | Need real photos (student face, product) as input | `gpt-image-2-image-to-image` |
| Two-stage (background + Pillow) | User explicitly wants deterministic text/logo overlay | Deprecated for AI Global |

Use `POST /api/v1/jobs/createTask` with model `nano-banana-2`.

For this user, when creating branded carousel posters where the reference style/font/phone-frame/logo-placement matters, default to KIE GPT Image 2 with model `gpt-image-2-text-to-image` instead of Nano Banana + local font overlay. Generate each carousel slide as a separate image/task unless the user explicitly asks for a contact sheet. QA Mongolian/Cyrillic spelling, logo, and phone number before sending or posting.

For GPT Image 2 poster/carousel generation through KIE, use `model: "gpt-image-2-text-to-image"` on the same marketplace jobs endpoint; see `references/kie-gpt-image-2-notes.md`. GPT Image 2 is useful when the user wants the full poster—including rounded-bold typography, phone frames, logo cards, and wave/footer styling—to match a reference image more closely than local font overlay can. For carousel publishing workflows, generate and send four **separate** slide images rather than an all-in-one contact sheet. Still QA every Mongolian/Cyrillic word before publishing.

For Mongolian-language posters, prefer a two-stage workflow: generate a text-free image/background first, then render all Mongolian/Cyrillic copy locally with Pillow, SVG, or HTML/CSS. Image models frequently misspell non-English text, and deterministic overlay makes the final asset reviewable and editable. See `references/mongolian-poster-text-overlay.md`.

### Aspect Ratio: Nano Banana 2 vs GPT Image 2

Nano Banana 2 **does not reliably respect aspect ratio prompts**. Even with explicit "9:16 portrait" or "720x1280" in the prompt, it returns 1:1 square images (1024x1024) or variable sizes. This was confirmed across 8+ submissions with this user's workflow.

GPT Image 2 (`gpt-image-2-text-to-image`) **does respect** the `"aspect_ratio"` parameter when included in `input`:

```json
{
  "model": "gpt-image-2-text-to-image",
  "input": {
    "prompt": "Photorealistic scene description...",
    "aspect_ratio": "9:16"
  }
}
```

Confirmed working aspect ratios:
- `"1:1"` — square (default)
- `"9:16"` — vertical (Instagram Reels, TikTok, social video)
- `"16:9"` — landscape (YouTube)

However, GPT Image 2 has a higher failure rate (~25-50% Internal Error 500) for complex scene prompts. For a 4-image set, budget for retries. Simpler prompts succeed more reliably.

**Decision tree for image generation:**
| Need | Use | Why |
|------|-----|-----|
| 1:1 square photorealistic | Nano Banana 2 | More reliable, faster, fewer Internal Errors |
| 9:16 vertical photorealistic | GPT Image 2 with `aspect_ratio: "9:16"` | Nano Banana 2 doesn't reliably produce this ratio |
| Branded carousel with text | GPT Image 2 text-to-image or image-to-image | Better for text placement |

Minimal request pattern:

```bash
curl --location 'https://api.kie.ai/api/v1/jobs/createTask' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H 'Content-Type: application/json' \
  --data '{
    "model": "nano-banana-2",
    "callBackUrl": "https://your-domain.com/api/callback",
    "input": {
      "prompt": "Create a cinematic poster ..."
    }
  }'
```

Prompt checklist for posters:

- State exact format: poster, thumbnail, product ad, event flyer, Instagram square, vertical story, etc.
- Include subject, setting, mood, color palette, lighting, typography instructions, and composition.
- If text must appear in the image, quote it exactly and keep it short.
- Specify brand constraints: logo placement, colors, avoid clutter, premium/minimal/playful style.
- Add negative constraints: no misspelled text, no extra logos, no distorted hands/faces, no watermark.
- If the user requires Mongolian text, strongly prefer `NO TEXT / NO LETTERS` in the generation prompt and add the Mongolian copy as a deterministic overlay afterward.
- If humans appear for this user's Mongolian audience, explicitly request Mongolian-looking / Ulaanbaatar-context people and verify the result visually.

## Veo 3.1 Fast Video Workflow

Use KIE's Veo 3.1 generation API for text-to-video, image-to-video, or reference/material based generation. For people-led social ads, especially when the user cares about the actor/model, environment, and first-two-second hook, first generate a still concept frame for approval before spending Veo credits. The still should lock the spokesperson look, setting, lighting, brand colors, and emotional contrast; then write the Veo prompt from the approved still. For multi-part continuation videos, generate sequentially and save each task/seed/reference id; pass Generation 1 into Generation 2, and Generation 2 into Generation 3 to preserve the same person/location.

Docs describe three modes:

- `TEXT_2_VIDEO` — text prompt only.
- `FIRST_AND_LAST_FRAMES_2_VIDEO` — transition video using one or two image frames.
- `REFERENCE_2_VIDEO` — material/reference-image driven video; docs note this is Fast-model oriented and supports 16:9 and 9:16.

Generation request pattern:

```bash
curl --location 'https://api.kie.ai/api/v1/veo/generate' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H 'Content-Type: application/json' \
  --data '{
    "prompt": "A dynamic 8-second product reveal video ...",
    "model": "veo3_fast",
    "aspectRatio": "9:16",
    "callBackUrl": "https://your-domain.com/api/callback"
  }'
```

Parameter names can vary by KIE docs/model version. If a request fails validation, inspect the latest docs or API error and adjust body keys rather than assuming the model is unavailable.

Video prompt checklist:

- Duration target and platform: TikTok/Reels/YouTube Shorts/ad bumper.
- Camera movement: push-in, pan, orbit, handheld, drone, macro, dolly zoom.
- Visual sequence: beginning, middle, end.
- Subject action and environment.
- Brand/product placement.
- Aspect ratio: 9:16 for vertical social, 16:9 for YouTube/landscape.
- Audio expectation: generated video may include audio; if separate narration is needed, generate TTS and combine later with a video editor/ffmpeg.

## ElevenLabs TTS via KIE Workflow

Use `POST /api/v1/jobs/createTask` with an ElevenLabs model.

### Model Input: Two Different Payload Formats

Two different ElevenLabs models exist on KIE's marketplace, each with a different input format. Use the right one based on which model you're calling:

#### Format A: Simple TTS (`text` + `voice` — for turbo-2.5 and multilingual-v2)

Models: `elevenlabs/text-to-speech-turbo-2-5`, `elevenlabs/text-to-speech-multilingual-v2`

```json
{
  "model": "elevenlabs/text-to-speech-turbo-2-5",
  "callBackUrl": "https://your-domain.com/api/callback",
  "input": {
    "text": "Unlock powerful API with KIE.AI! ...",
    "voice": "Rachel"
  }
}
```

#### Format B: Dialogue Array (`dialogue[]` — for text-to-dialogue-v3)

Model: `elevenlabs/text-to-dialogue-v3`

This model uses a **dialogue array** instead of a single text field. Each entry in the array can have its own voice, enabling multi-speaker dialogue. For single-speaker, use an array with one object.

```json
{
  "model": "elevenlabs/text-to-dialogue-v3",
  "input": {
    "dialogue": [
      {
        "text": "Text to speak...",
        "voice": "Lily"
      }
    ],
    "stability": 0.5
  }
}
```

Parameters:
- `dialogue[]` — array of speech segments. Each segment has `text` (string) and `voice` (string — voice NAME, not voice ID)
- `stability` — float, 0.0 to 1.0. Lower values = more expressive, higher = more stable/consistent. 0.5 is a good default.

**Voice support for dialogue-v3 — full scan (June 2026):**

| Voice | Gender | Status |
|-------|--------|--------|
| `Lily` | Female | ✅ Works |
| `Sarah` | Female | ✅ Works |
| `Alice` | Female | ✅ Works |
| `Callum` | Male | ✅ Works |
| `Daniel` | Male | ✅ Works |
| `Liam` | Male | ✅ Works |
| `Antoni` | Male | ❌ Not supported |
| `Sam` | Male | ❌ Not supported |
| `Adam` | Male | ❌ Not supported |
| `Patrick` | Male | ❌ Not supported |
| `Thomas` | Male | ❌ Not supported |
| `Michael` | Male | ❌ Not supported |
| `Oliver` | Male | ❌ Not supported |
| `Ethan` | Male | ❌ Not supported |
| `Henry` | Male | ❌ Not supported |
| `Jack` | Male | ❌ Not supported |
| `Noah` | Male | ❌ Not supported |
| `James` | Male | ❌ Not supported |
| `Benjamin` | Male | ❌ Not supported |
| `Lucas` | Male | ❌ Not supported |
| `William` | Male | ❌ Not supported |
| `Mason` | Male | ❌ Not supported |
| `Elijah` | Male | ❌ Not supported |
| `Alexander` | Male | ❌ Not supported |
| `Rachel` | Female | ❌ Not supported |
| `Arabella` | Female | ❌ Not supported |
| UUID formats (e.g. `"21m00Tcm4TlvDq8ikWAM"`) | — | ❌ Not accepted |

Tested via KIE marketplace endpoint `POST /api/v1/jobs/createTask` with model `elevenlabs/text-to-speech-turbo-2-5` and single-`text` payload — voice rejection was immediate (HTTP 422/500, not a generation-time bug). Dialogue-v3 uses the same voice pool — confirmed with `Callum` working in multi-turn dialogue.

**Emotion tags work in dialogue-v3:** `[excited]`, `[happy]`, `[sad]`, `[whisper]` — wrap text parts to shift delivery.

**Mongolian Cyrillic works** in the `text` field. Emotion tags like `[excited]` work with Mongolian text.

#### Common to both formats: Voice = NAME, not UUID

KIE's ElevenLabs integration selects the voice via the **voice name** string, NOT the ElevenLabs voice ID:
- `"voice": "Rachel"` ✅
- `"voiceId": "21m00Tcm4TlvDq8ikWAM"` ❌

### Available Models

| Model | Input Format | Notes |
|-------|-------------|-------|
| `elevenlabs/text-to-speech-turbo-2-5` | Format A (text+voice) | ✅ Fast, reliable, tested |
| `elevenlabs/text-to-speech-multilingual-v2` | Format A (text+voice) | ✅ Multilingual, Mongolian support |
| `elevenlabs/text-to-dialogue-v3` | Format B (dialogue[]) | The "V3" model the user refers to. Requires dialogue[] array — see Format B. ⚠️ Frequently gets stuck in "waiting" state (server-side queue congestion on KIE). Fall back to turbo-2.5 or multilingual-v2 if V3 doesn't advance. |

⚠️ **Key difference:** Do NOT use Format A (text+voice) with dialogue-v3 — it returns HTTP 500. Do NOT use Format B (dialogue[]) with the other models — they return `voiceId cannot be empty` or similar. Always match the format to the model.

#### Language Code Support

For multilingual TTS, the `language_code` parameter in `input` works with ISO 639-1 codes:
- `"language_code": "mn"` — Mongolian Cyrillic TTS (user's preferred use case)
- Omit or set `""` for auto-detection

#### Observed Timing

- Submit task: < 1s
- Generation + polling: ~90s (18 polls × 5s) for the `turbo-2-5` model
- Set command provider timeout to 180s to be safe

#### Integration as Hermes Command TTS Provider

To use KIE ElevenLabs TTS as Hermes' native `text_to_speech` tool output, configure a command-type TTS provider in `config.yaml`. Requires a Python wrapper script that reads text from a temp file, submits to KIE, polls, and downloads.

**Config snippet (`tts` section of config.yaml) — V3 Dialogue model (preferred):**
```yaml
tts:
  provider: kie-elevenlabs
  providers:
    kie-elevenlabs:
      type: command
      command: python3 /opt/data/scripts/kie_elevenlabs_tts.py "{input_path}" "{output_path}" "{voice}" "{model}"
      voice: Lily
      model: elevenlabs/text-to-dialogue-v3
      format: mp3
      voice_compatible: true
      max_text_length: 40000
      timeout: 180
```

**Alternative config — Simple TTS (turbo-2.5 / multilingual-v2):**
```yaml
tts:
  provider: kie-elevenlabs
  providers:
    kie-elevenlabs:
      type: command
      command: python3 /opt/data/scripts/kie_elevenlabs_tts.py "{input_path}" "{output_path}" "{voice}" "{model}"
      voice: Rachel
      model: elevenlabs/text-to-speech-turbo-2-5
      format: mp3
      voice_compatible: true
      max_text_length: 40000
      timeout: 180
```

The placeholder template receives: `{input_path}` (text file), `{output_path}` (where to write audio), `{voice}` (from config), `{model}` (from config).

**Wrapper script** (`kie_elevenlabs_tts.py`):
- Reads text from `{input_path}`
- Builds payload: `{"model": model, "input": {"text": text, "voice": voice}}`
- Submits to `POST /api/v1/jobs/createTask`
- Polls `GET /api/v1/jobs/recordInfo` every 3s for up to 60 attempts
- On success, converts KIE temp URL to signed download via `POST /api/v1/common/download-url`
- Downloads audio to `{output_path}`

**SSL note for this server:** Use `ssl._create_unverified_context()` in the wrapper script for `urllib.request.urlopen` calls — the server's SSL certificates trigger errors with the default context.

⚠️ **KIE TTS queue congestion: ALL models share the same backend queue.** Tasks for any ElevenLabs model (dialogue-v3, turbo-2.5, multilingual-v2) submit successfully (code 200, credits deducted) but can freeze in "waiting" for 30-55+ polls (~90-165s) then transition to "fail". This is a server-side KIE queue issue, not a payload problem — no config change helps. When stuck, fall back to edge-tts Python package (see Pitfall 22). The `kie_elevenlabs_tts.py` wrapper handles all three model formats; just switch `model` and `voice` in config.yaml and retry later.

TTS script checklist:

- Keep social ads concise: 10-30 seconds unless user asks longer.
- Write in the user's requested language; for this user, Mongolian is often preferred when the target audience is Mongolian.
- Include pronunciation hints only if the model supports them or if text spelling helps.
- Avoid huge paragraphs; split into short spoken beats.
- **ElevenLabs emotion tags work through KIE**: wrap parts of the text in `[excited]`, `[happy]`, `[sad]`, `[whisper]`, `[angry]` brackets to shift delivery. Works with `elevenlabs/text-to-speech-multilingual-v2` and `elevenlabs/text-to-speech-turbo-2-5` via KIE. Example: `[excited] Сайн уу! Шинэ мэдээ танилцуулж байна!`
- Generate captions/subtitles from the final script when packaging content.

### TTS Script Dual-Format Handling

The wrapper script at `scripts/kie_elevenlabs_tts.py` handles BOTH payload formats dynamically based on the model name:

- **Format A (turbo-2.5, multilingual-v2):** `{"model": model, "input": {"text": text, "voice": voice}}`
- **Format B (dialogue-v3):** `{"model": model, "input": {"dialogue": [{"text": text, "voice": voice}], "stability": 0.5}}`

The script currently uses Format B (dialogue[]) which works for ALL three models. The config.yaml sets `model: elevenlabs/text-to-dialogue-v3` and `voice: Lily`. If switching to turbo-2.5 or multilingual-v2, update config.yaml to use a Format A-capable model name AND update the script's payload to Format A, or keep Format B which may also work (needs testing per model).

## Polling and Download Pattern

For marketplace jobs, submit to `createTask`, extract the task/job id from the response, then poll `GET /api/v1/jobs/recordInfo` or the model-specific record endpoint until completion.

Nano Banana 2 / marketplace record responses may report `data.state: "success"` while the actual output URL is stored as a JSON-encoded string in `data.resultJson` (for example `{"resultUrls":["https://..."]}`). Do not stop just because a simple recursive URL regex finds nothing in the outer JSON; explicitly parse `resultJson` when present, then download the first `resultUrls` item. If the final poster needs reliable non-English typography, generate the visual with **no text** and overlay the exact localized text locally using a font that supports the language.

For Veo 3.1, docs describe status values on `successFlag`:

- `0` — generating.
- `1` — success.
- `2` — failed before completion.
- `3` — generation failed after task creation/upstream failure.

Observed Veo 3.1 Fast success records can put the final MP4 URL under `data.response.resultUrls[0]`, with audio and continuity metadata under `data.response.hasAudioList[0]` and `data.response.seeds[0]`. When a request used reference `imageUrls`, do not download the first URL found anywhere in the record because it may be the input PNG/reference image; prefer `data.response.resultUrls[0]` and verify the saved file is an MP4 (`ftyp`, `ffprobe`) before sending to the user. See `references/kie-veo31-fast-continuation-and-downloads.md` for the full pattern.

Polling pattern:

```bash
# Pseudocode; adapt id field names to response body.
TASK_ID='...'
for i in $(seq 1 60); do
  curl -sS 'https://api.kie.ai/api/v1/jobs/recordInfo?taskId='"$TASK_ID" \
    -H "Authorization: Bearer $KIE_API_KEY"
  sleep 10
done
```

If the API returns a KIE-hosted file URL that needs conversion, use:

```bash
curl --location 'https://api.kie.ai/api/v1/common/download-url' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H 'Content-Type: application/json' \
  --data '{"url":"https://...generated-file..."}'
```

Then immediately download the temporary URL to local storage.

**CRITICAL: download-url response shape.** The endpoint returns `{"code":200, "msg":"success", "data":"https://..."}` where `data` is a **string** (the signed temporary download URL), **not** an object. Incorrect parsing (e.g. `data.get("downloadUrl", "")` on `body["data"]`) will silently yield `None` or an AttributeError, and the direct KIE tempfile URL will return HTTP 403 when accessed without the signed query parameters.

**Correct Python parsing:**

```python
# download-url response: {"code":200, "msg":"success", "data":"https://signed-url..."}
resp = urllib.request.urlopen(req, context=ctx, timeout=60)
body = json.loads(resp.read().decode("utf-8"))
signed_url = body["data"]  # <-- "data" is a string (the download URL), not a dict
assert isinstance(signed_url, str) and signed_url.startswith("http")
```

**Correct recordInfo response parsing (for GPT Image 2 / marketplace models):**

The `data.resultJson` field is a **JSON-encoded string** containing `{"resultUrls":["https://..."]}`, not a dict. Parse it explicitly:

```python
record = json.loads(poll_response_body)
result_json_raw = record.get("data", {}).get("resultJson", "{}")
if isinstance(result_json_raw, str):
    result_data = json.loads(result_json_raw)  # string → dict
else:
    result_data = result_json_raw
kie_url = result_data.get("resultUrls", [])[0]  # the KIE tempfile URL
```

**Correct polling response parsing (createTask/recordInfo):**

For marketplace models (Nano Banana 2, GPT Image 2), the record response has:
- `data.state` — `"generating"` / `"success"` / `"failed"`
- `data.resultJson` — a **JSON-encoded string** containing `{"resultUrls": ["https://..."]}`, not a dict

```python
record = poll_result  # dict from json.loads
result_json_raw = record.get("data", {}).get("resultJson", "{}")
if isinstance(result_json_raw, str):
    result_data = json.loads(result_json_raw)
else:
    result_data = result_json_raw
result_urls = result_data.get("resultUrls", [])
kie_url = result_urls[0]  # the KIE tempfile URL
# Then convert via /api/v1/common/download-url as above
```

## Automated Cron Job Generation (no_agent: True)

When KIE.AI is used inside a `no_agent: true` cron job script (pure Python, no LLM), see the full reference at `references/kie-cron-auto-carousel-pattern.md`.

### Architecture Choice

Two cron job architectures exist for brand carousel autopost:

| Pattern | How | When |
|---|---|---|
| **LLM-driven** | Hermes agent generates images via `image_generate()` tool, then script sends to webhook | Need agent reasoning, flexible topic extraction, variable slide design |
| **Script-only (no_agent:true)** | Pure Python script calls KIE API directly for all 4 slides, polls, downloads, then sends to Make.com | Deterministic, no LLM tokens, simpler failure recovery, faster iteration |

Cron config for script-only:
```yaml
script: "brand_daily_carousel.py"   # bare filename in ~/.hermes/scripts/
no_agent: true
enabled_toolsets: ["terminal"]
```

### ⚠️ Critical: Brand Assets via Deterministic Overlay, Not Prompt

**Never trust GPT Image 2 prompts to reproduce actual brand logos, colors, or designed elements.** Even with detailed hex codes and descriptions, the model invents its own logo and picks random brand-adjacent colors.

**The correct approach is two-stage:**
1. **Stage 1 — Background image** generated via KIE (GPT Image 2 or Nano Banana 2) with `NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS`
2. **Stage 2 — Pillow compositing** that overlays the actual brand logo PNG, exact brand color hex codes, fixed text elements (title, phone, slide numbers), and designed frames/ribbons/capsules

See `references/kie-cron-auto-carousel-pattern.md` sections 7-10 for the full dual-stage pattern, Pillow compositing code, and prompt template for background-only generation.

## Multi-Asset Content Pack Recipe

For a campaign request like "make content for this product":

1. Draft a concise creative brief:
   - Target audience.
   - Offer/CTA.
   - Tone.
   - Platform and aspect ratios.
   - Required language.
2. Write the poster prompt for Nano Banana 2.
3. Write the video prompt for Veo 3.1 Fast.
4. Write a 10-30 second voiceover script.
5. Generate poster/image first; use it as a visual reference for video if suitable.
6. Generate video.
7. Generate TTS.
8. Save all outputs under a dated project directory.
9. Provide the user a compact review package: file paths, scripts, prompts used, and recommended caption/hashtags.
10. If publishing is requested, switch to approval-first social automation: preview first, publish only after explicit approval.

#### Reel/Video Frame Approval Workflow

**This user requires frame-by-frame approval BEFORE any generation.** Do NOT generate any images or video clips until the visual storyboard is approved.

**Correct flow:**
1. ✅ Draft the reel concept: target audience, key message, CTA
2. ✅ Write the frame-by-frame storyboard: describe EACH frame as a visual description + text overlay + estimated duration
3. ✅ Present as a table: Frame # | Type | Visual Description | Text/Overlay | Duration
4. ✅ **WAIT for user approval** before submitting any KIE generation jobs
5. ✅ Only after approval: generate frames (images at 9:16 via GPT Image 2), then TTS, then ffmpeg composite
6. ✅ Add brand watermark overlay at top-right, 1/10th video width (see watermark section below)
7. ✅ Preview composite and get final approval before publishing

**Do NOT default to Veo 3.1** — this user has explicitly said "Veo 3.1 aшиглахгүй" (don't use Veo 3.1). They prefer:
- **Images** generated as 9:16 via GPT Image 2 with `aspect_ratio: "9:16"`
- **ElevenLabs TTS** for voiceover (V3 dialogue model with Lily voice for Mongolian)
- **FFmpeg composite** to assemble images + TTS + watermark + captions

### Watermark Overlay for Brand Videos

For this user's brand videos (AI Global, Postly, etc.), add the brand watermark logo at:
- **Position:** Top-right corner
- **Size:** 1/10th of video width (e.g. 108px for 1080px-wide video, computed as `iw/10`)
- **Padding:** 20px from right and top edges
- **FFmpeg filter:** `[1:v]scale='iw/10':-1[logo];[0:v][logo]overlay=W-w-20:20`
- **Tool:** `scripts/add_ai_global_watermark.py` (generic — copy and adapt for each brand)

Brand watermark files are stored at each brand's `assets/logos/watermark-*.png` or can be generated from the main logo. Verify the file exists before running the composite command.

### Reel/Video Last Frame: Silent CTA

This user's preferred reel structure ends with a **silent CTA frame** — no voiceover on the last frame. Text-only overlay:
- "Дэлгэрэнгүй мэдээлэл авах бол comment үлдээгээрэй"
- Contact info: website + phone

For the TTS, generate audio only for frames 1 through N-1 (where N is the last frame). The last frame uses only visual text overlay timed to ~5 seconds.

### Images-as-B-Roll Social Video Ads

When the user wants a **social video ad** (Reels/Shorts) but prefers **images as B-roll** instead of Veo-generated video clips (or has explicitly rejected Veo):

1. **Generate 4 text-free photorealistic images** via KIE (Nano Banana 2 is more reliable than GPT Image 2 for photoreal 9:16 scenes — GPT Image 2 may return 500 Internal Error)
2. **Generate voiceover** — For Mongolian, use edge-tts Python package with voice `mn-MN-YesuiNeural` (Hermes `text_to_speech` edge provider fails for Mongolian Cyrillic). For English, use KIE ElevenLabs with `"voice": "Rachel"`.
3. **Generate background music** — synthetic track via ffmpeg sine-wave generation, or download royalty-free
4. **Compose with ffmpeg** — 4 images as slideshow + voiceover + music + captions (white text, yellow glow) → 720p 9:16 MP4
5. **Add captions** synced to voiceover via ffmpeg `drawtext` filter (white text with yellow `shadowcolor`/`shadowx=1:shadowy=1`)
6. **Deliver preview** to user for approval first

The user chose this over Veo video generation: still images as B-roll for a ~40s promo video targeting Mongolian teenagers. See `references/video-composition-ffmpeg-captions.md`.

## User Preference: Cyrillic Mongolian Captions (Not Transliterated)

This user has a strong preference for **Cyrillic Mongolian text** in captions (confirmed correction: "Кириллээр caption tai bh"). Do NOT use Latin transliteration (e.g. "Hiyamel oyuun uhaan") for on-screen captions — always use Mongolian Cyrillic (e.g. "Хиймэл оюун ухаан").

This applies to:
- **ffmpeg drawtext captions** — use `textfile=` approach (not inline `text=`) to avoid `:` parsing issues with phone numbers like `Бүртгүүлэх: 89097454`
- **KIE image prompts** — for text-free image generation, use `NO TEXT, NO LETTERS, NO LOGOS` and add Cyrillic text as a separate overlay step
- **Poster/carousel text** — when generating full-prompt images with embedded text, the model handles Cyrillic better when submitted via JSON file (not shell stdin) to avoid UTF-8 mangling

The user's preferred Mongolian TTS is ElevenLabs V3 dialogue via KIE with voice Lily, model elevenlabs/text-to-dialogue-v3 (dialogue[] format). Fallback: turbo-2.5 with voice Rachel. Last resort: edge-tts mn-MN-YesuiNeural.

## PDF → Translate → Multi-Voice Audiobook Pipeline

This pipeline converts a document (PDF) into per-chapter MP3 audiobooks with multiple TTS voices in dialogue format. It chains: text extraction → chunking → translation → multi-voice dialogue TTS → MP3 assembly.

### When to Use

- User provides a PDF (or any document) and asks for an **audiobook/audio version**
- User wants **multi-voice dialogue** (narrator + characters, or male+female interview format)
- User wants translation built into the pipeline (e.g. English PDF → Mongolian audiobook)
- Output should be **per-chapter MP3 files**

### Pipeline Steps

```
PDF ──→ [1. Extract] ──→ [2. Chunk] ──→ [3. Translate] ──→ [4. Format Dialogue] ──→ [5. TTS per Chapter] ──→ Chapter MP3s
```

#### Step 1: Extract Text from PDF
Use the `ocr-and-documents` skill. For text-based PDFs, pymupdf is fastest:

```bash
pip install pymupdf
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
with open('extracted.txt', 'w') as f:
    for page in doc:
        f.write(page.get_text() + '\n---PAGE BREAK---\n')
"
```

For scanned PDFs, see `ocr-and-documents` skill for easyocr or marker-pdf.

#### Step 2: Chunk by Chapters
Split extracted text into chapter-sized chunks. If the PDF has a table of contents, use it to find chapter boundaries. Otherwise, look for chapter headings (Chapter 1, 2... or section titles) or split at page ~10-page intervals for long documents.

Save each chapter to its own text file:
```python
chapters = [
    {"title": "Introduction", "text": "..." },
    {"title": "Chapter 1: Getting Started", "text": "..." },
    ...
]
# Save per chapter
import json
with open("chapters.json", "w") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
```

#### Step 3: Translate (English → Mongolian)
Use the LLM to translate each chapter's text from English to Mongolian. Send chapter by chapter to keep context manageable.

```python
# For each chapter, ask the LLM (through the agent) to translate
# The translated output becomes the raw material for dialogue formatting
```

**Translation guidelines:**
- Keep the meaning and tone faithful to the original
- Use natural conversational Mongolian (not literal word-for-word)
- Preserve paragraph structure and section breaks
- Mark speaker changes or narrative sections for dialogue formatting

#### Step 4: Format as Multi-Voice Dialogue
Split the translated text into speaker turns for the dialogue TTS model. The format depends on the content type:

**Narrative (interview/lesson format):**
```
Male narrator (voice: "Lily" ← default female; use "Sarah" for 2nd voice):
  Reads narration, explanations, scene descriptions

Female co-host (voice: "Sarah" / "Alice"):
  Reads questions, reactions, emphasis points, call-to-action
```

**Story/Drama format:**
```
Protagonist voice (voice: "Lily")
Antagonist/side character voice (voice: "Sarah")
Narrator voice (voice: "Lily" or "Sarah")
```

**Format into dialogue JSON:**
```json
{
  "dialogue": [
    {"text": "Сайн байна уу? Өнөөдөр бид хамтдаа...", "voice": "Lily"},
    {"text": "Тэгэхээр энэ нь яг яаж ажилладаг вэ?", "voice": "Sarah"},
    {"text": "Маш энгийнээр тайлбарлая...", "voice": "Lily"}
  ],
  "stability": 0.5
}
```

**Tips for good dialogue formatting:**
- Keep each turn 2-5 sentences (not entire paragraphs) — natural spoken rhythm
- Alternate voices every 2-4 turns to keep it interesting
- Use emotion tags for expressiveness: `[excited]`, `[happy]`, `[sad]`, `[whisper]`
- For long explanations, break into Q&A-style dialogue (question from one voice, answer from the other)
- Aim for 3-5 minutes of audio per dialogue JSON file (roughly 300-500 words in Mongolian)

#### Step 5: Generate Multi-Voice TTS Per Chapter

Use the dedicated multi-voice script at `scripts/kie_elevenlabs_multivoice.py`:

```bash
python3 /opt/data/skills/media/kie-content-maker/scripts/kie_elevenlabs_multivoice.py \
  chapter_1_dialogue.json \
  chapter_1.mp3 \
  elevenlabs/text-to-dialogue-v3
```

A fallback copy also lives at `/opt/data/scripts/kie_multi_voice_tts.py` (same logic, created independently).

This generates one MP3 file per chapter. **Typical timing:** ~150-180s for 9 dialogue turns (approx 2 pages of PDF content → ~2.5 MB MP3). For a 12-page PDF, estimate ~15 minutes total across all chapters if pipelined sequentially.

For long chapters, split the dialogue into multiple segments (3-5 min each, roughly 10-15 turns) and merge them after generation using ffmpeg concat.

**Supported voices for dialogue-v3 (tested):**
| Voice | Gender | Notes |
|-------|--------|-------|
| `Lily` | Female | ✅ Default, most reliable, tested with Mongolian |
| `Sarah` | Female | ✅ 2nd female voice option |
| `Alice` | Female | ✅ 3rd female voice option |
| `Callum` | Male | ✅ Best male voice, tested with Mongolian |
| `Daniel` | Male | ✅ Male alternative |
| `Liam` | Male | ✅ Male alternative |

⚠️ Dialogue-v3 does NOT support (confirmed rejected by API): `Rachel`, `Antoni`, `Sam`, `Adam`, `Patrick`, `Thomas`, `Michael`, `Oliver`, `Ethan`, `Henry`, `Jack`, `Noah`, `James`, `Benjamin`, `Lucas`, `William`, `Mason`, `Elijah`, `Alexander`, `Arabella`, or any voice UUID. Always test a new voice with a single-`text` task to the turbo-2.5 model first — rejection is immediate (HTTP 422/500).

**If V3 queue is stuck** (stays in "waiting" then "fail"): fall back to sequential single-voice generation. Generate each turn individually with `text_to_speech` tool (configured for turbo-2.5), then concatenate with ffmpeg.

#### Step 6: Merge & Deliver Per-Chapter MP3s

For chapters split into multiple segments:
```bash
# Concatenate MP3 segments for one chapter
ffmpeg -f concat -safe 0 -i <(for f in ch1_seg1.mp3 ch1_seg2.mp3; do echo "file '$PWD/$f'"; done) \
  -c copy chapter_1.mp3
```

Deliver each chapter MP3 to the user:
```
MEDIA:/path/to/chapter_1.mp3
MEDIA:/path/to/chapter_2.mp3
```

### Pitfalls

1. **V3 queue congestion** — `elevenlabs/text-to-dialogue-v3` frequently gets stuck in "waiting" on KIE's backend. When it fails, fall back to single-voice sequential generation with `text_to_speech` tool using turbo-2.5 model, then ffmpeg-concatenate.
2. **Long dialogue arrays** — Tested: 9 turns (~2000 Mongolian Cyrillic chars, ~2.5 MB MP3 output, ~150s generation) works reliably. Very long dialogue arrays (>20 turns or >5000 chars) may cause the V3 model to timeout or produce truncated output. Split into segments of 8-12 turns each for reliability.
3. **Mongolian Cyrillic in JSON** — Always use `ensure_ascii=False` and UTF-8 encoding when writing dialogue JSON files. Write the JSON file from Python, not from shell, to avoid UTF-8 mangling.
4. **KIE API key not in execute_code** — `KIE_API_KEY` is set in shell env but NOT in `execute_code` Python env. Always run TTS script via `terminal()` tool, not `execute_code`.
5. **SSL verification** — This server needs `ssl._create_unverified_context()` for all `urllib` calls to `api.kie.ai`. The multi-voice script handles this automatically.
6. **Download URL expiry** — KIE temp URLs expire quickly. The script downloads immediately after generation.
7. **Chapter boundaries** — If the PDF has no clear chapters, ask the user how to split, or use page-count-based chunks (10-15 pages ≈ 20-30 min of audio).
8. **Translation quality** — For formal/professional content, do a translation sanity check before TTS generation. If the topic is highly technical or domain-specific, ask the user to verify the first chapter's translation before generating the rest.

### Scripts

- `scripts/kie_elevenlabs_multivoice.py` — Multi-voice dialogue TTS wrapper. Accepts JSON with `{"dialogue": [{"text": "...", "voice": "Lily"}, ...]}` array. Generates one MP3 with alternating voices.

### Input JSON Format Reference

Full example dialogue JSON:

```json
{
  "dialogue": [
    {
      "text": "Сайн байна уу? Тавтай морил. Өнөөдөр бид маш сонирхолтой сэдвийн талаар ярилцах болно.",
      "voice": "Lily"
    },
    {
      "text": "Тийм ээ, надад хэлээч, энэ нь яг юу вэ?",
      "voice": "Sarah"
    },
    {
      "text": "Энэ бол хамгийн сүүлийн үеийн технологи юм. [excited] Маш олон боломжийг нээж өгч байна!",
      "voice": "Lily"
    }
  ],
  "stability": 0.4
}
```

## Reference Files

- `references/kie-api-notes.md` — endpoint notes and observed request/response shapes.
- `references/supernova-two-stage-carousel-overlay.md` — Supernova brand carousel two-stage pattern: text-free background via KIE + Pillow overlay with actual brand logo, exact color hexes, and fixed Mongolian text elements. Includes brand color table, background prompt template, Pillow CLI usage, and automation integration notes.
- `references/kie-veo-result-download-continuation.md` — Veo 3.1 Fast polling, result URL extraction, continuation IDs/seeds, and MP4 verification pitfalls.
- `references/kie-veo-continuation-spokesperson-ads.md` — Veo 3.1 Fast multi-generation continuation ads with same-character storytelling, task/seed handoff, audio QA, and Postly-style spokesperson examples.
- `references/kie-cron-auto-carousel-pattern.md` — `no_agent: true` cron script pattern for daily GPT Image 2 carousel generation with Make.com webhook, state file advancement, shell escaping pitfalls, and timing/cost estimates.
- `references/brand-carousel-prompt-authoring.md` — workflow for extracting brand identity, layout rules, slide structure, and content type labels from a user and saving as a reusable carousel image generation prompt document (for ChatGPT, KIE GPT Image 2, or other image generators). Covers style references, image placement rules per content type, and two delivery options (user self-designs vs automated generation).
- `references/testimonial-photo-two-stage-overlay.md` — two-stage overlay pattern for student/testimonial carousels: generate branded slide background via KIE GPT Image 2, then overlay actual person photo via Pillow with rounded corners. Includes concrete Batbaatar example and compositing code.
- `references/openai-vision-image-review.md` — OpenAI GPT-4o vision review workflow for carousel image QA. Covers review script usage, scoring rubric, JSON output parsing, and cron integration. Companion script at `scripts/review_image.py`.
- `scripts/generate_kie_carousel.py` — Generic Python template for generating N slides via KIE GPT Image 2, with correct download URL parsing, polling, and error handling. Copy and modify for each brand/carousel.
- `scripts/kie_elevenlabs_tts.py` — KIE ElevenLabs TTS wrapper for Hermes command TTS provider. Usage: `python3 kie_elevenlabs_tts.py <input_path> <output_path> <voice> <model>`. Available voices: Rachel, Lily, Sarah, Alice. Requires `KIE_API_KEY`.
- `scripts/kie_elevenlabs_multivoice.py` — Multi-voice dialogue TTS wrapper using `elevenlabs/text-to-dialogue-v3`. Usage: `python3 kie_elevenlabs_multivoice.py <dialogue_json> <output_path> [model]`. Accepts JSON with `{"dialogue": [{"text":"...","voice":"Lily"}, ...]}`. Generates single MP3 with alternating voices. Required for audiobook and multi-speaker workflows.
- `references/template-driven-carousel-architecture.md` — template-as-database-schema pattern: fixed template + dynamic markers + image slots + Pillow compositing. Philosophy from Battushig (May 2026). Concrete example for `aiglobal_success_story_v1`.
- `references/mongolian-content-generator-patterns.md` — Mongolian-specific content generation patterns: student description parsing, name gender detection pitfalls (e.g. "Тэмүүлэн" contains "эм"), pipe-delimited story format, KIE slot prompt templates, and default Mongolian text values.
- `references/new-brand-content-plan-workflow.md` — when user sends a brand image and asks for a full social media content plan: brand identification, weekly calendar, reel ideas, carousel design, 30-day launch plan. Covers the vision-fallback pattern.
- `references/vision-fallback-when-model-doesnt-support-vision.md` — direct OpenAI GPT-4o vision API call via terminal when the active conversation model cannot accept image_url inputs (e.g. deepseek-v4-flash). Base64 encode, fallback pattern, ssl context workaround.
- `references/ebarimt-api-notes.md` — Mongolia eBarimt consumer API research: Keycloak auth (realm `ITC`, client `vatps`), consumer endpoints on `service.itc.gov.mn`, POS API 3.0 merchant endpoints, accessibility notes. Use when the user asks about ebarimt lottery registration, receipt lookup, or Mongolian government API integration.
- `references/video-composition-ffmpeg-captions.md` — FFmpeg composition for social video ads: scaling scenes to 1080x1920, Cyrillic Mongolian captions via textfile (avoiding colon parsing bug), time-based caption animation, scene concatenation with and without crossfade, voiceover overlay.
- `references/ffmpeg-poster-composition-mongolian.md` — 1:1 square poster creation from background image + Cyrillic text overlays using ffmpeg drawtext with textfile. Covers multiple drawtext chaining, font availability, color styling, box backgrounds, and Make.com webhook multipart upload pattern. Use when KIE image-to-image or Pillow is unavailable.
- `references/kie-gpt-image-1.5-notes.md` — GPT Image 1.5 model naming findings and file upload unavailability from this server.
- `references/user-reel-background-pip-overlay.md` — User-provided reel background template with picture-in-picture scene image overlay pattern. When user sends their own JPEG as the reel background, use full-screen background + PiP scene images + captions on top.

## Vision Fallback Pattern

When the active conversation model doesn't support `image_url` input (e.g. `deepseek-v4-flash`, certain auxiliary models), `vision_analyze` fails with a `unknown variant image_url` error. Use the fallback pattern in `references/vision-fallback-when-model-doesnt-support-vision.md` to call OpenAI GPT-4o vision directly via terminal with the `OPENAI_API_KEY` env var.

## Hard Rules (User-Enforced, Session-Corrected)

1. **NEVER use FFmpeg for poster generation.** FFmpeg's `drawtext` is ONLY for video composition (reels with captions). Posters must be generated EXCLUSIVELY through KIE AI (GPT Image 2 text-to-image or image-to-image). The user explicitly banned FFmpeg posters — this is a hard rule. Violating it wastes KIE credits and produces rejected output.

2. **Make.com poster webhook: single request, numbered fields.** Always send all N posters in ONE multipart request with `image1=@poster1.png` through `imageN=@posterN.png`. Separate individual POSTs result in only 1 poster being received (Make.com scenario uses numbered fields). Base64-in-JSON fails with request entity too large. As safety net, send individual backup POSTs (2s delay each) after the combined request. Confirm by checking Facebook output.

3. **Poster generation: KIE GPT Image 2 text-to-image preferred.** When the user provides a background template and file upload to KIE is broken (403/404 from this server), describe the template's visual style, layout zones, and colors in the text-to-image prompt. Do NOT attempt image-to-image: `gpt-image/1.5-image-to-image` (with `input_urls`) consistently returns Internal Error 500, and KIE file upload is unreachable from this server (403/404). Text-to-image with a detailed style description is the only reliable path.

4. **NEVER regenerate already-approved/sent posters.** If 3 posters are already on Facebook, generate ONLY the 4th. Recreating existing assets wastes credits and frustrates the user. The Make.com webhook accepts individual poster additions. When unsure, ask which posters still need creation.

## Common Pitfalls

1. **API key in code.** Always use `KIE_API_KEY` env var. Store in `/opt/data/.env` as `KIE_API_KEY=...` for cron scripts to load, never write the literal key into scripts or prompts.

2. **Stale API docs.** KIE docs are Apidog-generated and endpoint schemas may evolve. If validation fails, use the error body to update parameter names.

3. **Infinite polling.** Set a bounded retry count (30 attempts × 10s = 5 min max). Report timeout as failure rather than hanging.

4. **Expiring download URLs.** Temporary KIE download URLs expire quickly. Save files to disk immediately once a final URL is available.

5. **Overstuffed image text.** Poster models struggle with long non-English copy. For Mongolian, generate text-free images (`NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS`) with clean negative space, then overlay text locally with Pillow using a font that supports Cyrillic/Mongolian. See `references/mongolian-poster-text-overlay.md`.

6. **Hard typography panels.** When overlaying text on portrait images, prefer smooth full-canvas gradients and blurred backplates over hard rectangles. Hard edges across faces look like artifacts.

7. **Publishing without approval.** Content generation is not publication. For this user: approval-first workflow.

8. **Language mismatch.** For Mongolian audience content, default to Mongolian text unless the user specifies otherwise.

9. **Shell escaping non-ASCII prompts.** Never pass Cyrillic/CJK text through shell `-d '...'` — the shell mangles UTF-8 bytes. Use Python's `urllib.request` or a temp JSON file with `curl -d @file.json`.

10. **Cron script path restriction.** Script files must be relative filenames in `~/.hermes/scripts/`. Absolute paths are rejected with an error.

11. **ElevenLabs V3 dialogue model stuck in "waiting" then "fail".** `elevenlabs/text-to-dialogue-v3` frequently submits successfully (code 200, task created) but stays in "waiting" state for 50+ polls (~2.5 min) before transitioning to "fail". This is a server-side KIE queue issue, not a payload problem. The `dialogue[]` format is correct but the model's backend is unreliable. Fall back to `elevenlabs/text-to-speech-turbo-2-5` with `text`+`voice` Format A when V3 fails. The `kie_elevenlabs_tts.py` wrapper handles both formats — just switch the `model` and `voice` in config.yaml.

12. **Reel/Video frame approval flow.** This user requires frame-by-frame visual descriptions approved BEFORE any generation submits to KIE. Follow this order: (1) draft concept → (2) write TTS script for approval → (3) write frame-by-frame visual descriptions → (4) wait for approval → (5) generate images → (6) generate TTS → (7) ffmpeg composite → (8) preview. Never skip to generation. The user's specific CTA preference: "comment үлдээгээрэй" (silent CTA frame, no voiceover on last frame).

15. **User-provided template compositing (not KIE-generated background).** When the user sends their own template image (JPEG/PNG) and says "use this as the background," do NOT send it to KIE for re-generation. Instead:
    - Use the user's image directly as the base canvas
    - Only overlay the brand's actual logo, person photo, and any missing text
    - Cover/remove any pre-existing old logo on the template by sampling nearby background color and drawing a filled rectangle before placing the new logo
    - Use smooth anti-aliased rounded corners for person photos (render at 4x resolution, then downscale with LANCZOS)
    - Use soft shadow (GaussianBlur) instead of sharp colored borders around photos — gold borders create jagged corner artifacts
    - Verify the template has no overlapping elements before sending to the user
    - This pattern was specifically corrected: the user had a ready template and I was wasting credits generating a new KIE version. The review script at `scripts/review_image.py` should catch overlapping logo issues.

24. **User-provided template: use image-to-image via tmpfiles.org, not text-to-image description.** When the user sends a JPEG template and says "use this as background" (like temp1 for AI Global), you CAN use `gpt-image-2-image-to-image` — upload the template to **tmpfiles.org** (not KIE's broken file upload) to get a public URL for `input_urls`. This produces much better results (exact template layout retained) than describing the template in a text-to-image prompt. If the user also provides a person photo (instructor/student), upload BOTH images to tmpfiles.org and include both in `input_urls`. See the "Multi-Image Image-to-Image via tmpfiles.org" section above for the full pattern.

25. **GPT Image 2 invents brand assets.** Prompt-only generation does not produce real brand logos or accurate brand colors. Always use deterministic Pillow overlay for brand elements (logo, colors, phone, frames).

26. **ElevenLabs V3 dialogue model queue congestion.** `elevenlabs/text-to-dialogue-v3` (the user's preferred "V3" model for Mongolian TTS) frequently gets stuck in "waiting" then transitions to "fail" — a server-side KIE queue issue. When V3 is stuck, switch to `elevenlabs/text-to-speech-turbo-2-5` (Format A: text+voice) or `elevenlabs/text-to-speech-multilingual-v2` (same format). All three share the same backend queue, so if one is stuck, all may be stuck. Last resort: edge-tts Python package with voice `mn-MN-YesuiNeural` for Mongolian TTS.

13. **Missing Pillow or font dependencies for two-stage overlay.** Before starting a two-stage workflow that composites backgrounds + local text/logo, verify that (a) `Pillow` is importable in the target Python, (b) the font files referenced in the overlay script exist at their expected paths (e.g. `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf` for Cyrillic/Mongolian support), and (c) any brand logo asset is in PNG format with transparency (JPG opaque backgrounds look unnatural on composited slides). If these are missing, install/fix them before generating backgrounds — not after, or you'll waste KIE credits on backgrounds that can't be composited. For this user's server, create a venv at `/opt/data/.venv` and use `/opt/data/.venv/bin/python3` for Pillow operations.

14. **KIE queue "waiting" state**: GPT Image 2 tasks can get stuck in state `"waiting"` when the generation queue is congested. This is NOT a failure — the task is queued but hasn't started generating. Wait up to 90 polls (15 min). If it stays in `"waiting"` beyond that, submit a new task with a fresh task ID. Do NOT cancel early — tasks often auto-advance to `"generating"` after 10-30 polls.

17. **KIE generation speed varies wildly — retry on excessive timeouts.** Observed variation: a slide can take anywhere from ~90s (fast) to >600s (stuck in `"generating"`). If a task hasn't completed after 60 polls (10 min), it may be stuck. Instead of waiting indefinitely, submit a fresh task for that slide with a slightly simplified prompt (shorter body text, fewer visual constraints). The stuck task will either finish later (can be discarded) or fail — either way a fresh parallel task gives a recovery path. Do NOT assume a long-running task will fail; it may still complete. Let the retry run alongside the original.

18. **Python path mismatch in background/cron scripts.** The Hermes venv Python (`/opt/hermes/.venv/bin/python3`) has Pillow, openai, and other packages. The system Python (`/usr/bin/python3`) does not. When running compositing or review scripts via `terminal(background=true)` or cron `script:`, either:
    - Use explicit path: `/opt/hermes/.venv/bin/python3 /path/to/script.py`
    - Or set shebang to `#!/opt/hermes/.venv/bin/python3` in the script file
    - Or export `PATH="/opt/hermes/.venv/bin:$PATH"` before running
    - Failing to do this causes `ModuleNotFoundError: No module named 'PIL'` or `'openai'` at runtime

17. **SSL verification in KIE Python scripts.** On this server, `urllib.request.urlopen()` raises SSL certificate errors when connecting to `api.kie.ai`. Always pass `context=ssl._create_unverified_context()` (import `ssl` and create `ssl_ctx = ssl._create_unverified_context()` once at the top of the script). Without this, every API call fails with a certificate verification error.

18. **`pip install openai` required for review script.** The review script at `/opt/data/scripts/review_image.py` uses `from openai import OpenAI`. If the `openai` package is not installed, the script crashes. Verify with `python3 -c "from openai import OpenAI; print('OK')"` before relying on the review pipeline.

20. **User may reject Pillow compositing** — The AI Global user explicitly rejected the two-stage Pillow approach as "huuchin" (old/dated). For this user, prefer `gpt-image-2-image-to-image` with reference images. Check before defaulting to Pillow compositing.

22. **Mongolian TTS fallback: edge-tts Python package.** The Hermes `text_to_speech` tool (edge provider) fails for Mongolian Cyrillic text with "No audio was received". The `edge-tts` Python package (installable via `pip install edge-tts` in the Hermes venv) works with Mongolian voice `mn-MN-YesuiNeural` (female) and `mn-MN-IreeduiNeural` (male). Use this as a fallback when KIE ElevenLabs queue is stuck in "waiting". The edge-tts output is .mp3 and can be used directly in ffmpeg composition. The ebarimt.mn website and API subdomains return connection timeouts from non-Mongolian IPs. However, `auth.itc.gov.mn` (Keycloak) and `service.itc.gov.mn` (consumer API) are reachable. Always test connectivity before planning automated flows. See `references/ebarimt-api-notes.md` for the full accessibility matrix and known working endpoints.

27. **ffmpeg drawtext with Mongolian Cyrillic breaks on `:` in text values.** When using ffmpeg's `drawtext=text='...'` filter with text containing `:` (colon), the filter parser interprets the colon as an option separator and fails with `No option name near`. This is especially common with phone numbers like `Бүртгүүлэх: 89097454`. The fix is to use `textfile=` parameter instead of inline `text=`: write each caption to a separate text file, then reference it as `drawtext=textfile=/path/to/caption.txt:fontfile=...:fontsize=...`. This avoids all shell/filter parsing issues. See `references/images-as-broll-ffmpeg-composition.md` for full working examples.

29. **GPT Image 2 redesigns user-provided templates.** When using `gpt-image-2-image-to-image` with a template reference, the model frequently treats the reference as "style inspiration" and regenerates the logo, changes branding text, alters the footer, and shifts the overall layout — even when explicitly told "keep exactly as in the reference." **The simple "DO NOT change" instruction is not sufficient.** Use this proven two-stage approach:

    **Stage 1 — Generate WITHOUT a logo:** Tell KIE: "IMPORTANT - NO LOGO: The [logo position] area has NO LOGO. Do NOT add, invent, or place any logo. Leave it as empty [background color]." This prevents the model from inventing a fake logo.

    **Stage 2 — Overlay real logo with Pillow:** After generation, overlay the actual brand logo PNG deterministically. See `references/no-logo-plus-pillow-overlay-pattern.md` for exact code and per-brand paths.

    The user explicitly confirmed this approach (June 5, 2026): "dimension do not change the logo anything else just the dynamic texture it can be changed." The background texture CAN vary — only the logo, branding bar text, and footer contact info must remain fixed.

    See `news-poster` skill's `references/template-preservation-prompt-pattern.md` for prompt structure.

## Carousel Comparison Slide Design: Side-by-Side, Not Sequential

When creating comparison/before-after carousel content (WITH vs WITHOUT, Problem vs Solution), the user prefers a **single split-frame slide** showing both sides simultaneously — not two sequential slides. This was explicitly corrected when I proposed separate "WITHOUT" and "WITH" slides; the user wanted them merged into one slide for instant visual contrast.

**Layout pattern:**
- Split the 1:1 square into two vertical halves
- LEFT (WITHOUT / Problem): dark theme (deep teal/navy), stressed visuals, 4 roles with salary totals
- RIGHT (WITH Postly / Solution): turquoise/bright theme, AI agent icons, low price point
- Thin vertical divider line in center
- Brand logo top-right corner

**Why this works:** The user wants the cost/salary savings to register in one glance — scrolling from one slide to another dilutes the comparison.

## Brand Logo Placement in Two-Stage Carousels

**ALWAYS include the actual brand logo on branded carousel images.** The user corrected me for forgetting it. This is not optional.

**Placement:** Top-right corner by default — the user explicitly confirmed this position. Use a small logo (≈18% of slide width) with margin.

**Before compositing, verify:**
1. The logo file exists at the brand's `assets/logos/` path
2. It loads correctly with Pillow (check with `Image.open()` before the generation loop)
3. If JPG (no alpha channel), paste without mask: `overlay.paste(logo, (x, y))`. If PNG with alpha, use the mask: `overlay.paste(logo, (x, y), logo)`

**Font verification before compositing:** ALWAYS test that font files load with `ImageFont.truetype()` BEFORE submitting KIE background generation jobs. A missing or corrupt font file wastes KIE credits on backgrounds that can't be composited. Run this check:

```python
try:
    font = ImageFont.truetype(FONT_BOLD, 40)
    print("Font loaded ✓")
except Exception as e:
    print(f"Font error: {e}")
    # Fallback to DejaVu Sans Bold which is known to work
    FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
```

## API Key Accessibility

`KIE_API_KEY` is set in the shell environment but NOT available in the `execute_code` tool's Python environment. When making KIE API calls, use the `terminal` tool with `curl` or Python via `python3 -c` in a shell command — not `execute_code`. If you need to run a script, write it to a file and invoke it via `terminal`.

## Concept Approval Workflow: Test One Slide First

When the user proposes a new campaign concept (carousel/reel campaign), do NOT generate the full set upfront. Follow this pattern:

1. **Present 2-3 concept directions** as text/tables (the user picks one)
2. **Generate ONE sample slide** from the chosen concept
3. **Send for review** — the user may want layout changes, different text, or brand positioning fixes
4. **Only after approval** of the test slide, proceed to generate the remaining slides

This saves KIE credits and avoids rework. The user explicitly said "test one slide first, if I like it we continue."

## Template-Driven Carousel Architecture (Battushig's Pattern)

### Philosophy: Template as Database Schema

The user explicitly articulated this principle: **KIE should not generate the entire poster.** The model hallucinates logos, misspells text, and invents layouts — every time.

Instead, treat the template as a **database schema**:

| Layer | Responsibility | Never changes |
|-------|---------------|---------------|
| **Template** | Fixed layout — background, logo position, typography, colors, progress bar, footer | Ever |
| **Hermes** | Generates *only* marker values — text content, student profiles, storylines | Generates new content each run |
| **Image Gen (KIE)** | Generates *only* image slots — text-free photos, visuals, dashboards | Prompt style per slot stays consistent |
| **Renderer (Pillow)** | Composites template + markers + images → final 4 slides | Logic is fixed per template_id |

### Fixed vs Dynamic (Lock/Unlock Principle)

**NEVER redesign the template. NEVER move the logo. NEVER change typography. NEVER change colors. NEVER change layout.**

Only generate values for markers.

Example breakdown for `aiglobal_success_story_v1`:

**Locked (fixed elements):**
- Logo position: top-left pill badge + top-right logo
- Background: light cream (#FAFAF8), Italian minimal
- Font: Manrope (fallback DejaVu Sans Bold)
- Colors: charcoal (#1A1A1A), gold (#D7AB46), white (#FFFFFF)
- Carousel progress bar: disabled
- Footer: contact info bottom-left
- Gold bottom divider

**Variable (dynamic markers):**
- Slide 1: student_photo, headline, student_name, age, occupation, quote
- Slide 2: before_photo, problem_1/2/3
- Slide 3: success_photo, week_1/2/3
- Slide 4: result_visual, metric_1/2/3, cta

### The Image Slot Pattern

DO NOT tell KIE: "Create a student success story poster."

Instead, tell it: "Generate only: student_photo, before_photo, success_photo, result_visual" — each with specific style constraints. Then inject into the template.

**4 image slots per carousel:**

```
slot_A: student_photo      → Slide 1 (portrait, right)
slot_B: before_photo       → Slide 2 (struggle visual, right)
slot_C: success_photo      → Slide 3 (happy+ laptop, right)
slot_D: result_visual      → Slide 4 (dashboard/app, right)
```

**Style for each slot (don't vary across runs):**
- slot_A: "Mongolian, 18-25 years old, professional, friendly, realistic, high quality, white background, yellow accent lighting"
- slot_B: "Young Mongolian student thinking, confused expression, professional photography, realistic"
- slot_C: "Young Mongolian student smiling with laptop, achievement moment, bright, happy, professional photography"
- slot_D: "Mobile app dashboard, colorful data visualization, achievement screen, modern UI design, clean"

### Pipeline Flow

```
1. Hermes generates content ───────────→ template_data.json
   (student profile, text markers,        (all marker values)
    storyline, CTA)

2. KIE GPT Image 2 generates ──────────→ slot_A.png .. slot_D.png
   4 text-free images                     (NO TEXT, NO LOGOS)

3. Renderer (Pillow) ──────────────────→ slide_1.jpg .. slide_4.jpg
   composites template background +
   fixed elements (logo, badge, footer) +
   text markers + slot images

4. Delivery ──────────────────────────→ Telegram preview
   approval-first, one slide at a time
```

### Template Schema Location

The template layout is defined in a JSON schema at the brand's template directory:

```
/opt/data/social-content/brands/<brand>/templates/<template_id>/
  template.json       — Full schema: fixed layout + slide markers + image slots
  render.py           — Pillow compositing script (entry point)
```

Concrete example (created in this session):
```
/opt/data/social-content/brands/ai-global/templates/aiglobal_success_story_v1/
```

The template.json defines:
- `fixed.typography` — font sizes, colors, fallback paths
- `fixed.colors` — hex value constants
- `fixed.layout` — exact positions for badge, logo, footer, divider
- `slides[]` — each slide with markers, placement coordinates, font styles
- `image_slots` — slot IDs with gen-style descriptions

### Pipeline Invocation

```bash
# 1. Generate content (Hermes does this — produces JSON)
hermes_content.json

# 2. Generate 4 slot images via KIE
python3 /opt/data/scripts/generate_slot_images.py \
  --template aiglobal_success_story_v1 \
  --data hermes_content.json \
  --output-dir ./slots/

# 3. Composite final slides
python3 /opt/data/social-content/brands/ai-global/templates/aiglobal_success_story_v1/render.py \
  --template template.json \
  --data hermes_content.json \
  --slots-dir ./slots/ \
  --output ./final_slides/
```

### Why This Works

- **95% brand consistency** — fixed elements never change across 100s of carousels
- **Unlimited variety** — Hermes generates different stories each run while the template stays identical
- **No KIE text errors** — textual content is overlaid deterministically by Pillow
- **No KIE logo invention** — real brand logo is composited from disk
- **Credits used efficiently** — only generate what changes (4 small photos), not 4 full poster slides

## User Design Preferences (Battushig / Postly & Supernova Brands)

When generating carousel poster content for this user's Mongolian brands, apply these design defaults:

### All brands
- **Cleaner, lighter, simpler** — the user explicitly asked for a "lighter, simpler version" with less visual noise. Prefer light/cream/soft backgrounds over dark or busy gradients, minimal text per slide (short headline + 1-2 bullets max), generous whitespace, and clean modern typography over cluttered infographic style.
- Verified reference example: beige/cream tones (#F4EFEB range), high brightness (200+/255), subtle contrast, portrait 1:1.5 ratio.

### Postly-specific
- Brand colors: turquoise (#4CBFDD, #5ED4C0), deep teal (#063B4A), white, soft sky (#EAFBFF)
- Font: Nunito Bold (check `/opt/data/fonts/Nunito-Bold.ttf` loads; fallback to DejaVu Sans Bold if it doesn't)
- Comparison/cost content: prefer side-by-side single slides over sequential
- Always include Postly logo top-right on all branded images
- Content is approval-first: generate one slide, send preview via Telegram, wait for approval before continuing

### Supernova-specific
- Red/blue medical styling, thinner borders and softer shadows
- Logo card and phone capsule for brand recognition
- See `references/supernova-two-stage-carousel-overlay.md`

## GPT Image 2 Section-Based Prompt Pattern

For carousel slides where you need predictable layout zoning, use the section-based prompt pattern documented in `references/gpt-image-2-section-prompt-pattern.md`. The pattern breaks the slide into named zones (TOP/MIDDLE/BOTTOM) with specific content, hex colors, and styling per zone — yielding more reliable results than freeform single-block prompts for branded Mongolian carousels.
- Phone capsule, logo card, Supernova red/blue medical styling should remain for brand recognition, but use thinner borders and softer shadows.
- For future carousel templates, prefer simpler visual metaphors (one clear central element) over multi-element comparison layouts.

## Verification Checklist

- [ ] `KIE_API_KEY` was not written into any persistent file or final response.
- [ ] Credits were checked or the user accepted proceeding without a credit check.
- [ ] Request body used the intended model: Nano Banana 2, GPT Image 2, Veo 3.1 Fast, or ElevenLabs.
- [ ] Task id was captured.
- [ ] Polling reached success or a clear failure state was reported.
- [ ] Output URLs were converted/downloaded before temporary links expired.
- [ ] Local output paths and prompts/scripts were given to the user.
- [ ] Publishing, if any, waited for explicit approval.
- [ ] Shell escaping was avoided for non-ASCII prompts (used Python urllib or temp JSON file).
- [ ] Cron script is in `~/.hermes/scripts/`, not an absolute path.
- [ ] Environment dependencies verified for two-stage overlay: Pillow importable, fonts exist at expected paths, brand logo is PNG with alpha (or compositing path decided for JPG).