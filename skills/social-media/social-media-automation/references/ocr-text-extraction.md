# OCR Text Extraction — No Library Workaround

When a client sends an image containing text (flyer, poster, course info, contact card, PDF screenshot) and no OCR libraries are installed (no tesseract, no Pillow, no easyocr), use the **OCR.space free API** as a fallback.

## Prerequisites

- Python 3 stdlib only (urllib, base64, json)
- Internet access (the API is a remote endpoint)
- No API key needed — the demo key `helloworld` works for basic use

## Technique

Convert the image to base64 and POST to OCR.space's free tier:

```python
import json, urllib.request, urllib.parse, base64

with open('/path/to/image.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

data = urllib.parse.urlencode({
    'base64Image': f'data:image/jpeg;base64,{img_b64}',
    'language': 'eng',          # OCR language (eng works for Mongolian Cyrillic too)
    'OCREngine': '2',           # Engine 2 = better accuracy
}).encode()

req = urllib.request.Request(
    'https://api.ocr.space/parse/image',
    data=data,
    headers={
        'apikey': 'helloworld',  # Free demo key
        'Content-Type': 'application/x-www-form-urlencoded'
    }
)

resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read())

if result.get('ParsedResults'):
    text = result['ParsedResults'][0].get('ParsedText', '')
    print(text)
```

## Handling Cyrillic/Mongolian text

OCR.space Engine 2 handles Mongolian Cyrillic reasonably well. Common OCR errors to watch for:

| Intended | OCR output |
|----------|-----------|
| бүх | бух |
| зөвлөх | зевлех |
| өглөөний | оглеений |
| өдрийн | одрийн |
| бүртгүүлэх | буртгуулэх |

Always review and correct Mongolian text after extraction.

## When to use this

- Client sent a **course flyer** with dates, instructor names, prices
- Client sent a **business card** or contact card
- Client sent a **promotional poster** with text that should be re-used in captions
- Any image where the text content needs to be extracted, referenced, or re-purposed

## Save source alongside extraction

After extracting text, save both the **original image** and **extracted text as .md** in a predictable location:

```
brand/<slug>/assets/references/
  original-flyer.jpg       # source image
  original-flyer.md        # markdown with cleaned text
```

## Alternatives if OCR.space fails

1. **Try smaller image** — compress/resize if the file is very large (300KB+)
2. **Try OCREngine=1** — older engine, sometimes better with specific layouts
3. **Google Vision API** — needs a GCP project + billing, but much more accurate
4. **Ask the user to retype the text** — fallback when all APIs fail

## Key pitfalls

- **No pip/sudo?** OCR.space works with Python stdlib only — no dependencies needed
- **Rate limits** — the free `helloworld` key allows ~500 requests/day
- **Image too large** — error 400 may mean the base64 payload exceeds limits; consider sending a smaller JPEG
- **Mongolian OCR quality** — good but not perfect; always manually QA extracted Mongolian text before using it in content
