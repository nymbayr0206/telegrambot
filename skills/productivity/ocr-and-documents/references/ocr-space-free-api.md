# OCR.space Free API — Zero-Dependency OCR Fallback

## When to Use

When no local OCR tools are installed (no tesseract, no marker-pdf, no pip), and you need to extract text from a JPEG/PNG image. The OCR.space free API requires nothing but `curl` or `urllib` — no packages, no models, no installs.

## API Details

- **Endpoint:** `https://api.ocr.space/parse/image`
- **Free API key:** `helloworld` (demo key, rate-limited but works for occasional use)
- **Engine:** `OCREngine=1` (most reliable; Engine 2 can fail on some images)
- **Free tier:** 500 requests/month, ~10 req/10s rate limit

## Request Pattern (Python via urllib)

```python
import base64, json, urllib.request, urllib.parse

with open('image.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

data = urllib.parse.urlencode({
    'base64Image': f'data:image/jpeg;base64,{img_b64}',
    'language': 'eng',
    'OCREngine': '1',  # Engine 1 (default) is most reliable; Engine 2 can return status 99 on some images
}).encode()

req = urllib.request.Request(
    'https://api.ocr.space/parse/image',
    data=data,
    headers={
        'apikey': 'helloworld',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
)

resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read())
if result.get('OCRExitCode') == 1:
    text = result['ParsedResults'][0]['ParsedText']
else:
    text = f"OCR failed (exit code {result.get('OCRExitCode')}): {result.get('ErrorMessage')}"
```

## OCREngine Pitfall

- `OCREngine=2` is advertised as "best accuracy" but can return `OCRExitCode: 99` (error) on some images, especially business cards or images with mixed text/layout.
- `OCREngine=1` (default, omitting the parameter) is more reliable for business-card-style images, contact data, and mixed-content screenshots.
- **Strategy**: try Engine 1 first. If results are poor but the API returns success, try Engine 2. Never assume Engine 2 will work — always check the exit code.

## Limitations

- **Image size limit:** ~1MB for free tier
- **Language support:** eng, mongolian, 20+ others
- **No layout preservation:** returns flat text, no tables/columns
- **Rate limited:** 10 requests per 10 seconds
- **Cyrillic accuracy:** Good for printed text, poor for handwriting
- **Free key may change:** `helloworld` is a well-known demo key; if it stops working, register at https://ocr.space for a free API key

## When Not to Use

- Need table detection → marker-pdf
- Need layout/reading order → marker-pdf
- Processing many documents → install tesseract locally
- Text-only PDF → use pymupdf (faster, local)
