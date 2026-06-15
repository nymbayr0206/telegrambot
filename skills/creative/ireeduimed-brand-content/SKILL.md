---
name: ireeduimed-brand-content
description: "Ирээдүймэд (Ireeduimed) brand content system — educational carousels, social posters, and news-style content for OB/GYN pregnancy clinic. Template-driven via KIE image-to-image. Mongolian Cyrillic content targeting pregnant women."
version: 1.0.0
author: Hermes Agent
tags: [ireeduimed, brand-content, educational, carousel, kie-ai, pregnancy, obgyn]
related_skills: [ai-global-brand-content, kie-content-maker, news-poster]
---

# Ирээдүймэд Brand Content System

## Brand Identity

| Field | Value |
|-------|-------|
| Name | Ирээдүймэд (Ireeduimed) |
| Business | Эх ураг эмэгтэйчүүдийн эмнэлэг (OB/GYN clinic) |
| Phone | 7771 0404 |
| Address | 25-р эмийн сан, замын урд, Ялгуун төвийн 3 давхарт |
| Target audience | Жирэмсэн эхчүүд, жирэмсэн болох гэж буй эмэгтэйчүүд |
| Language | Mongolian Cyrillic only |
| Workspace | `/opt/data/social-content/brands/ireeduimed/` |
| Logo | `assets/logos/logo-ireeduimed.jpg` |
| Brand registry | `brand-registry.json` (slug: `ireeduimed`) |

## Catbox URL Expiry Warning

All template reference URLs hosted on `litter.catbox.moe` expire after **72 hours**. Before generating, check that URLs are still valid (`curl -s -o /dev/null -w "%{http_code}" <URL>`). If expired, re-upload the reference images from local files and update the URLs in prompts.

Sources:
- edutemp1 local: `templates/edutemp1/edutemp1-reference.jpg`
- mindtemp1 local: `templates/mindtemp1/mindtemp1-reference.jpg`
- Logo local: `assets/logos/logo-ireeduimed.jpg`

## Verified Educational Content Sources

### Pregnancy Education (edutemp1 content)
- **edoctor.mn** — "Жирэмсэн эхэд өгөх 20 зөвлөгөө": https://edoctor.mn/4113.html
- **NHS UK** — Week-by-week pregnancy guide: https://www.nhs.uk/best-start-in-life/pregnancy/week-by-week-guide-to-pregnancy/
- **CDC Pregnancy**: https://www.cdc.gov/pregnancy/index.html
- **WHO Maternal Health**: https://www.who.int/publications/i/item/9789240080591
- **Cleveland Clinic** — Healthy Pregnancy Guide: https://my.clevelandclinic.org/-/scassets/files/org/obgyn/healthy-pregnancy-guide-20.pdf
- **MedlinePlus Pregnancy**: https://medlineplus.gov/pregnancy.html

### Pregnancy Psychology (mindtemp1 content)
- **ikon.mn** — Б.Баярмаа: "4 жирэмсэн эх тутмын 1 нь сэтгэл гутралд өртөж байна": https://ikon.mn/n/3lvj
- **eclinic.mn** — "Жирэмсэн үеийн сэтгэцийн өөрчлөлтүүд": https://eclinic.mn/patient/blog/170
- **WHO Perinatal Mental Health**: https://www.who.int/teams/mental-health-and-substance-use/promotion-prevention/perinatal-mental-health
- **Cleveland Clinic** — Prenatal Depression: https://my.clevelandclinic.org/health/diseases/22984-prenatal-depression
- **Toronto Therapy Practice** — Coping with emotional changes: https://www.torontotherapypractice.com/blog/how-to-cope-with-physical-and-emotional-changes-during-pregnancy

## Template — edutemp1 (Educational Posters)

The primary template for all Ireeduimed social content.

### Characteristics
- **Dimensions:** 1254×1254 (1:1 square)
- **Format:** JPEG reference image for KIE image-to-image generation
- **Reference URL:** `https://litter.catbox.moe/i9vrtx.jpg` (72h expiry — re-upload if stale)
- **Logo URL:** `https://litter.catbox.moe/atdcff.jpg`
- **Local path:** `templates/edutemp1/edutemp1-reference.jpg`
- **Spec doc:** `templates/edutemp1/template-spec.md`

