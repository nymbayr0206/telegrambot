# No-Logo + Pillow Overlay Pattern

## Problem

`gpt-image-2-image-to-image` with a branded template reference **always invents a fake logo**. Even with explicit "DO NOT change the logo" instructions, the model treats the reference logo as "style inspiration" and regenerates it differently. The user notices immediately ("our logo is totally different").

## Root Cause

GPT Image 2 image-to-image does not perform deterministic copy-paste of reference image regions. It generates a *new* image that *resembles* the reference. Logos, being small detail regions with specific text/shapes, are the first thing the model hallucinates.

## Solution: Two-Stage with "NO LOGO"

### Stage 1: Generate via KIE with "NO LOGO" instruction

Tell KIE explicitly to **not place any logo** in the logo area. This prevents the model from inventing a fake logo that would conflict with the real one.

```json
{
  "model": "gpt-image-2-image-to-image",
  "input": {
    "prompt": "CRITICAL - NO LOGO: The [logo position] area has NO LOGO. Do NOT add, invent, or place any logo. Leave it as empty [background color].",
    "input_urls": ["TEMPLATE_URL", "NEWS_IMAGE_URL"],
    "aspect_ratio": "1:1"
  }
}
```

### Stage 2: Overlay the Real Logo with Pillow

After downloading the KIE output, overlay the actual brand logo PNG using Pillow's alpha compositing:

```python
from PIL import Image

# Load brand logo (must be RGBA with transparency)
logo = Image.open('/path/to/logo-transparent.png')
logo_w = int(TEMPLATE_WIDTH * 0.15)  # ~15% of template width
logo_h = int(logo.size[1] * (logo_w / logo.size[0]))
logo_resized = logo.resize((logo_w, logo_h), Image.LANCZOS)

# Position (typically top-right with margin)
pos_x = TEMPLATE_WIDTH - logo_w - 20
pos_y = 12

# Load KIE-generated poster
img = Image.open('kie_generated.png').convert('RGBA')

# Paste logo using its alpha channel as mask
img.paste(logo_resized, (pos_x, pos_y), logo_resized)

# Save final output
img.convert('RGB').save('final.jpg', 'JPEG', quality=92)
```

## Why This Works

- KIE never generates a fake logo (no conflict)
- The real brand logo is overlaid deterministically (exact pixels, exact alpha)
- Background texture CAN vary — the user accepted this ("the dynamic texture it can be changed")
- The technique works for any brand with a transparent PNG logo file

## Tested Brands

| Brand | Logo Path | Size | Position |
|-------|-----------|------|----------|
| AI Global | `/opt/data/social-content/brands/ai-global/assets/logos/logo-ai-global-transparent.png` | 1280x1280 RGBA | Top-right, 15% width |

## Verification

After overlay, verify:
- [ ] Logo is at correct position (not overlapping other elements)
- [ ] Logo has correct aspect ratio (not stretched)
- [ ] Alpha transparency blends smoothly with background
- [ ] File size is reasonable (JPEG quality 92)
