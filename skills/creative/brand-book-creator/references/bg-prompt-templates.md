# GPT Image 2 Prompt Examples for Brand Book Backgrounds

Use these as **prompt templates** for KIE GPT Image 2 (`gpt-image-2-text-to-image`).
Replace `[BRAND_COLORS]`, `[INDUSTRY]`, `[VIBE]` with actual values from logo analysis.

## 📁 Prompt File Structure

Write each prompt to a temp JSON file before calling curl (Cyrillic-safe pattern):

```python
import json, os, subprocess, time

def generate_background(bg_type, brand_colors, industry, vibe, aspect_ratio="16:9"):
    prompts = {
        "educational": f"""Text-free background for a poster. NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS.

Style: Educational, knowledge-sharing, seminar vibe. Clean bright atmosphere.
Colors: {brand_colors}
Industry: {industry}
Vibe: {vibe}

Design elements:
- Soft warm gradient background with geometric accent shapes (circles, light bulbs, abstract book shapes)
- Clean negative space in center/upper-center for future text placement
- Subtle grid or dot pattern texture
- Bright, airy, inspiring atmosphere — like a TED talk or workshop backdrop
- No people, no faces, no hands
- Landscape 16:9 composition, high resolution""",

        "industry_leader": f"""Text-free background for a poster. NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS.

Style: Premium, authoritative, industry-leader vibe. Professional and powerful.
Colors: {brand_colors}
Industry: {industry}
Vibe: {vibe}

Design elements:
- Rich dark tones or deep premium colors as base
- Gold/copper foil accent lines or subtle geometric patterns
- Sleek diagonal or layered architectural shapes
- Abstract trophy/crown/mountain silhouette shapes in background
- Negative space in center for text placement
- No people, no faces, no hands
- Landscape 16:9 composition, high resolution""",

        "sales_promotion": f"""Text-free background for a poster. NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS.

Style: Energetic, promotional, CTA-focused sales vibe. Attention-grabbing.
Colors: {brand_colors}
Industry: {industry}
Vibe: {vibe}

Design elements:
- Vibrant dynamic gradient with contrast arrows or burst shapes
- Abstract discount ribbons, star bursts, or price-tag shapes as subtle background texture
- Energetic diagonal lines or speed lines suggesting urgency
- Circular spotlight or glow effect centered for product placement
- Negative space for promotional text/CTA
- No people, no faces, no hands
- Landscape 16:9 composition, high resolution"""
    }
    return prompts[bg_type]
```

## Submission Pattern (Python, Cyrillic-safe)

```python
import json, urllib.request, ssl, time

KIE_API_KEY = os.environ["KIE_API_KEY"]

def generate_bg(prompt, label="background"):
    """Submit to KIE GPT Image 2, poll until done, return local file path."""
    payload = {
        "model": "gpt-image-2-text-to-image",
        "input": {"prompt": prompt, "aspect_ratio": "16:9"}
    }
    req = urllib.request.Request(
        "https://api.kie.ai/api/v1/jobs/createTask",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {KIE_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    ctx = ssl.create_default_context()
    resp = json.loads(urllib.request.urlopen(req, context=ctx, timeout=60).read())

    task_id = resp.get("data", {}).get("taskId") or resp.get("data", {}).get("recordId")
    if not task_id:
        raise RuntimeError(f"No task ID in response: {resp}")

    # Poll
    for _ in range(36):  # 6 min max
        poll_url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"
        poll_req = urllib.request.Request(
            poll_url, headers={"Authorization": f"Bearer {KIE_API_KEY}"}
        )
        poll_resp = json.loads(urllib.request.urlopen(poll_req, context=ctx, timeout=30).read())

        state = poll_resp.get("data", {}).get("state", "")
        if state == "success":
            # Extract result URL
            result_json = poll_resp.get("data", {}).get("resultJson", "{}")
            if isinstance(result_json, str):
                result_data = json.loads(result_json)
            else:
                result_data = result_json
            urls = result_data.get("resultUrls", [])
            if urls:
                return download_kie_url(urls[0], f"{label}.jpg")
            raise RuntimeError(f"No resultUrls in: {result_data}")
        elif state == "failed":
            raise RuntimeError(f"Generation failed: {poll_resp}")
        time.sleep(10)

    raise TimeoutError(f"Background '{label}' did not finish in 6 minutes")
```

## Timing Tips

| Step | Duration |
|------|----------|
| 1 bg generation | ~2–3 min |
| 3 bgs sequentially | ~7–10 min total |
| Composite via Pillow | < 5 sec |
| **Total** | **~10 min** |
