<｜end▁of▁thinking｜>

<｜｜DSML｜｜tool_calls>
<｜｜DSML｜｜invoke name="skill_manage">
<｜｜DSML｜｜parameter name="file_content" string="true"># Testimonial Photo Two-Stage Overlay

## When to Use

When generating a student success/testimonial carousel and the user provides:
1. A real person photo (portrait) of the student
2. The brand's visual identity rules (colors, fonts, layout)

## Workflow

### Stage 1: KIE GPT Image 2 - Generate the Slide Background

Submit to `POST /api/v1/jobs/createTask` with model `gpt-image-2-text-to-image`.

Include in the prompt:
- Brand layout (labels, logo, contact info, text content)
- A reserved blank photo frame area (circular or rounded rectangle, right side ~30-35% width)
- Explicit instruction: do NOT generate a person in the frame

### Stage 2: Pillow Compositing (Two Sub-Patterns)

### Pattern A: Photo-Only Overlay (onto an existing KIE slide with embedded text/logo)

Use when the KIE slide already has acceptable text and logo — only the photo needs replacing:

```python
from PIL import Image, ImageDraw

slide = Image.open('kie_slide.jpg').convert('RGB')
photo = Image.open('student_photo.jpg').convert('RGB')

w, h = slide.size
pw = int(w * 0.32)
ph = int(h * 0.50)
photo_resized = photo.resize((pw, ph), Image.LANCZOS)

margin_right = int(w * 0.06)
x = w - pw - margin_right
y = int((h - ph) / 2) + int(h * 0.03)

mask = Image.new('L', (pw, ph), 0)
draw = ImageDraw.Draw(mask)
draw.rounded_rectangle([(0, 0), (pw, ph)], radius=30, fill=255)
slide.paste(photo_resized, (x, y), mask)
slide.save('final_slide.jpg', quality=95)
```

### Pattern B: Full Compositing (preferred — KIE text-free background + overlay EVERYTHING)

Use when KIE-invented text, logo, or photo are unacceptable — generate a **text-free background** via KIE (prompt: `NO TEXT, NO LETTERS, NO LOGOS, NO PEOPLE`) then overlay all assets deterministically with Pillow. This gives pixel-perfect control.

```python
from PIL import Image, ImageDraw, ImageFont
import os

# --- Setup ---
bg = Image.open('kie_text_free_bg.jpg').convert('RGB').resize((1080, 1080), Image.LANCZOS)
canvas = bg.copy()
draw = ImageDraw.Draw(canvas)
W, H = 1080, 1080

# Brand colors
CREAM = (255, 248, 240)   # #FFF8F0
GOLD  = (215, 171, 70)    # #D7AB46
DARK  = (26, 26, 46)      # #1A1A2E
WHITE = (255, 255, 255)
GRAY  = (102, 102, 102)   # #666666

# Fonts — DejaVu Sans works well for Mongolian Cyrillic
FONT_BOLD  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)
FONT_SUB   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
FONT_SMALL = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)

# --- 1. Gold pill badge (top-left) ---
badge_text = "🏆 Амжилтын түүх"
bb = draw.textbbox((0, 0), badge_text, font=FONT_SMALL)
badge_w, badge_h = bb[2]-bb[0]+40, bb[3]-bb[1]+20
draw.rounded_rectangle([(40, 30), (40+badge_w, 30+badge_h)], radius=int(badge_h/2), fill=GOLD)
draw.text((60, 40), badge_text, fill=WHITE, font=FONT_SMALL)

# --- 2. Real logo (top-right) ---
logo = Image.open('brand_logo.jpg').convert('RGB')
logo_size = 140
logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
canvas.paste(logo, (W - logo_size - 35, 25))

# --- 3. Headline text (left ~60% of canvas) ---
headlines = ["Хиймэл оюун ухаан", "намайг гүйцэх гэж байхад", "би түрүүлж сурсан"]
headline_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
for i, line in enumerate(headlines):
    draw.text((50, 220 + i*65), line, fill=DARK, font=headline_font)

# --- 4. Subtitle ---
sub = "Батбаатарын түүх — IT салбарт 10+ жил"
sub_y = 220 + len(headlines)*65 + 30
draw.text((50, sub_y), sub, fill=GRAY, font=FONT_SUB)

# --- 5. Circular photo with gold border (right side) ---
photo = Image.open('student_photo.jpg').convert('RGB')
psize = 320
photo = photo.resize((psize, psize), Image.LANCZOS)

# Circular crop mask
mask = Image.new("L", (psize, psize), 0)
ImageDraw.Draw(mask).ellipse([(2, 2), (psize-2, psize-2)], fill=255)

circular = Image.new("RGBA", (psize, psize), (0,0,0,0))
circular.paste(photo, (0, 0), mask)

# Gold border ring
border = 6
ring = Image.new("RGBA", (psize+border*2, psize+border*2), (0,0,0,0))
ImageDraw.Draw(ring).ellipse([(0, 0), (psize+border*2-1, psize+border*2-1)], outline=GOLD, width=border)
ring.paste(circular, (border, border), circular)

px = W - psize - border*2 - 50
py = int(H/2) - int((psize+border*2)/2) - 30
canvas.paste(ring, (px, py), ring)

# --- 6. Contact pill (bottom-left) ---
contact = "📞 89097454  🌐 aiglobal.mn"
cb = draw.textbbox((0, 0), contact, font=FONT_SMALL)
cw, ch = cb[2]-cb[0]+40, cb[3]-cb[1]+16
draw.rounded_rectangle([(40, H-80), (40+cw, H-80+ch)], radius=int(ch/2), fill=GOLD)
draw.text((60, H-72), contact, fill=WHITE, font=FONT_SMALL)

# --- 7. Gold line bottom ---
draw.rectangle([(30, H-25), (W-30, H-23)], fill=GOLD)

canvas.save('final_slide.jpg', quality=95)
```

