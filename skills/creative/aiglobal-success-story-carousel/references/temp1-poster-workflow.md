# temp1 AI Global Poster Workflow (June 2, 2026)

## Context

User requested an **AI Vibe Coder salary research poster** using the **temp1 background template**. First attempt failed (text-only description in GPT Image 2 prompt = unbranded output). Fixed by uploading temp1 to KIE file storage and using `input_urls` with `gpt-image-2-image-to-image`.

## Source Files

- **Template:** `/opt/data/social-content/brands/ai-global/assets/backgrounds/temp1.jpg`
- **Mounted at:** `assets/backgrounds/temp1.jpg` relative to brand root
- **Dimensions:** 1254x1254 (1:1 square)

## Exact Workflow Executed

### 1. Upload temp1 to KIE File Storage

```bash
curl -s -X POST 'https://kieai.redpandaai.co/api/file-stream-upload' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -F "file=@/opt/data/social-content/brands/ai-global/assets/backgrounds/temp1.jpg" \
  -F "uploadPath=images/aiglobal-templates" \
  -F "fileName=temp1-bg.jpg"
```

Returns:
```json
{
  "data": {
    "downloadUrl": "https://tempfile.redpandaai.co/kieai/327934/images/aiglobal-templates/temp1-bg.jpg"
  }
}
```

### 2. Submit Image-to-Image Task

```python
payload = {
    "model": "gpt-image-2-image-to-image",
    "input": {
        "prompt": "Create ONE single 1:1 square poster using the attached reference image as the exact background template. Keep the EXACT same background design, gradient, texture, and layout structure from the reference image. Do NOT change the background. ... [full content prompt with AI Global branding, data sections, Mongolian text]",
        "input_urls": ["https://tempfile.redpandaai.co/kieai/327934/images/aiglobal-templates/temp1-bg.jpg"],
        "aspect_ratio": "1:1"
    }
}
# POST to https://api.kie.ai/api/v1/jobs/createTask
# Task ID returned: 6c550ffb2290a25ee56b726982b08537
```

### 3. Poll for Result (Python)

```python
import ssl, json, urllib.request, time
ssl._create_default_https_context = ssl._create_unverified_context

TASK_ID = "6c550ffb2290a25ee56b726982b08537"
for i in range(20):
    req = urllib.request.Request(
        f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={TASK_ID}",
        headers={"Authorization": f"Bearer {KIE_KEY}"}
    )
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    state = data["data"]["state"]
    if state == "success":
        result_url = json.loads(data["data"]["resultJson"])["resultUrls"][0]
        print(result_url)  # https://tempfile.aiquickdraw.com/images/chatgpt/file_xxx.png
        break
    elif state == "failed":
        raise Exception(f"Failed: {data}")
    time.sleep(6)
```

Had to poll ~13 rounds (78s) before success.

### 4. Download Result

Direct download with `curl -L` (the `/api/v1/common/download-url` endpoint returned 422 for this URL):

```bash
curl -Lv "https://tempfile.aiquickdraw.com/images/chatgpt/file_0000000059c071fd8fdf17cd9617b460.png" \
  -o /opt/data/social-content/brands/ai-global/outputs/ai-vibe-coder-salary-poster-v3.png
```

Result: 1.6MB PNG, 1:1 square, branded with temp1 background + AI Global styling.

## Prompt Strategy That Worked

The successful prompt had these exact components:

1. **Template preservation directive** (first sentence):
   "Create ONE single 1:1 square poster using the attached reference image as the exact background template. Keep the EXACT same background design, gradient, texture, and layout structure from the reference image. Do NOT change the background."

2. **Brand identity** (explicit):
   - "Add AI Global luxury logo (black + gold, professional, small)"
   - "Black and gold color scheme matching AI Global brand"
   - Contact: "89097454  aiglobal.mn" at bottom

3. **Content sections** (data-driven):
   - Title in gold
   - Statistics in dark boxes/sections
   - Dollar amounts, percentages
   - Certificate info (ISO/IEC 17024:2012)

4. **Language constraint** (final sentence):
   "Mongolian Cyrillic ONLY."

## What Failed

**First attempt:** Used GPT Image 2 (not image-to-image) with a text description of temp1:
> "Dark gradient background, dark blue/navy top, lighter blue center, dark bottom with gold accent"
> Result: unbranded, didn't match temp1 at all. User: "enә poster manai branded tohirohgui bna"

**Fix:** Switched to `gpt-image-2-image-to-image` model + `input_urls` with uploaded temp1 URL.

## Key Lesson

**For this user: NEVER describe temp1 in text. Always upload and reference via image-to-image.**
