# Supernova Brand Carousel — Two-Stage Background + Pillow Overlay

Session derived from user feedback: GPT Image 2 prompt-only generation produces made-up logos and wrong colors.

## Brand Colors (from brand-guide.md and user's logo image)

| Color | Hex | Usage |
|---|---|---|
| Medical red | `#F20B2E` | Phone capsule outline, emphasis words, bottom ribbon |
| Healthcare blue | `#1768B5` | Slide number ribbon, icon outlines, dividers |
| Sky blue | `#DDEFF8` | Background wash/tint |
| Navy | `#071B4D` | Main headline text, tagline capsule |
| Gray | `#6B6F77` | Subtitle, body text, tagline text |

## Stage 1: Background Generation Prompt (KIE GPT Image 2)

Use for generating text-free backgrounds that will receive Pillow overlay:

```python
prompt = (
    "Create ONE separate 1:1 square social media carousel background image. "
    "NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS. "
    "Color palette: red (#F20B2E) and blue (#1768B5) accents on light sky-blue background (#DDEFF8). "
    "Visual style: clean medical/healthcare infographic. "
    "DNA helix, cells, medical icons, glowing bubbles. "
    "Dark navy (#071B4D) ribbon at bottom. "
    "White glowing highlights. "
    "Leave negative space at top-right for logo, top-left for title, bottom-right for phone. "
    "Mongolian healthcare aesthetic. "
    "NO other slides, NO collage."
)
```

## Stage 2: Pillow Overlay

Use the `templates/supernova-carousel-overlay-v3.py` from the `social-media-automation` skill. It handles:

- Tagline capsule (top-left): `Мэдлэгт дусал нэмэр`
- Brand logo paste (top-right): any PNG with transparency
- Slide number ribbon (left): blue rounded rectangle
- Title text (navy + red emphasis on first word)
- Gray subtitle below title
- Phone capsule (bottom-right): red outline, red phone icon, "Утас: 70000303"
- Footer wave ribbons (bottom-left): red then blue
- All colors from hex constants: RED, BLUE, SKY, NAVY, GRAY

## Usage

```bash
python3 /opt/data/skills/social-media/social-media-automation/templates/supernova-carousel-overlay-v3.py \
  --background background.png \
  --logo /opt/data/social-content/brands/supernova/assets/logos/supernova-logo-transparent.jpg \
  --slide "1/4" \
  --title "Хүмүүс яагаад өөр өөр хурдаар хөгшрдөг вэ?" \
  --subtitle "" \
  --phone "Утас: 70000303" \
  --tagline "Мэдлэгт дусал нэмэр" \
  --output final-slide.jpg
```

## Complete Automation Script

For cron-based daily carousel using this two-stage pattern, integrate into the no_agent:true script at:
`/opt/data/social-content/brands/supernova/scripts/supernova_daily_carousel.py`

The script should:
1. Generate 4 text-free backgrounds via KIE GPT Image 2 (each ~3 min, no text/logos)
2. Run the overlay template 4 times with per-slide title and slide number
3. Send the 4 final JPEGs to Make.com webhook
4. Advance state

## Pitfall: Logo File Format

If the user's logo is a JPG (not PNG with transparency), it will paste as an opaque rectangle with a solid background color (usually white or sky blue). This looks unnatural on the carousel. Request a **PNG with transparent background** for proper compositing. If only JPG is available, crop closely around the logo and use a matching background color in the paste operation.
