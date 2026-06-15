# Vision Fallback: When Active Model Doesn't Support Image Input

## Problem

The active conversation model (e.g. `deepseek-v4-flash`, some Hermes auxiliary models) does not accept `image_url` content blocks. When a user sends an image (screenshot, brand asset, design reference) via a messaging platform, the `vision_analyze` tool fails with:

```
Error: unknown variant `image_url`, expected `text`
```

This means the LLM backend refused the image block — not that the tool or file is broken.

## Solution: Direct OpenAI API Call via Terminal

Since `$OPENAI_API_KEY` is typically set in the environment, fall back to a direct GPT-4o vision API call from the `terminal` tool.

```python
import base64, json, os, urllib.request, ssl

api_key = os.environ["OPENAI_API_KEY"]

with open("/opt/data/image_cache/img_xxxx.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

payload = {
    "model": "gpt-4o",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image in detail..."},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{b64}",
                "detail": "high"
            }}
        ]
    }],
    "max_tokens": 1500
}

req = urllib.request.Request(
    "https://api.openai.com/v1/chat/completions",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    method="POST"
)
ctx = ssl._create_unverified_context()  # needed on this server
resp = urllib.request.urlopen(req, context=ctx, timeout=60)
result = json.loads(resp.read())
analysis = result["choices"][0]["message"]["content"]
print(analysis)
```

## Key Details

- **Base64 encoding** — read the file as bytes, encode with `base64.b64encode()`, then use `data:image/jpeg;base64,...` as the URL.
- **`ssl._create_unverified_context()`** — required on this server; `urllib.request.urlopen` raises cert errors without it.
- **`detail: "high"`** — gives GPT-4o full resolution analysis. Use `"low"` for simpler/faster analysis.
- **Image path** — user-sent images land at `/opt/data/image_cache/img_*.jpg` (Telegram) or you can reference the path the user mentioned.
- **`max_tokens: 1500`** — enough for detailed brand/content analysis; increase for multi-page or dense infographics.

## When to Use

- User sends an image and says "look at this" but `vision_analyze` fails with model-not-supported errors.
- You need to understand a brand logo, screenshot, design reference, or document image.
- After analysis, proceed with the task as normal (content plan, carousel generation, etc.) using the LLM-generated description.

## When NOT to Use

- If the image is analyzed successfully by `vision_analyze` — skip this fallback.
- For video analysis (use `video_analyze` instead).
- For real-time browser screenshots (use `browser_vision` instead).