### 🔒 FIXED Elements (NEVER change)
These MUST be preserved EXACTLY in every generated image:
- **Logo** — Ирээдүймэд logo. NEVER regenerate or modify
- **Background** — design, gradient, colors, texture. NEVER change
- **Layout structure** — all sections, spacing, margins, element positions. NEVER rearrange
- **Contact info** — 7771 0404, 25-р эмийн сан... NEVER change
- **Brand name/positioning** — NEVER change
- **Frames, borders, decorative elements** — keep identical

### ✅ DYNAMIC Elements (can change per post)
1. **HEADLINE** — main title text (the primary dynamic field)
2. **BODY CONTENT** — educational tips, actionable advice in the middle content frame
3. **ILLUSTRATION/VISUAL** — small related image in the content area

### Content Rule (user preference — CRITICAL)
When creating educational posters, **REAL content is mandatory**, not just a headline. Each post must include:
- Meaningful, actionable tips in Mongolian (✅ Фолийн хүчил уух, ✅ Эмчид хандах — type format works well)
- A small related visualization/illustration alongside the text
- Content must be pregnancy/health educational advice, not generic copy

## Carousel Workflow (4-slide)

The user confirmed this approval workflow:

### Step 1: Submit Slide 1 Only
Generate the FIRST slide only, get approval before proceeding.

### Step 2: Wait for Approval
Send the generated image via MEDIA: in Telegram. User reviews and either approves or requests changes.

### Step 3: Generate Slides 2-4
Only after slide 1 approval, generate the remaining 3 slides.

## KIE Image-to-Image Workflow

### Step 1: Upload Template to Temp Hosting
Use catbox.moe for reference image hosting:
```bash
curl -s -F "reqtype=fileupload" -F "time=72h" \
  -F "fileToUpload=@template.jpg" \
  https://litterbox.catbox.moe/resources/internals/api.php
```

### Step 2: Submit Generation Task
```json
{
  "model": "gpt-image-2-image-to-image",
  "input": {
    "prompt": "Create ONE 1:1 square social media poster...",
    "input_urls": ["https://litter.catbox.moe/i9vrtx.jpg"],
    "aspect_ratio": "1:1"
  }
}
```

### Step 3: Poll Until Success
Poll `GET /api/v1/jobs/recordInfo?taskId=<id>` every 10s. Typical generation time: ~65-100s.

### Step 4: Download
- Convert result URL to signed download URL via `POST /api/v1/common/download-url`
- Download with `curl -L -o output.png "<signed_url>"`
- Save to `output/` directory under the brand workspace

### Step 5: Deliver
- Send via MEDIA: path in Telegram
- Wait for approval before generating more slides

## Prompt Construction for Educational Posters

For edutemp1, the prompt structure is:

```
Create ONE 1:1 square social media educational poster (1254x1254) using the attached reference image as the EXACT template background and layout.

CRITICAL - PRESERVE THESE TEMPLATE ELEMENTS:
- Logo — do NOT change, move, or replace the logo
- Background design, colors, gradients — keep EXACTLY as in the template
- Contact information / footer — do NOT change
- Brand name and positioning — do NOT change
- All decorative elements, frames, borders, and layout structure — keep IDENTICAL
- Overall proportions, margins, spacing — preserve exactly

CHANGE these elements:
1. HEADLINE text: "[HEADLINE]" (in the headline/title area)
2. BODY CONTENT AREA — replace with REAL pregnancy tips:
   "✅ [Tip 1]"
   "✅ [Tip 2]"
   "✅ [Tip 3]"
   ...
3. Add a SMALL ILLUSTRATION/IMAGE in the content area — a soft, warm illustration related to the content

Style: Professional medical/healthcare educational poster. Warm, trustworthy, clean. Mongolian Cyrillic text ONLY.
```

## Suggested Educational Topic Categories

1. **Эхний алхамууд** — Just found out you're pregnant
2. **Зөв хооллолт** — Nutrition during pregnancy
3. **Дасгал хөдөлгөөн** — Safe exercise
4. **Хүүхдийн хөгжил** — Baby development by week
5. **Аюултай шинж тэмдэг** — Warning signs to watch
6. **Төрөх бэлтгэл** — Birth preparation
7. **Төрсний дараах** — Postpartum care

