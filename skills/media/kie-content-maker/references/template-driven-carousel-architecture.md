# Template-Driven Carousel Architecture

## Origin

This pattern was designed by Battushig (AI Global founder) in May 2026. The core insight: **most AI content systems fail because they ask KIE to generate the entire poster. Instead, generate only the variables and inject them into a fixed template.**

## Architecture Layers

### 1. Template (fixed, never changes)

A template is a **database schema** — it defines:
- Fixed layout: background, logo position, footer, colors, typography
- Marker slots: where variable content goes (text regions, image frames)
- Image slots: which images to generate and where to place them

**Rules:**
- NEVER redesign the template
- NEVER move the logo
- NEVER change typography or colors
- NEVER change layout

### 2. Content Generator (Hermes)

Hermes generates **only the variable marker values**:
- Student profile: name, age, occupation, quote
- Storyline: 3 problems, 3 weekly milestones, 3 metrics
- CTA text

Markers are output as a JSON data file.

### 3. Image Generator (KIE GPT Image 2)

KIE generates **only the image slots** — text-free, logo-free:
- Each slot has a fixed prompt style (doesn't vary per student)
- NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS
- Generate 4 independent images (one per slot)

### 4. Renderer (Pillow)

Composites everything into final slides:
1. Load template background (pre-generated or Pillow-created)
2. Paste logo (from brand assets)
3. Draw fixed elements: gold badge, divider, footer
4. Place slot images into their frames
5. Draw all text markers with exact fonts and positioning
6. Output 4 final JPGs (1080×1080)

## Template Schema (JSON)

Every template lives at:
```
/opt/data/social-content/brands/<brand>/templates/<template_id>/template.json
```

### Schema Structure

```jsonc
{
  "template_id": "aiglobal_success_story_v1",
  "version": "1.0.0",
  "brand": "AI Global",

  "fixed": {
    "canvas": { "width": 1080, "height": 1080, "format": "1:1 square" },
    "background": {
      "base_color": "#FAFAF8",
      "style": "Light cream, subtle texture, Italian minimal",
      "source": "pre-generated or Pillow fallback"
    },
    "typography": {
      "font_family": "Manrope",
      "font_fallback": "DejaVu Sans Bold",
      "font_path_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
      "font_path_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
      "headline_size": 52,
      "subhead_size": 36,
      "body_size": 28,
      "small_size": 22
    },
    "colors": {
      "charcoal": "#1A1A1A",
      "gold": "#D7AB46",
      "white": "#FFFFFF",
      "cream": "#FAFAF8",
      "light_gray": "#F0EFEB",
      "medium_gray": "#888888"
    },
    "layout": {
      "content_type_badge": {
        "position": "top-left",
        "margin_x": 45,
        "margin_y": 35,
        "background_color": "#D7AB46",
        "text_color": "#FFFFFF",
        "font_size": 24,
        "padding_x": 24,
        "padding_y": 12,
        "border_radius": 20,
        "label": "🏆 Амжилтын түүх"
      },
      "logo": {
        "position": "top-right",
        "margin_x": 40,
        "margin_y": 25,
        "size": 140
      },
      "contact_footer": {
        "position": "bottom-left",
        "margin_x": 45,
        "margin_y": 35,
        "font_size": 22,
        "color": "#888888",
        "text": "📞 89097454  🌐 aiglobal.mn"
      },
      "gold_divider": {
        "enabled": true,
        "position": "bottom",
        "margin_x": 40,
        "margin_y_from_bottom": 75,
        "height": 2,
        "color": "#D7AB46",
        "width_percent": 0.92
      }
    }
  },

  "slides": [
    // Each slide has markers with placement coordinates
  ],

  "image_slots": {
    "slot_A": {
      "label": "Student portrait",
      "gen_style": "Mongolian, 18-25 years old, professional, friendly, realistic, high quality, white background, yellow accent lighting",
      "fallback_color": "#E8E4DC"
    },
    "slot_B": { ... },
    "slot_C": { ... },
    "slot_D": { ... }
  }
}
```

## Render Script Pattern

The renderer (`render.py`) at the template directory should:

```python
#!/opt/hermes/.venv/bin/python3
"""aiglobal_success_story_v1 renderer — composites template + markers + slot images."""

import json, argparse, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1080

def render_slide(template, data, slots_dir, slide_idx, output_path):
    """Render one slide from template schema + marker data + slot images."""
    slide_def = template["slides"][slide_idx]
    F = template["fixed"]
    C = F["colors"]
    L = F["layout"]

    # 1. Background
    bg_path = os.path.join(slots_dir, "..", "background.png")
    if os.path.exists(bg_path):
        canvas = Image.open(bg_path).convert("RGB").resize((W, H), Image.LANCZOS)
    else:
        canvas = Image.new("RGB", (W, H), hex_to_rgb(C["cream"]))
    draw = ImageDraw.Draw(canvas)

    # 2. Fonts
    font_bold = ImageFont.truetype(F["typography"]["font_path_bold"], 52)
    font_body = ImageFont.truetype(F["typography"]["font_path_regular"], 28)
    # ... load all font sizes from template

    # 3. Fixed elements — badge, logo, footer, divider
    draw_badge(canvas, draw, L["content_type_badge"], C)
    paste_logo(canvas, template_dir, L["logo"])
    draw_footer(canvas, draw, L["contact_footer"], font_body)
    draw_divider(canvas, draw, L["gold_divider"], C)

    # 4. Slot images
    for marker_name, marker_def in slide_def["markers"].items():
        if marker_def["type"] == "image_slot":
            slot_id = marker_def["slot_id"]
            img_path = os.path.join(slots_dir, f"{slot_id}.png")
            if os.path.exists(img_path):
                paste_image(canvas, img_path, marker_def["placement"])

    # 5. Text markers
    for marker_name, marker_def in slide_def["markers"].items():
        if marker_def["type"] == "text":
            value = data.get(marker_name, "")
            draw_text(canvas, draw, value, marker_def)

    canvas.save(output_path, quality=95)
```

## Concrete Example: aiglobal_success_story_v1

### Image Slots

| Slot | Slide | Content | Generated Prompt |
|------|-------|---------|-----------------|
| slot_A | 1 | Student portrait | "Mongolian male student, 18-25, smiling, professional, friendly, realistic, high quality, white background, yellow accent lighting, NO TEXT, NO LETTERS" |
| slot_B | 2 | Before/struggle | "Young Mongolian student thinking, confused expression, educational setting, professional photography, realistic, NO TEXT" |
| slot_C | 3 | Success/happy | "Young Mongolian student smiling with laptop, achievement moment, bright lighting, happy, professional photography, NO TEXT" |
| slot_D | 4 | Result/dashboard | "Mobile app dashboard, colorful data visualization, achievement screen, modern UI design, clean, NO TEXT" |

### Slide Layout Summary

**All 4 slides share:**
- Background: cream (#FAFAF8) with subtle texture
- Top-left: gold pill "🏆 Амжилтын түүх"
- Top-right: AI Global logo (140px)
- Bottom-left: "📞 89097454  🌐 aiglobal.mn"
- Gold divider line near bottom

**Slide 1 (Student Introduction):**
- Split layout: text left (~55%) + photo right (~38%)
- Headline: 3 lines, Manrope Bold 52px, charcoal
- Name: gold (#D7AB46) 28px
- Age + occupation: medium gray 22px
- Quote: italic gray 24px
- Photo frame: rounded rectangle, gold 4px border

**Slide 2 (Before):**
- Left: 3 problems with ❌ prefix, 28px
- Right: before_photo in same frame as slide 1

**Slide 3 (Transformation):**
- Left: 3 weekly milestones with ✅ prefix, 26px
- Right: success_photo

**Slide 4 (Results & CTA):**
- Left: 3 metrics in gold 40px bold
- CTA text at bottom-left
- Right: result_visual (dashboard/app screenshot)

## Creating a New Template for a Different Brand

1. Create directory: `brands/<brand>/templates/<template_id>/`
2. Write `template.json` with fixed layout, slides, markers, and image_slots
3. Write `render.py` following the pattern above
4. Generate one text-free background image via KIE GPT Image 2
5. Test with sample data before generating slot images

## Pitfalls

- **Don't generate text-heavy images via KIE**: KIE misspells Mongolian text. Generate text-free images only. All text goes through Pillow overlay.
- **Don't vary slot prompt styles**: If slot A is "portrait" for every carousel, the prompt should be identical. Only the student name/story changes (in Hermes, not in KIE).
- **Don't composite without font check**: Before any rendering, verify font files exist at paths in template.json. Missing fonts produce silently blank text.
- **Don't use nonexistent brand fonts**: Manrope may not be installed. Always specify fallback fonts (DejaVu Sans Bold for Mongolian Cyrillic).
- **Don't generate background per carousel**: One text-free background image serves all carousels for that template. Cache it at `templates/<template_id>/background.png`.
