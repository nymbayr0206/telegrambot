# KIE GPT Image 2 notes

Session-derived notes for using KIE.AI GPT Image 2 for brand carousel/poster generation.

## Endpoint and model

Use the standard KIE marketplace job endpoints:

```http
POST https://api.kie.ai/api/v1/jobs/createTask
GET  https://api.kie.ai/api/v1/jobs/recordInfo?taskId=...
```

Request body for text-to-image:

```json
{
  "model": "gpt-image-2-text-to-image",
  "input": {
    "prompt": "...",
    "aspect_ratio": "1:1"
  }
}
```

Auth:

```http
Authorization: Bearer $KIE_API_KEY
Content-Type: application/json
```

Do not persist the API key in scripts or skill files. Load from environment or `/opt/data/.env` if that is already the user's secret store.

## Why use GPT Image 2 for carousels

Use this model when the user wants the whole poster design to match a visual reference, including:

- rounded bold typography feel,
- phone capsule/frame,
- logo placement/card,
- footer waves,
- red/blue brand style,
- social-media infographic polish.

This model produced a closer Supernova carousel style than the deterministic Pillow overlay with DejaVu Sans. The user explicitly preferred GPT Image 2 for future carousels across brands when style/font fidelity matters.

## Separate-slide prompting

When creating a carousel for Make.com/Facebook, generate each slide as a separate image. Include this in every prompt:

```text
Create ONE separate 1:1 square social media carousel slide, not a collage and not four slides in one image.
Generate only this single slide N/4 as a final poster image.
```

Avoid sending contact sheets to webhook publishers. Contact sheets are only for QA previews when the user asks.

## Mongolian text QA

GPT Image 2 can render Mongolian/Cyrillic text with better style than local overlay, but text can still be wrong. Before publishing or webhook autopost:

1. Visually inspect every slide.
2. Check title, body, slide number, logo card, and phone capsule.
3. Confirm fixed Supernova strings are correct:
   - `Мэдлэгт дусал нэмэр`
   - `Утас: 70000303`
4. If a word is misspelled, regenerate that slide rather than trying to publish.

If exact text control is more important than style fidelity, use a text-free image + local overlay workflow instead.

## Webhook upload pattern

For Make.com carousel publishing, send multipart form data:

```bash
curl -sS -X POST "$MAKE_WEBHOOK_URL" \
  -F 'brand=supernova' \
  -F 'campaign=Telomer Effect Ebook Carousel Series' \
  -F 'carousel_number=2' \
  -F 'topic=Consequences of premature cellular aging' \
  -F 'model=gpt-image-2-text-to-image' \
  -F 'language=mn' \
  -F 'format=1:1 square carousel' \
  -F 'caption=...' \
  -F 'slide1=@/path/slide-01.jpg;type=image/jpeg' \
  -F 'slide2=@/path/slide-02.jpg;type=image/jpeg' \
  -F 'slide3=@/path/slide-03.jpg;type=image/jpeg' \
  -F 'slide4=@/path/slide-04.jpg;type=image/jpeg' \
  -w '\nHTTP_STATUS:%{http_code}\n'
```

Treat `HTTP_STATUS:200` plus an accepted response as success. For stateful daily automation, increment `next_carousel` only after success.

## Polling and result parsing

The create response contains `data.taskId`/`recordId`. Poll `recordInfo` until the response contains output URLs. Results may appear in nested JSON/stringified fields such as `resultJson` or `response`; parse those fields explicitly instead of only regexing the top-level response.

## CRITICAL: JSON temp-file technique for Mongolian/Cyrillic prompts

Shell escaping will BREAK any `curl` command that includes Mongolian Cyrillic text in the JSON body. This includes `-d '{"prompt": "Монгол текст..."}'` — the shell will mangle Cyrillic characters before curl sees them.

**Always** write the JSON to a temp file and use `@file`:

```python
import json, os

payload = {
    "model": "gpt-image-2-text-to-image",
    "input": {
        "prompt": "ONE separate 1:1 square social media carousel slide. Mongolian text here...",
        "aspect_ratio": "1:1"
    }
}

tmpfile = "/opt/data/supernova_automation/tmp_payload.json"
os.makedirs(os.path.dirname(tmpfile), exist_ok=True)
with open(tmpfile, 'w', encoding='utf-8') as f:
    json.dump(payload, f)

import subprocess
result = subprocess.run([
    "curl", "-sS", "-X", "POST",
    "https://api.kie.ai/api/v1/jobs/createTask",
    "-H", "Authorization: Bearer $KIE_API_KEY",
    "-H", "Content-Type: application/json",
    "-d", f"@{tmpfile}"
], capture_output=True, text=True)
os.unlink(tmpfile)
```

Even when using Python's `urllib.request` (which handles Cyrillic natively), the temp-file approach is the simplest and most portable pattern for cron scripts that may run in restricted environments.

## Timing reference

| Step | Time |
|---|---|
| Task creation | < 1s |
| GPT Image 2 generation (medium quality) | ~3 min per slide |
| Poll interval | 10s |
| Max attempts | 30 (5 min) |
| Download + cleanup | < 5s |
