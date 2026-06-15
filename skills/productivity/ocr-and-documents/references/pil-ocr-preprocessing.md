# PIL Image Preprocessing for OCR

## When to Use

When OCR.space (or any OCR engine) returns incomplete, garbled, or missing text — especially on:
- Business cards with multiple font sizes
- Screenshots with dithering or JPEG artifacts
- Mixed text/logo/background images
- Small text that the OCR engine misses entirely

## The Technique

```python
from PIL import Image, ImageEnhance, ImageFilter

img = Image.open('input.jpg')

# 1. Enlarge 2× (helps OCR see small text)
img_big = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)

# 2. Grayscale (removes color noise)
img_gray = img_big.convert('L')

# 3. Boost contrast (2-3× enhancement works well)
enhancer = ImageEnhance.Contrast(img_gray)
img_contrast = enhancer.enhance(2.0)  # Try 2.0-3.0 for stubborn images

# 4. Sharpen (makes edges crisper for character recognition)
img_sharp = img_contrast.filter(ImageFilter.SHARPEN)
# For very blurry images, apply sharpen twice:
img_sharp = img_sharp.filter(ImageFilter.SHARPEN)

# 5. Save at moderate quality (85-95)
img_sharp.save('processed.jpg', 'JPEG', quality=90)
```

## Section-Based Cropping

For images taller than ~600px, OCR engines often miss content toward the edges of the frame. Crop into horizontal slices and OCR each one:

```python
from PIL import Image

img = Image.open('input.jpg')
h = img.height
w = img.width
n_sections = 4
section_h = h // n_sections

for i in range(n_sections):
    top = i * section_h
    bottom = (i + 1) * section_h if i < n_sections - 1 else h
    section = img.crop((0, top, w, bottom))
    section.save(f'section_{i}.jpg', 'JPEG', quality=90)
```

Then OCR each section and concatenate the results.

## Tips

- **JPEG quality:** 85-95 is the sweet spot — high enough for OCR, small enough for API rate limits
- **File size:** Keep files under 1MB for OCR.space free tier; if too large, reduce quality or dimensions slightly
- **Sectioning:** 3-4 sections is usually enough; more than 6 hurts the rate limit
- **Cyrillic / Mongolian text:** Contrast enhancement helps significantly — Cyrillic characters are more sensitive to anti-aliasing and compression artifacts than Latin
- **Empty sections:** If a section returns blank text, it's likely a margin/header/footer area with little content; skip it
- **Combined approach:** For best results, apply preprocessing THEN section-crop, not the reverse — each section benefits from the full-image contrast boost
