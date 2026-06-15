# KIE Image-to-Image Workflow (gpt-image-2-image-to-image)

## When to Use

Use this model when the user wants KIE to generate complete branded slides with:
- Consistent template layout (reference template image sent as visual input)
- Real student/people photos embedded in the output
- Full Mongolian text content baked into the image
- No Pillow compositing (user rejected local compositing)

## API Endpoint

```text
POST https://api.kie.ai/api/v1/jobs/createTask
```

Model name: `gpt-image-2-image-to-image`

## Step 1: Upload Images to KIE File Storage

File upload domain: `https://kieai.redpandaai.co` (NOT api.kie.ai)

```bash
curl -s -X POST 'https://kieai.redpandaai.co/api/file-stream-upload' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -F "file=@/path/to/template-ref.jpg" \
  -F "uploadPath=images/brand-name/templates" \
  -F "fileName=template.jpg"
```

Response includes `downloadUrl` — this is the URL to use in `input_urls`.

## Step 2: Submit Generation Task

```python
import json, os, ssl, urllib.request

payload = json.dumps({
    "model": "gpt-image-2-image-to-image",
    "input": {
        "prompt": "Full slide description with ALL text content...",
        "input_urls": [
            "https://tempfile.redpandaai.co/kieai/.../template.jpg",
            "https://tempfile.redpandaai.co/kieai/.../student.jpg"
        ],
        "aspect_ratio": "1:1"
    }
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.kie.ai/api/v1/jobs/createTask",
    data=payload,
    headers={
        "Authorization": f"Bearer {os.environ['KIE_API_KEY']}",
        "Content-Type": "application/json"
    }
)
ctx = ssl._create_unverified_context()
resp = urllib.request.urlopen(req, context=ctx, timeout=120)
body = json.loads(resp.read().decode("utf-8"))
task_id = body.get("data", {}).get("taskId")
```

## Step 3: Poll and Download

Same as GPT Image 2 text-to-image:

```python
# Poll
req = urllib.request.Request(
    f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
    headers={"Authorization": f"Bearer {os.environ['KIE_API_KEY']}"}
)
resp = urllib.request.urlopen(req, context=ctx, timeout=30)
body = json.loads(resp.read().decode("utf-8"))
state = body.get("data", {}).get("state")

# On success, parse resultJson
result_raw = body.get("data", {}).get("resultJson", "{}")
if isinstance(result_raw, str):
    result_data = json.loads(result_raw)
else:
    result_data = result_raw
kie_url = result_data.get("resultUrls", [])[0]

# Convert to signed download URL
dl_req = urllib.request.Request(
    "https://api.kie.ai/api/v1/common/download-url",
    data=json.dumps({"url": kie_url}).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {os.environ['KIE_API_KEY']}",
        "Content-Type": "application/json"
    }
)
dl_resp = urllib.request.urlopen(dl_req, context=ctx, timeout=60)
dl_body = json.loads(dl_resp.read().decode("utf-8"))
signed_url = dl_body["data"]  # string, not dict

# Download
img_resp = urllib.request.urlopen(urllib.request.Request(signed_url), context=ctx, timeout=120)
with open("output.jpg", "wb") as f:
    f.write(img_resp.read())
```

## Prompt Construction Pattern

### Layout Description (embed in every prompt)

```
Create ONE separate 1:1 square social media carousel slide.
Use the attached reference image for style guidance.
This is Slide {N} of 4 -- {Slide Label}.
Layout: light cream/off-white background (#FAFAF8), Italian minimal aesthetic, clean airy style.
Top-left: small gold (#D7AB46) pill badge saying "{BADGE_TEXT}".
Top-right: small AI Global luxury logo (black+gold, square, about 15% width).
Bottom-left: gray text "📞 89097454  🌐 aiglobal.mn" in clean font.
Bottom: thin gold (#D7AB46) divider line.
LEFT SIDE (55%): Large bold headline "{HEADLINE}" in dark charcoal (#1A1A1A), 3 lines max.
RIGHT SIDE (38%): Place the attached photo in a rounded rectangle with thin gold border.
Magazine quality, professional, clean.
Mongolian Cyrillic text ONLY. NO English text.
```

### Per-Slide Specifics

**Slide 1 (Student Introduction):**
```
Below: student name "{NAME}" in gold (#D7AB46), then age "{AGE}" in gray, then occupation "{OCCUPATION}" in gray.
Quote: "{QUOTE}" in italic gray.
Input images: template reference + student portrait photo
```

**Slide 2 (Before):**
```
Section heading: "ӨМНӨ НЬ" in gold, smaller.
Three problem items with ❌ prefix:
❌ {problem_1}
❌ {problem_2}
❌ {problem_3}
Input images: template reference only (KIE generates the struggle visual)
```

**Slide 3 (Transformation):**
```
Section heading: "ХУВИРАЛ" in gold, smaller.
Three achievement items with ✅ prefix:
✅ {week_1}
✅ {week_2}
✅ {week_3}
Input images: template reference only (KIE generates success visual)
```

**Slide 4 (Results and CTA):**
```
Three metric items in large gold (#D7AB46) text:
{METRIC_1}
{METRIC_2}
{METRIC_3}
Bottom CTA: "{CTA}" in dark charcoal.
Input images: template reference only (KIE generates dashboard/result visual)
```

## Observed Behavior

- Generation time: ~50-100s per slide (avg ~60s)
- File size: ~1.3MB per 1080x1080 JPEG
- The model renders the reference template style faithfully
- Mongolian Cyrillic text in prompts renders into the image text correctly (QA still recommended)
- Real portrait photos are placed as described in the prompt layout
- input_urls can contain 1-2 images (template + optional photo)

## Known Pitfalls

1. **Data URLs not supported** — `input_urls` requires uploaded URLs (tempfile.redpandaai.co). Base64 data URLs cause "File type not supported" errors.
2. **Upload domain differs** — File upload is at `kieai.redpandaai.co`, API requests are at `api.kie.ai`.
3. **input_urls may affect cost** — Each image in input_urls counts toward API processing.
4. **Mongolian text QA required** — The model usually handles embedded Cyrillic, but always check output for misspellings.
5. **Logo accuracy** — The model will generate a logo resembling the reference, not the exact official logo. For pixel-perfect logo, the image-to-image approach with reference template is best.
