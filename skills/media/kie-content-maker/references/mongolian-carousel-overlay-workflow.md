# KIE Nano Banana 2 + Deterministic Mongolian Carousel Overlay Pattern

Use this pattern for Mongolian branded healthcare/social carousels, especially Supernova.

## Why

Nano Banana 2 can create strong visual backgrounds, but non-English/Mongolian Cyrillic text and exact brand element placement are best rendered locally. This keeps spelling, phone numbers, logo placement, and slide numbering deterministic.

## Pattern

1. Create a slide-by-slide JSON brief with:
   - `headline`
   - `body`
   - `visual_prompt`
   - caption and campaign metadata
2. For each slide, submit Nano Banana 2 background generation with strict text suppression:
   - `NO TEXT`
   - `NO LETTERS`
   - `NO RANDOM LOGO`
   - `NO WATERMARK`
3. Poll `/api/v1/jobs/recordInfo?taskId=...` until output URLs appear.
4. If output URLs are inside `data.resultJson`, parse that string as JSON and read `resultUrls`.
5. Download outputs immediately; temporary URLs can expire.
6. Use Pillow/HTML/SVG to overlay:
   - fixed brand phrase
   - logo
   - phone
   - slide number
   - headline/body copy
   - brand accent lines/panels
7. Create a contact sheet for QA and a ZIP for all final slides.
8. Save metadata next to final slides: source, topic, caption, approval status, asset paths, QA notes.

## Supernova example paths

- Draft JSON: `/opt/data/social-content/brands/supernova/drafts/carousel-01-why-aging-different-copy.json`
- KIE generator script: `/opt/data/social-content/brands/supernova/scripts/generate_carousel_01_kie.py`
- Overlay script: `/opt/data/social-content/brands/supernova/scripts/overlay_carousel_01.py`
- Final output folder: `/opt/data/social-content/brands/supernova/generated/carousel-01-why-aging-different/final/`

Do not store `KIE_API_KEY` in any generated script or final response. Load it from the environment or `/opt/data/.env` without printing it.
