# Template Markers → KIE GPT Image 2 Full-Prompt Pattern

When there is no template API endpoint that accepts `template_id` + markers separately, submit the complete poster prompt to KIE GPT Image 2.

## Workflow

### 1. Generate Template Markers & Image Prompts

Follow the standard marker rules per template type (industry_update, success_story, etc.).

### 2. Construct the Full KIE Prompt

Combine everything into ONE comprehensive prompt that describes:

```
"Create a ONE single 1:1 square social media carousel slide poster for AI Global.

BRAND STYLE:\n- Background: See live style authority at `/opt/data/social-content/brands/ai-global/carousel-prompt-instructions.md`. As of June 2026: light blue gradient (#E8F4FD → #D6EAF8). **Do NOT default to cream/off-white without checking the live doc.**\n- Typography: Clean modern sans-serif, charcoal (#1A1A1A) for headlines, gold (#D7AB46) for accents\n- Premium, modern, educational technology brand feel

LAYOUT (top to bottom):
- TOP-LEFT: Gold pill/badge [TYPE LABEL in white on gold background]
- TOP-RIGHT: AI Global brand logo (simple minimal text)
- MAIN HEADLINE: [headline text] in charcoal bold
- SUBHEADLINE: [subheadline text] in medium gray
- TREND 1 with icon: [trend_1 text] in charcoal
- TREND 2 with icon: [trend_2 text] in charcoal
- TREND 3 with icon: [trend_3 text] in charcoal
- HERO VISUAL: [hero_visual_prompt description]
- BOTTOM: Thin gold divider line
- BOTTOM-LEFT: Contact "89097454  aiglobal.mn" in small gray text
- CTA: [cta_text] in gold accent

IMPORTANT:
- Mongolian Cyrillic or latin-transliterated Mongolian text
- Clean sans-serif font
- Airy design with generous whitespace
- Gold (#D7AB46) accent color
- No watermarks, no extra logos"
```

### 3. Submit to KIE

Write the prompt to a JSON file (to handle UTF-8 Mongolian text without shell encoding issues):

```python
import json

prompt_data = {
    "model": "gpt-image-2-text-to-image",
    "input": {
        "prompt": "<full_prompt_text>"
    }
}

with open("/tmp/kie_prompt.json", "w", encoding="utf-8") as f:
    json.dump(prompt_data, f, ensure_ascii=False, indent=2)
```

Then submit via curl:

```bash
curl -s --location 'https://api.kie.ai/api/v1/jobs/createTask' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d @/tmp/kie_prompt.json
```

### 4. Poll for Completion

```bash
for i in $(seq 1 30); do
  resp=$(curl -s "https://api.kie.ai/api/v1/jobs/recordInfo?taskId=<TASK_ID>" \
    -H "Authorization: Bearer $KIE_API_KEY")
  state=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('state','unknown'))")
  if [ "$state" = "success" ]; then
    echo "$resp" | python3 -c "
import sys, json
d = json.load(sys.stdin)
rj = d.get('data', {}).get('resultJson', '{}')
if isinstance(rj, str):
    import json as j2
    rd = j2.loads(rj)
else:
    rd = rj
for u in rd.get('resultUrls', []):
    print(f'RESULT_URL: {u}')"
    break
  fi
  sleep 10
done
```

### 5. Download Image

Use Python urllib with SSL workaround (required on this server):

```python
import urllib.request, json, ssl

ctx = ssl._create_unverified_context()
api_key = "read from env"

# Convert KIE tempfile URL to signed download URL
req = urllib.request.Request(
    "https://api.kie.ai/api/v1/common/download-url",
    data=json.dumps({"url": "<KIE_TEMPFILE_URL>"}).encode(),
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req, context=ctx, timeout=60)
body = json.loads(resp.read())
signed_url = body["data"]  # Note: data is a STRING (the download URL), not a dict

# Download
req2 = urllib.request.Request(signed_url, headers={"User-Agent": "Mozilla/5.0"})
resp2 = urllib.request.urlopen(req2, context=ctx, timeout=120)
with open("/path/to/output.png", "wb") as f:
    f.write(resp2.read())
```

## Image Quality

GPT Image 2 generation takes ~2-5 minutes per slide. Observed:
- Fast cases: ~90s
- Typical: ~3-4 minutes (18-24 polls × 10s)
- Some cases: stuck in "waiting" for 10+ polls then advance to "generating"

If a task is stuck >10 minutes, submit a fresh task with slightly simplified prompt rather than waiting indefinitely.

## Important Constraints

- **KIE_API_KEY** is in shell env, NOT in execute_code Python env. Use terminal tool with curl or Python subprocess.
- **SSL verification fails** on api.kie.ai — use `ssl._create_unverified_context()` in Python.
- **Download URL expires** (~20 min) — download immediately after getting it.
- **resultJson** is a JSON-encoded string, not a dict. Parse it.
- **download-url response**: `data` field is a STRING (the signed URL), not an object.
- For Mongolian text: use latin transliteration to avoid encoding issues, or write prompt to JSON file (not inline shell).