## Template — mindtemp1 (Psychology/Mental Health Posters)

A secondary template for Ирээдүймэд psychology/mental health awareness content for pregnant women.

### Characteristics
- **Dimensions:** 1254×1254 (1:1 square)
- **Format:** JPEG reference image for KIE image-to-image
- **Reference URL:** `https://litter.catbox.moe/bpk0hu.jpg` (72h expiry — re-upload if stale)
- **Logo URL:** `https://litter.catbox.moe/atdcff.jpg` (shared with edutemp1)
- **Local path:** `templates/mindtemp1/mindtemp1-reference.jpg`
- **Spec doc:** `templates/mindtemp1/template-spec.md`

### 🔒 FIXED Elements (NEVER change)
Same preservation rules as edutemp1:
- **Logo** — NEVER change, move, or regenerate
- **Background** — NEVER change design/colors
- **Layout structure** — NEVER rearrange
- **Contact info** — 7771 0404, address — NEVER change
- **Brand name** — NEVER change

### ✅ DYNAMIC Elements
1. **HEADLINE** — main title text
2. **BODY CONTENT** — psychology facts, tips, advice in Mongolian
3. **ILLUSTRATION** — small calm/soothing illustration related to mental health

### Verified Psychology Content (Session June 5, 2026)

Key verified facts from Mongolian sources:
- **4 жирэмсэн эх тутмын 1** сэтгэл гутралд өртдөг (Монгол Улсын судалгаа, 2017 — СЭМҮТ)
- Дааврын өөрчлөлтөөс сэтгэл хөдлөл тогтворгүй болох нь хэвийн
- Шинж тэмдэг: амархан уйлах, гомдох, сэтгэл ханах мэдрэмжгүй болох, хүүхдээ төрүүлэхээс айх
- Гэр бүлийн дэмжлэг, нөхрийн халамж, ойлголцол маш чухал
- 5 эмэгтэй тутмын 1 (20%) нь жирэмсэн/төрсний дараах сэтгэл түгшлийн эмгэгтэй (eclinic.mn)

### mindtemp1 Prompt Pattern

For mindtemp1, use this prompt structure with the mindtemp1 reference URL:

```text
Create ONE 1:1 square social media educational poster (1254x1254) using the attached reference image as the EXACT template background and layout.

CRITICAL - PRESERVE THESE TEMPLATE ELEMENTS:
[Same template preservation instructions as edutemp1]

CHANGE these elements ONLY:
1. HEADLINE text: "[PSYCHOLOGY HEADLINE]"
2. BODY CONTENT AREA — replace with these psychology facts and tips:
   "🧠 [Fact/tip 1]"
   "💡 [Fact/tip 2]"
   "💖 [Fact/tip 3]"
   "🌿 [Tip 4]"
   "🩺 [Tip 5]"
3. Add a SMALL ILLUSTRATION — a calm, warm illustration related to mental health

Style: Professional, warm, soothing, trustworthy. Mongolian Cyrillic ONLY.
```

### Suggested Psychology Topic Categories

1. **Сэтгэл хөдлөлийн өөрчлөлт** — Emotional changes during pregnancy
2. **Сэтгэл гутралын шинж тэмдэг** — Signs of prenatal depression
3. **Гэр бүлийн дэмжлэгийн ач холбогдол** — Family support importance
4. **Стресс тайлах аргууд** — Stress management techniques
5. **Өөртөө анхаарал тавих** — Self-care for pregnant women
6. **Тусламж авахаас бүү ай** — Don't be afraid to seek help

## Reference Files

- `references/session-2026-06-05-workflow.md` — Full session transcript and KIE parameters from the first live run (edutemp1 slide 1 creation, user correction on content depth, successful v2 generation)

## Related Skills

- `ai-global-brand-content` — template pattern reference (7-template system, KIE workflow, approval flow)
- `kie-content-maker` — KIE API integration (task submission, polling, download)
- `aiglobal-success-story-carousel` — carousel generation patterns (4-slide structure, student story format)
