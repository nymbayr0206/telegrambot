# News Post 1 — Worked Example

## Session: 2026-06-05

First test of the `news-post-1` template. Result: ✅ Success (74s generation, 6 credits)

## News Source

| Field | Value |
|-------|-------|
| Title | Apple approves Poke as the first AI agent on its Messages for Business platform |
| Source | TechCrunch AI |
| URL | https://techcrunch.com/2026/06/04/apple-approves-poke-as-the-first-ai-agent-on-its-messages-for-business-platform/ |
| Date | 2026-06-04 |

## Mongolian Summary

**Headline:** Apple Messages дээр анхны AI agent

**Body (3 lines):**
- Poke startup нь Apple-ийн Messages for Business дээр зөвшөөрөгдсөн анхны AI agent боллоо
- Хэрэглэгчид энгийн текст мессежээр AI agent ашиглах боломжтой
- AI agent бизнесийн харилцааг бүрэн автоматжуулж, үйлчлүүлэгчид 24/7 туслах боломж

## Template Reference

| Item | Location |
|------|----------|
| Template image | `/opt/data/social-content/brands/ai-global/templates/news-post-1/assets/template-reference.jpg` |
| KIE tmpfiles URL | `https://tmpfiles.org/dl/wlw66eagSUkd/template-reference.jpg` |
| Template spec | `templates/news-post-1/template-spec.md` |
| Test output | `templates/news-post-1/test_post_1.jpg` |
| Test metadata | `templates/news-post-1/test_post_1_metadata.json` |

## KIE Prompt Used

```json
{
  "model": "gpt-image-2-image-to-image",
  "input": {
    "prompt": "Create ONE separate 1:1 square social media news poster. Use the attached reference image for EXACT layout and style guidance.\n\nIMPORTANT - LOCKED ELEMENTS (MUST keep these EXACTLY as in the reference, DO NOT change):\n- Top area: DO NOT change the AI Global logo\n- \"AI TECH NEWS\" branding bar in the upper-middle: DO NOT change this text\n- Bottom dark footer bar: DO NOT change the text \"8909 7454\", \"Ayud tower 601 TooT\", \"www.aiglobal.mn\"\n- Keep the gold/amber background color exactly as in the reference\n- Keep the gold and dark color scheme\n- Keep the bottom dark bar design exactly as in the reference\n\nDYNAMIC ELEMENTS - Replace these with NEW Mongolian text:\n- HEADLINE (large bold text in the upper-middle area, position ~y=18-35%): \"Apple Messages дээр анхны AI agent\"\n- BODY TEXT (in the lower-middle area above the dark footer bar, ~y=35-88%):\n  \"Poke startup нь Apple-ийн Messages for Business дээр зөвшөөрөгдсөн анхны AI agent боллоо\"\n  \"Хэрэглэгчид энгийн текст мессежээр AI agent ашиглах боломжтой\"\n  \"AI agent бизнесийн харилцааг бүрэн автоматжуулж, үйлчлүүлэгчид 24/7 туслах боломж\"\n\nStyle: Professional news poster, modern, clean. Dark text on gold/amber background. Mongolian Cyrillic text ONLY. Magazine quality, crisp typography, premium finish.",
    "input_urls": [
      "https://tmpfiles.org/dl/wlw66eagSUkd/template-reference.jpg"
    ],
    "aspect_ratio": "1:1"
  }
}
```

## KIE Result

| Property | Value |
|----------|-------|
| Task ID | `b62cb4759b57b7fa64843d93d9096b1c` |
| State | `success` |
| Cost | 6 credits |
| Generation time | 74 seconds |
| Output URL | `https://tempfile.aiquickdraw.com/images/chatgpt/b62cb4759b57b7fa64843d93d9096b1c_6b292517c6dd404283c4dfdd82411e2b.png` |
| Local file | `test_post_1.jpg` (1024x1024, RGB) |

## Key Pattern for Future Runs

1. **Fetch news** → RSS pipeline (TechCrunch AI)
2. **Pick one story** → most relevant for Mongolian audience
3. **Summarize in Mongolian** → keep headline SHORT (2-5 words), body to 3 bullet lines max
4. **Upload template to tmpfiles.org** → get fresh URL each session (URLs may expire)
5. **Construct KIE image-to-image prompt** → LOCKED elements first ("DO NOT change"), then DYNAMIC elements
6. **Submit, poll, download** → ~74s typical generation time
7. **Deliver via MEDIA: path** in Telegram

## OCR Technique (When Vision Unavailable)

When the active model (DeepSeek) doesn't support image input, use easyocr:
```python
import easyocr
reader = easyocr.Reader(['en', 'mn'], gpu=False)
results = reader.readtext('/path/to/template.jpg')
for (bbox, text, conf) in results:
    print(f"[{conf:.0f}%] {text}")
```

Also use PIL pixel analysis to understand layout:
```python
from PIL import Image
img = Image.open('/path/to/template.jpg')
# Sample color bands at different heights
for y_pct in range(0, 100, 2):
    y = int(img.height * y_pct / 100)
    # ... analyze pixel brightness/color
```
