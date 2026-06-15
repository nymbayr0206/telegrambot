---
name: ai-global-brand-content
description: "AI Global brand content generation system — all 7 templates. Never compose/design: ONLY generate marker values + image prompts and pass to KIE."
version: 1.2.0
author: Hermes Agent
metadata:
  hermes:
    tags: [aiglobal, brand-content, templates, kie-ai, carousel]
    related_skills: [aiglobal-success-story-carousel, kie-content-maker, rss-news-pipeline]
---

# AI Global Brand Content System

## Cardinal Rule

**Do NOT generate poster layouts yourself.**
**Do NOT use Pillow — EVER.**
**Do NOT create new designs from scratch.**
**Do NOT reposition logos, text areas, typography, or branding elements.**

**LOCKED (never change):**
- Logo position (top-right, ~15% width)
- Gold accent color (#D7AB46) for badges, dividers, highlights
- Charcoal text color (#1A1A1A)
- Manrope font (or clean modern sans-serif equivalent)
- Top-left badge, bottom-left contact info, bottom gold divider
- Layout structure (headline position, spacing, margins)

**FLEXIBLE (can adjust per user request):**
- Background style and colors — the user may want cream, light blue gradient, or other light tones
- See authoritative style reference at `/opt/data/social-content/brands/ai-global/carousel-prompt-instructions.md`
- Always confirm with user before making background changes permanent

Your job is ONLY:
1. Select the correct template
2. Generate content marker values
3. Construct full slide prompts with embedded text + reference images
4. Pass everything to KIE's image-to-image model

Every template already contains:
- AI Global logo
- Manrope typography
- Brand colors (gold accent, charcoal text)
- Visual hierarchy, layout, design elements
- CTA sections, footer elements

Never reposition these. Never ask for the logo. Never create a new layout.

## Comparison/Transformation Content (Before/After)

When generating Before/After certification comparison content:

**TONE RULE — CRITICAL: Never use dramatic framing.**
- ❌ WRONG: "dark times", "no income", "no respect", "black period", "struggling"
- ✅ CORRECT: "Normal but inefficient — time wasted, headaches, work not enjoyable"
- The "Before" state is **normal/practical**, not dramatic/tragic
- The "After" state shows **practical improvements**: more time saved, less headache, work more enjoyable

**Content structure:**
| Element | Description |
|---------|-------------|
| Before | Normal work life but inefficient — lots of time wasted on repetitive tasks, frequent headaches, work isn't fun |
| After | Certification → time savings, fewer headaches, work becomes more enjoyable |
| Social proof | Global stat: "X people worldwide hold this certification" |
| Aspirational CTA | "You can be the next one" / "Beat the rest" — competitive but not dark |

This format works as a carousel (4 slides: before → after → global stats → CTA) or as standalone comparison posters. Apply the same CTA rules as course_sell_v1 (never "Бүртгүүлэх", always "Мэдээлэл авах → Коммент бичээрэй").

See `references/comparison-content-guide.md` for detailed markers and flow.

## Available Templates (7)

| Template ID | Purpose |
|---|---|
| `news-post-1` | AI tech news OR success story single poster — 1:1 square gold/amber background, fixed AI TECH NEWS branding bar + top logo + dark footer (8909 7454 / Ayud tower 601 TooT / aiglobal.mn). Only headline + image + body text are dynamic. News-poster skill has full details. |
| `aiglobal_industry_update_v1` | AI industry news/trends update |
| `aiglobal_success_story_v1` | Student success story carousel (4 slides) |
| `aiglobal_tips_hacks_v1` | AI tips, tricks, hacks |
| `aiglobal_course_intro_v1` | Course introduction / promo |
| `aiglobal_course_sell_v1` | Course sales promotion (4 slides: instructor intro, time savings, workforce efficiency, CTA) |
| `aiglobal_promotion_v1` | General promotion / offer |

## Template Markers

### aiglobal_industry_update_v1

```
marker_values:
  headline: string
  subheadline: string
  trend_1: string
  trend_2: string
  trend_3: string
  cta: string

image_prompts:
  hero_visual_prompt: string (text-free cinematic style)
```

### aiglobal_success_story_v1

See `aiglobal-success-story-carousel` skill for full pipeline. 4-slide carousel with:

```
marker_values:
  student_name: string
  occupation: string
  headline: string
  quote: string
  before_problem_1/2/3: string
  week_1/2/3: string
  result_1/2/3: string
  cta: string

image_prompts:
  student_photo_prompt: string
  before_photo_prompt: string
  success_photo_prompt: string
  result_visual_prompt: string
```

### aiglobal_tips_hacks_v1

```
marker_values:
  headline: string
  tip_1_title: string
  tip_1_desc: string
  tip_2_title: string
  tip_2_desc: string
  tip_3_title: string
  tip_3_desc: string
  tip_4_title: string
  tip_4_desc: string
  cta: string

image_prompts:
  hero_visual_prompt: string
  illustration_prompt: string
```

### aiglobal_course_intro_v1

```
marker_values:
  course_name: string
  instructor: string
  start_date: string
  duration: string
  format: string
  price: string
  key_takeaway_1/2/3: string
  target_audience: string
  cta: string

image_prompts:
  course_visual_prompt: string     # text-free scene/visual
  instructor_photo_prompt: string  # ONLY used when no real instructor photo exists
```

**⚠️ When user provides an actual instructor photo:** Do NOT use `instructor_photo_prompt`. Instead:
- Upload the user's photo + template background (temp1) to tmpfiles.org
- Use `gpt-image-2-image-to-image` with both images in `input_urls`
- 🔴 **CRITICAL: temp1 must NEVER be modified** — the prompt must say "Use the first image (temp1) as background EXACTLY as-is, do NOT modify or alter the template design"
- The prompt must say: "Take the person's face from the second image and place it in the circular/portrait frame that already exists on the template"
- Keep the template design perfectly intact — only fill in the portrait circle + add text
- See `kie-image-to-image` skill for the full multi-image workflow with temp1

### news-post-1 — AI Tech News Single Poster

A single 1:1 square news poster with fixed layout (gold background, AI TECH NEWS branding bar, logo, dark footer with contact info). Content is generated fresh each time using KIE GPT Image 2 image-to-image with the template reference.

```marker_values:
  headline: string                  # Short, bold, 2-5 word Mongolian headline
  body_line_1: string               # First key point (1 short sentence)
  body_line_2: string               # Second key point (1 short sentence)
  body_line_3: string               # Third key point (1 short sentence)
  
  # LOCKED — never change these:
  # Logo: AI Global logo (top area, kept from template)
  # Branding bar: "AI TECH NEWS" (fixed text)
  # Footer: "8909 7454", "Ayud tower 601 TooT", "www.aiglobal.mn"
  # Background: gold/amber (#F0AB06)
```

**Workflow (confirmed working):**
1. Fetch latest AI agentic/tech news from RSS feeds (TechCrunch AI, The Verge AI, Ars Technica)
2. Pick the most impactful story for Mongolian audience
3. Summarize in Mongolian — very short (headline: 2-5 words, body: 3 short bullet lines max)
4. Generate via KIE `gpt-image-2-image-to-image` with template reference from tmpfiles.org
5. Template ref URL is at `templates/news-post-1/assets/template-reference.jpg`; upload to tmpfiles.org first
6. KIE prompt construction: declare LOCKED elements first (DO NOT change logo, AI TECH NEWS bar, footer text, gold background), then DYNAMIC elements (headline + body)

**Reference:** `references/news-post-1-worked-example.md`

### aiglobal_promotion_v1

```marker_values:
  headline: string
  offer_title: string
  offer_detail: string
  discount_percent: string
  expiry_date: string
  condition_1/2: string
  cta: string

image_prompts:
  hero_visual_prompt: string
  offer_visual_prompt: string
```

### aiglobal_course_sell_v1 — Course Sales Promotion (4-slide carousel)

Persuasive sales carousel with 4 specific slides. Always present text content to user for approval first, then generate with temp1 + instructor photo.

```marker_values:
  slide_1_tagline: string                  # Hook: "Build your own AI agent"
  slide_1_instructor_name: string          # Full name (e.g. "А. Мөнх-Учрал")
  slide_1_instructor_bio_1: string         # First credential line
  slide_1_instructor_bio_2: string         # Second credential line
  slide_1_instructor_bio_3: string         # Third credential line
  slide_2_headline: string                 # e.g. "20+ hours/week saved"
  slide_2_saving_1: string                 # First automation category + hours
  slide_2_saving_2: string                 # Second automation category + hours
  slide_2_saving_3: string                 # Third automation category + hours
  slide_2_saving_4: string                 # Fourth automation category + hours
  slide_2_total: string                    # Total: "Сард 80+ цаг = 2 ажлын долоо хоног"
  slide_3_headline: string                 # e.g. "1 person = 5 people's work"
  slide_3_team_cost: string                # Traditional team + cost
  slide_3_ai_cost: string                  # AI agent team + cost
  slide_3_savings: string                  # Savings percentage
  slide_4_course_name: string              # e.g. "AI+ Agent"
  slide_4_benefit_1: string                # First course benefit
  slide_4_benefit_2: string                # Second course benefit
  slide_4_limited_spots: string            # "Зөвхөн 20 хүнийг бүртгэнэ"
  slide_4_requirement: string              # "Ямар ч код шаардлагагүй"
  slide_4_cta: string                      # CTA text

image_prompts:
  slide_template: "temp1.jpg (all 4 slides via image-to-image)"
  instructor_photo_path: "assets/people/trainer-<name>.jpg"
```

**4-Slide Structure:**
| Slide | Focus | Key Content |
|---|---|---|
| 1 | Instructor Intro | Hook tagline + instructor name + credentials + photo (temp1 + person photo) |
| 2 | Time Savings | 4 automation categories with weekly hours + monthly total |
| 3 | Workforce Efficiency | 1 AI Builder vs traditional team cost comparison with ₮ savings |
| 4 | CTA | Course name + benefits + limited spots + no-code + CTA |

**⚠️ CTA Rules (user preference — DO NOT violate):**
- NEVER include a start date on the poster
- NEVER use "Бүртгүүлэх" / "Register" — use "Мэдээлэл авах" or "Коммент бичээрэй"
- ALWAYS include limited spots: "Зөвхөн X хүнийг бүртгэнэ" (e.g. 20)
- Slide 1 MUST feature instructor's real photo on temp1 background (image-to-image)
- All text in Cyrillic Mongolian only
- **temp1 Knowledge Base:** A structured description of temp1's visual design, colors, layout, and immutable rules is at `/opt/data/knowledge_bases/ai-global-temp1/`. Load this when you need to describe temp1 without vision support.

**Workflow:**
1. Present 4-slide text content to user for approval
2. After approval, generate all 4 slides using temp1 + instructor photo (image-to-image for slide 1, text-only temp1 for slides 2-4)
3. Use `kie-image-to-image` skill for the technical generation pipeline

## How to Send to KIE — Which Approach per Template

**IMPORTANT: No dedicated template API endpoint exists yet.** The templates are NOT hosted on KIE's side. Choose approach by template type:

| Template | KIE Method | Why |
|---|---|---|
| `aiglobal_industry_update_v1` | Text-to-image full prompt | Pure text + hero visual, no reference needed |
| `aiglobal_tips_hacks_v1` | Text-to-image full prompt | Pure text content |
| `aiglobal_course_intro_v1` | **Image-to-image** (when instructor photo exists) or **text-to-image** (no reference) | If user provides real instructor photo, use `gpt-image-2-image-to-image` with both template + photo via tmpfiles.org. Otherwise fall back to text-to-image. |
| `aiglobal_course_sell_v1` | **Image-to-image** | All 4 slides use temp1. Slide 1 needs instructor photo embedded; slides 2-4 use temp1 text-only. |
| `aiglobal_promotion_v1` | Text-to-image full prompt | Offer text + visual |
| `news-post-1` | **Image-to-image** | Template has fixed layout (logo, bar, footer). Must preserve these via reference image. No separate photo needed. |

### Approach A (Standard): Text-to-Image Full Prompt

Used for: industry_update, tips_hacks, course_intro, promotion.

1. Write a **full GPT Image 2 prompt** that embeds the template layout description + all marker values + image prompt into one comprehensive text block
2. Submit via `POST /api/v1/jobs/createTask` with `model: "gpt-image-2-text-to-image"`
3. Poll `GET /api/v1/jobs/recordInfo?taskId=<id>` until state=`"success"`
4. Parse `data.resultJson` (JSON-encoded string) -> `resultUrls[0]`
5. Convert to signed download URL via `POST /api/v1/common/download-url`
6. Download locally immediately (URL expires ~20 min)

### Approach B: Image-to-Image with Reference Images

Used for: success_story (needs student photo + template background).

Use `model: "gpt-image-2-image-to-image"` when you need:
- Consistent template layout (send the reference template image)
- Real student/people photos embedded in the output
- Brand-accurate colors, logo, and typography
- Full text content baked into the image

Upload images to KIE first:

```bash
curl -s -X POST 'https://kieai.redpandaai.co/api/file-stream-upload' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -F "file=@template-reference.jpg" \
  -F "uploadPath=images/aiglobal-templates" \
  -F "fileName=template.jpg"
```

Then submit:

```python
payload = {
    "model": "gpt-image-2-image-to-image",
    "input": {
        "prompt": "Full slide description with embedded text...",
        "input_urls": [TEMPLATE_URL, PHOTO_URL],
        "aspect_ratio": "1:1"
    }
}
```

Poll and download same as Approach A. Observed: ~50-100s/slide.

See `aiglobal-success-story-carousel` skill for full pattern.

### Prompt Construction Pattern

The full prompt should describe:

- **Format**: "1:1 square social media carousel slide, 1080x1080"
- **Brand style**: See the authoritative style reference at `/opt/data/social-content/brands/ai-global/carousel-prompt-instructions.md` for current background, colors, and aesthetic. Default as of June 2026: light blue gradient (#E8F4FD → #D6EAF8), fresh modern feel.
- **Template layout**: Where each element goes (top-left badge, top-right logo, headline position, trend list, footer, CTA, divider)
- **Marker values**: All text content embedded directly in the prompt at their layout positions
- **Image prompt**: The hero/slot visual description
- **Style constraints**: "Premium, modern, educational", "No watermarks", "Mongolian Cyrillic text"

For Mongolian text, use latin transliteration when the prompt is sent via JSON — the model handles it better than raw Cyrillic inside JSON.

See `references/full-prompt-pattern-industry-update.md` for a concrete working example.

### Observed Generation Times

- GPT Image 2 text-to-image: ~80-290 seconds (generates full image + embedded text)
- GPT Image 1.5 image-to-image: ~60-90s per slide
- GPT Image 2 image-to-image: ~50-100s per slide
- ElevenLabs TTS: ~23s
- State transitions: generating (can take many polls) → success
- If stuck in "waiting" state beyond 15 polls (150s), submit a fresh task

### KIE API Reference

**Base URL:** `https://api.kie.ai`
**Auth:** Bearer token via `KIE_API_KEY` env var

**Endpoints:**
- `POST /api/v1/jobs/createTask` — create generation task
- `GET /api/v1/jobs/recordInfo?taskId=<id>` — poll task status

**Model Names (confirmed working):**\n| Model | Name | Input Fields |\n|-------|------|-------------|\n| GPT Image 2 Text-to-Image | `gpt-image-2-text-to-image` | `prompt`, `aspect_ratio`, `size` |\n| GPT Image 1.5 Image-to-Image | `gpt-image/1.5-image-to-image` | `prompt`, `input_urls` (array), `aspect_ratio`, `quality` |\n| GPT Image 2 Image-to-Image | `gpt-image-2-image-to-image` | `prompt`, `input_urls` (array), `aspect_ratio` |\n| ElevenLabs Dialogue V3 | `elevenlabs/text-to-dialogue-v3` | `dialogue[]` (array of `{text, voice}` objects) — use `voice: \"Lily\"` for Mongolian |

**Result format:** `resultUrls` array in the parsed `data.resultJson`
**Download:** Use `curl -L -o output.ext "resultUrls[0]"` (follow redirects with `-L`)
**File Upload (may be restricted):** Attempted endpoints `/api/file-base64-upload` (403), `/api/file-stream-upload` (404). When unavailable, fall back to text-to-image with descriptive prompts matching the reference style.

**Mongolian TTS notes (LEGACY — use dialogue V3 instead):**\n- **Always use `elevenlabs/text-to-dialogue-v3`** with `dialogue[]` array — see `kie-image-to-image` skill for full API reference\n- Voice: `"Lily"` works directly (no voice ID, no `language_code` needed)\n- Do NOT use `elevenlabs/text-to-speech-multilingual-v2` — user corrected this rule in June 2026\n- The old model notes below are kept only for reference:\n  - `language_code: "mn"` enables Mongolian pronunciation\n  - Voice "Rachel" works for Mongolian text\n  - Speed around 0.95 for natural pacing\n  - Returns ~28 seconds of audio for a ~600-char script

## Final Output Format

Return only:

```
template_id: [name]

marker_values:
  marker_1: "value"
  marker_2: "value"
  ...

image_prompts:
  prompt_key: "detailed style prompt, NO TEXT, NO LETTERS, NO LOGOS"
```

## Industry Update Workflow (from this session)

When the user requests an **industry update** carousel:

1. **Fetch fresh AI news** — use the `rss-news-pipeline` skill to pull latest articles from confirmed working sources:
   - TechCrunch AI (`https://techcrunch.com/category/artificial-intelligence/feed/`) — RSS 2.0, best source
   - The Verge (`https://www.theverge.com/rss/index.xml`) — Atom, filter by `<category term="AI"/>`
   - Ars Technica (`https://feeds.arstechnica.com/arstechnica/index`) — RSS 2.0, filter by `<category><![CDATA[AI]]></category>`

2. **Select top 3 stories** as trends — pick diverse, impactful stories relevant to AI Global's Mongolian audience (students, aspiring developers).

3. **Generate markers** — write headline, subheadline, 3 trends in **Mongolian**, with a motivational CTA pointing to AI Global's courses. Trends should be concrete and relatable.

4. **Generate image prompt** — cinematic, futuristic AI/tech visual style, text-free, dark theme with neon accents.

5. **Return in exact output format** — `template_id`, `marker_values`, `image_prompts`.

6. **Send to KIE** — Construct a full GPT Image 2 prompt embedding the template layout + all markers + image visual description. Submit via `POST /api/v1/jobs/createTask` with `model: gpt-image-2-text-to-image`. Poll, download, deliver to user.

No extra commentary unless the user asks.

## Approval Workflow: One Slide First

When generating a new carousel concept for any template:

1. **Text pre-approval** — For course sell carousels (course_sell_v1), present the full 4-slide text content to the user first. Wait for text approval before generating any images. This avoids wasting KIE credits on text revisions.
2. **Generate ONE sample slide only** (not the full set) — after text is approved, send the sample image for review.
3. **Send the image to the user for review** via MEDIA: path in Telegram
4. **Wait for approval or changes** — the user may want layout fixes, different text, or brand positioning changes
5. **Only after approval**, generate the remaining slides

This applies to ALL 7 templates. Reasoning: saves KIE credits, avoids rework, the user explicitly confirmed this pattern.

## Image Generation Rule

For image prompts:
- Generate prompts only — do NOT create the image yourself
- Always include `NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS`
- Style should match AI Global's premium cinematic aesthetic
- Send prompt to KIE (via `kie-content-maker` skill)

## User Communication Style

- For straightforward content generation: use tools first, present options quickly, avoid asking clarifying questions when the workflow is established
- If the user says "No" to an offer, stop offering further suggestions
- Deliver output fast without chit-chat

## Content Plan Tracking

The AI Global content plan lives in **Google Sheets** and a local **brand-guide.md** file — both are sources of truth.

**Google Sheet:** `AI Global Content Plan — June 2026`
- ID: `1LS3tcVV0n5GHVwCMtgjwW-6Yp_xB6dMKlMVbASos28Y`
- Tabs: Content Calendar, Carousel Tracker, Reel Tracker, Content Ideas, Industry News
- Contains weekly schedule, per-carousel slide generation status, per-reel status

**Brand guide:** `/opt/data/social-content/brands/ai-global/brand-guide.md`
- Section `Content Plan — June 2026` has the canonical monthly schedule (7 carousels + 4 reels)
- Goal: 20 students per course = 40 total per month

**Monthly content mix:**
| Type | Quantity | Examples |
|------|----------|---------|
| Carousels | 7/month | 3 educational, 3 product, 1 success story |
| Reels | 4/month | Intro, education, instructor meet, testimonial |
| News posters | ~4/month | AI trend news (news-post-1 template) |

**Status check pattern** — When the user asks "хэдэн контент генерировал бэ?", read both the Google Sheet (Carousel Tracker + Reel Tracker tabs) and the file system (`/opt/data/social-content/brands/ai-global/generated/` and `templates/news-post-1/`) to report total generated vs planned.

## Related Skills

- `aiglobal-success-story-carousel` — deep pipeline for the success story template (4-slide compositing, student content generation, slot image workflow)
- `kie-content-maker` — KIE.AI API integration (task submission, polling, download, two-stage overlay)
- `rss-news-pipeline` — fetching and filtering news from RSS feeds for industry update content
- `social-media-automation` — approval-first publishing workflow
- `kie-content-maker` references `references/template-driven-carousel-architecture.md` — the template-as-schema philosophy

## Reference Files

- `references/full-prompt-pattern-industry-update.md` — concrete working example of a full GPT Image 2 text-to-image prompt for `aiglobal_industry_update_v1`. Includes prompt template, latin transliteration rule, submission pattern, polling timing (observed ~290s), and download steps.
- `references/kie-template-full-prompt-pattern.md` — how to write and submit full GPT Image 2 prompts for templates (no dedicated KIE template endpoint yet).
- `references/course-sell-v1-worked-example.md` — worked example from June 2026: AI+ Agent course sell carousel (4 slides, instructor photo on temp1, CTA rules, cost comparison).
- **Live style authority**: `/opt/data/social-content/brands/ai-global/carousel-prompt-instructions.md` — the definitive brand design guide for all AI Global carousels. Update this file when background/color preferences change. The skill references it rather than duplicating the style spec.
- **Course sell carousel conventions**: `references/course-sell-carousel-conventions.md` — 4-slide structure, CTA rules, no start date, limited seats format, and English brand name handling for AI Global course promotion carousels.
- **temp1 Knowledge Base**: `/opt/data/knowledge_bases/ai-global-temp1/` — structured description of temp1's visual design, layout, colors, dimensions, and immutable rules, plus the actual image file. Use when you need to describe temp1 without vision support.

## Pitfalls

1. **Never use Pillow** — the user explicitly rejected it as "huuchin" (old). Use KIE GPT Image 2 instead (text-to-image for most templates, image-to-image for success stories).
2. **Mongolian text in image prompts** — always use "NO TEXT" constraint. KIE invents misspellings.
3. **Don't ask for the logo** — every template already has it embedded.
4. **Course sell CTA: NEVER use "Бүртгүүлэх"** — user always wants "Мэдээлэл авах → Коммент бичээрэй". Also: no start dates on posters, always include limited spots ("Зөвхөн X хүнийг бүртгэнэ"). Slide 1 must feature instructor photo.
5. **Background/colors flexibility** — Logo, font, gold accent, charcoal text, and layout structure are locked, but the **background style/color** can be updated on user request (as happened in June 2026: cream → light blue gradient). Always reference the live style doc at `carousel-prompt-instructions.md` rather than assuming a fixed background. If the user requests a background change, update both the skill and the prompt-instructions doc.
6. **Delivery to KIE** — `KIE_API_KEY` is in shell env, not in `execute_code` Python. Use `terminal` for KIE calls.
7. **SSL verification** — KIE API calls on this server need `ssl._create_unverified_context()`.
8. **Old news** — always fetch fresh news for industry updates. The reference file at `rss-news-pipeline/references/` may have stale data.
