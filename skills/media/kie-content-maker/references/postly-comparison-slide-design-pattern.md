# Postly Comparison Slide Design Pattern (Concept 1: The Wave)

Used for the WITH vs WITHOUT comparison campaign (May 29, 2026).

## Background Prompt (for KIE GPT Image 2 — text-free)

```text
Create ONE 1:1 square social media carousel slide background. Split vertically
into TWO equal panels. NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS, NO WORDS
anywhere.

LEFT PANEL: Dark moody background in deep navy-teal (#063B4A) with subtle 
red/dark accents. Four small empty circular avatar placeholders stacked
vertically in the center area. Abstract stressed/chaotic decorative lines.
A horizontal dark bar area at the bottom.

RIGHT PANEL: Bright hopeful background in turquoise gradient (#4CBFDD to
#5ED4C0). Clean, minimal, modern. Two larger circular avatar placeholders in
the center area (one with a subtle gear icon shape, one with a subtle
conversation bubble shape). A horizontal gradient bar area at the bottom.

DIVIDER: A thin white or light gray vertical divider line in the center.

TOP AREA: Clean white space reserved for branding and title.

Style: Modern SaaS, clean, premium. Rounded corners. Subtle shadows.
Dark on left, bright on right.
```

## Pillow Compositing Details

See `templates/postly-comparison-slide-composer.py` for the full script.

Key decisions from the session:
- Split is LEFT=WITHOUT (dark/red) vs RIGHT=WITH POSTLY (turquoise/bright)
- Logo top-right, ~18% of slide width
- Thin vertical divider at center
- LEFT: 4 employee roles with icon circles, salary capsules, total bar
- RIGHT: 2 AI agent entries, price bar with "Зөвхөн 390,000₮/сар"
- Bottom tagline across full width
- Final output resized to 1080x1080

## Verifications to Run

- [ ] Logo file exists and loads in Pillow
- [ ] Font files load with ImageFont.truetype() (Nunito Bold; fallback DejaVu Sans Bold)
- [ ] Background has clean negative space for both panels
- [ ] Mongolian text is correct (prices, agent names, total)
- [ ] Resize to 1080x1080 for Instagram
