# Session Workflow — June 5, 2026

## Context
First live run for Ирээдүймэд brand. Created edutemp1 template, generated slide 1 of educational carousel.

## User Correction (Important)
First attempt only changed the headline. User rejected it — they want **real content in the body** with actionable tips and a related image. This became the content rule in the main skill.

## KIE Parameters (Successful v2 Run)

**Task ID:** `68098a6562f658768022bbff588fea8c`
**Model:** `gpt-image-2-image-to-image`
**Reference URL:** `https://litter.catbox.moe/i9vrtx.jpg`
**Generation time:** ~100 seconds (10 polls at 10s intervals)
**Credits:** 6
**Output file:** `edutemp1_slide1_v2.png` (1.2MB, 1254x1254)

### v2 Prompt (worked)

Full prompt text sent to KIE:

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
1. HEADLINE text: "Жирэмсэн гэдгээ мэдсэн үү?" (in the headline/title area)
2. BODY CONTENT AREA — replace with these REAL pregnancy tips in a clean list:
   "✅ Фолийн хүчил, Д витамин уух"
   "✅ Эмчид хандаж үзлэгт хамрагдах"
   "✅ Тамхи, архинаас татгалзах"
   "✅ Эрүүл хооллолт, хангалттай ус"
   "✅ Стрессгүй, тайван байх"
3. Add a SMALL ILLUSTRATION/IMAGE in the content area — a simple, soft, warm illustration of a pregnant woman's silhouette or a baby ultrasound or a maternal health icon. The illustration should be small, tasteful, and placed alongside the text tips.

Style: Professional medical/healthcare educational poster. Warm, trustworthy, clean. Mongolian Cyrillic text ONLY. The tips text should be clearly readable.

Do NOT add any other new elements. Keep all template framing, logo, footer exactly as in the reference.
```

## Download Pattern

```bash
# Get signed URL
SIGNED=$(curl -s --location "https://api.kie.ai/api/v1/common/download-url" \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"$RESULT_URL\"}")

# Extract data field (it's a string, not an object)
DOWNLOAD_URL=$(echo "$SIGNED" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',''))")

# Download with redirect following
curl -L -o /opt/data/social-content/brands/ireeduimed/output/edutemp1_slide1_v2.png "$DOWNLOAD_URL"
```

## Image URLs (catbox.moe — 72h expiry)
- edutemp1: https://litter.catbox.moe/i9vrtx.jpg
- Logo: https://litter.catbox.moe/atdcff.jpg
- v2 output: /opt/data/social-content/brands/ireeduimed/output/edutemp1_slide1_v2.png