## Key Points

- **KIE cannot embed a specific photo** - it will invent a face. Always use the two-stage approach.
- **Even worse: KIE invents brand logos and misspells text.** For premium brands (luxury, education), always use Pattern B (full compositing) — generate a text-free background, then overlay the real logo, exact text, and real photo.
- **The KIE prompt must explicitly say "do NOT generate a person"** and describe the area as a reserved frame/placeholder. Also add "NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS" for Pattern B.
- **The user typically wants the photo on ALL 4 slides** of the testimonial carousel.
- **Always test Slide 1 first** - send the final composited result for approval before generating slides 2-4.
- **Font check before Stage 1**: verify Pillow is importable and brand fonts exist. Wastes KIE credits if not done upfront.
- **Python path for background processes**: when running compositing scripts via `terminal(background=true)`, the background process may use `/usr/bin/python3` which lacks Pillow. Use an explicit venv path: `/opt/hermes/.venv/bin/python3` or add the shebang `#!/opt/hermes/.venv/bin/python3`.
- **DejaVu Sans Bold** is a reliable fallback for Mongolian Cyrillic text (installed at `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`). The brand-specified Manrope font is typically not installed.
- **Photo dimensions**: square crop ~300px with circular mask is good for side-by-side layout. Gold (#D7AB46) circular border (6px) adds premium feel.
- **Text positioning**: for 3-line headlines, use 65px line spacing with DejaVu Sans Bold 50px. Position in left ~60% of canvas to leave room for photo on right.

## Real Example (AI Global — Batbaatar Testimonial, June 2026)

- **Student:** Batbaatar, IT professional, 10+ years
- **Story:** Felt behind by AI agent growth, learned automation, saved 3-4 hrs/week
- **Carousel:** 4 slides (Hook → Explain → Deepen → CTA)
- **Slide 1 headline:** "Хиймэл оюун ухаан намайг гүйцэх гэж байхад би түрүүлж сурсан"
- **Approach used:** Pattern B (full compositing from text-free KIE background)
- **Canvas:** 1080×1080px, cream (#FFF8F0) background via KIE
- **Photo:** 320×320px circular crop with 6px gold (#D7AB46) border, positioned at (W-410, H/2-190)
- **Headline font:** DejaVu Sans Bold 50px, dark (#1A1A2E), three lines at 65px spacing
- **Subtitle:** DejaVu Sans 28px, gray (#666)
- **Logo:** 140×140px, placed top-right at (W-175, 25)
- **Badge:** "🏆 Амжилтын түүх" gold pill, top-left at (40, 30)
- **Contact:** "📞 89097454 🌐 aiglobal.mn" gold pill, bottom-left at (40, H-80)
- **Review result:** PASS (A) — all scores 8-9/10
- **Script ref:** `/opt/data/scripts/generate_slide1_two_stage.py`
- **KIE background task:** 60e85aa7da59ac02dcc099a32653f29c (~50s gen)

## Reference

See also `references/brand-carousel-prompt-authoring.md` Step 6a for the full workflow.
