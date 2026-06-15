# Template Preservation Prompt Pattern

## Problem

GPT Image 2 (`gpt-image-2-image-to-image`) frequently modifies the fixed elements of a template reference image — changing the logo, rewriting the branding bar text, altering the footer, or shifting the overall layout — even when explicitly told not to. The model treats the reference as "style inspiration" rather than a fixed canvas.

## The Pattern That Works

After trial and error (June 5, 2026), the following prompt structure reliably preserves the template:

### Structure

```
Create ONE 1:1 square social media news poster. TWO reference images provided.

CRITICAL - TEMPLATE PRESERVATION:
The FIRST image is the TEMPLATE. It has a FIXED layout that MUST be preserved EXACTLY:
- [Logo position]: DO NOT change, move, or regenerate
- [Branding bar]: DO NOT change the text, font, or position
- [Footer]: DO NOT change the text
- [Background color]: DO NOT change the color
- The overall layout, spacing, and proportions MUST remain identical to the template

ONLY change these THREE things from the template:
1. HEADLINE text (in the headline area, y=18-24%)
2. The image inside the middle rectangular frame (y=25-68%) — replace with the SECOND reference image
3. BODY text below the image (y=70-88%)

HEADLINE: "[WHITE PART]" in WHITE text + "[DARK PART]" in DARK CHARCOAL text.

IMAGE PLACEMENT: Place the photo from the SECOND image into the existing rectangular frame in the middle of the template. The frame is already on the template — just fill it with the new image.

BODY TEXT (short lines):
"[Line 1]"
"[Line 2]"
"[Line 3]"

Style: Professional news poster. Mongolian Cyrillic text ONLY. Premium finish.
```

### Key Differences from Previous Failing Patterns

| Element | Failing Pattern (model changed template) | Working Pattern (model preserved template) |
|---------|------------------------------------------|---------------------------------------------|
| Structure | Instructions mixed together | **TEMPLATE PRESERVATION** section at top, separated from content changes |
| Negative constraints | "DO NOT change" mixed in with descriptions | Bulleted list of EXACTLY what stays, explicitly marked as "FIXED" |
| What changes | Vague "replace this" | **"ONLY change these THREE things"** — numbered and explicit |
| Image placement | Generic "place photo in frame" | "The frame is already on the template — just fill it" |

### Concrete Example (WhatsApp AI Agent)

```text
Create ONE 1:1 square social media news poster. TWO reference images.

CRITICAL - TEMPLATE PRESERVATION:
The FIRST image is the TEMPLATE. It has a FIXED layout that MUST be preserved EXACTLY:
- AI Global logo at top: DO NOT change, move, or regenerate
- "AI TECH NEWS" branding bar: DO NOT change the text, font, or position
- Dark footer bar at bottom: DO NOT change "8909 7454", "Ayud tower 601 TooT", "www.aiglobal.mn"
- Gold/amber background (#F0AB06): DO NOT change the color
- The overall layout, spacing, and proportions MUST remain identical to the template

ONLY change these THREE things from the template:
1. HEADLINE text (in the headline area, y=18-24%)
2. The image inside the middle rectangular frame (y=25-68%) — replace with the SECOND reference image
3. BODY text below the image (y=70-88%)

HEADLINE: "WhatsApp" in WHITE text + "AI agent дэлхий даяар нээгдэв" in DARK CHARCOAL text.

IMAGE PLACEMENT: Place the WhatsApp icon/phone photo from the SECOND image into the existing rectangular frame in the middle of the template. The frame is already on the template — just fill it with the new image.

BODY TEXT (short lines):
"Meta компани WhatsApp Business-д AI agent нэвтрүүллээ"
"Бизнесүүд token-д суурилсан үнээр AI agent ашиглах боломжтой"
"Жижиг, дунд бизнесүүдэд том боломж нээгдэж байна"

Style: Professional news poster. Mongolian Cyrillic text ONLY. Premium finish. Magazine quality.
```

## Why It Works

1. **Psychological separation** — A distinct "CRITICAL - TEMPLATE PRESERVATION" section signals that this is not optional
2. **Explicit "ONLY change these THREE things"** — Limits the model's creative freedom to exactly what's needed
3. **"The frame is already on the template — just fill it"** — Prevents the model from redesigning the frame itself
4. **Numbered list of changes** — Makes it crystal clear that nothing else should differ

## ⚠️ CRITICAL LIMITATION: GPT Image 2 Still Hallucinates the Logo

Even with the best prompt pattern above, **GPT Image 2 invents/modifies the brand logo 100% of the time**. It treats the logo as "style inspiration" and creates a similar-looking but different logo. The user explicitly noticed and rejected this (June 5, 2026): "it still changed our logo. Our logo is totally different."

**The prompt-only approach cannot fix this.** The model architecture fundamentally treats input images as style references, not as fixed elements to preserve.

### The Fix: Two-Stage Approach

Instead of asking KIE to preserve the logo (which it cannot do), use this two-stage workflow:

#### Stage 1: Generate WITHOUT a logo
In the KIE prompt, explicitly say the logo area should be empty:

```text
IMPORTANT - NO LOGO: The top-left area of the template has NO LOGO. Do NOT add, invent, or place any logo in the top area. Leave it as empty gold background.
```

This prevents the model from inventing a fake logo that would visually conflict with the real one.

#### Stage 2: Overlay the real logo with Pillow
After downloading the KIE output, overlay the actual brand logo PNG — use actual image dimensions since KIE outputs 1024×1024 (not 1254×1254):

```python
from PIL import Image

logo = Image.open('path/to/logo-transparent.png')  # must be RGBA

img = Image.open('kie_generated.png').convert('RGBA')
w, h = img.size  # KIE outputs 1024x1024, not 1254x1254

logo_w = int(w * 0.15)  # 15% of actual width
logo_h = int(logo.size[1] * (logo_w / logo.size[0]))
logo_resized = logo.resize((logo_w, logo_h), Image.LANCZOS)
pos_x = w - logo_w - 20  # top-right
pos_y = 12

img.paste(logo_resized, (pos_x, pos_y), logo_resized)  # alpha channel as mask
img.convert('RGB').save('final.jpg', 'JPEG', quality=92)
```

### Logo File Location

For AI Global: `/opt/data/social-content/brands/ai-global/assets/logos/logo-ai-global-transparent.png` (1280x1280, RGBA with transparency)

### Why This Works

- **Deterministic** — The real logo file is always correct, never hallucinated
- **Cheaper** — No wasted credits on regeneration attempts that still produce wrong logos
- **Faster** — One KIE submission + one Pillow operation vs. 3-4 retries that still fail

## Verification

After generation, check:
- [ ] Logo is the same as the template (not a new/hallucinated logo)
- [ ] "AI TECH NEWS" bar text is unchanged
- [ ] Footer phone/address/web are unchanged
- [ ] Gold background color is unchanged
- [ ] Overall layout proportions are the same
