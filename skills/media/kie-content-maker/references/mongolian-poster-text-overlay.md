# Mongolian Poster Text Overlay Workflow

Use this when creating Mongolian-language posters through KIE.AI or any image model.

## Why

Image generators often misspell Mongolian/Cyrillic or create unreadable text. For approval-ready social graphics, prefer a two-stage workflow:

1. Generate the visual/background with **no text at all**.
2. Add all Mongolian copy deterministically with Pillow, SVG, or HTML/CSS rendering.
3. Visually verify the final image before delivery.

## Recommended Steps

1. Prompt the image model for a text-free background:
   - Include: `NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARK`.
   - Ask for clean negative space where text will be placed.
   - For this user’s Mongolian audience, specify Mongolian-looking people when humans appear.
2. Keep in-image copy short:
   - Headline: 2-5 words.
   - Hook/subtitle: 1-2 short lines.
   - CTA/badge: 1-3 words.
   - Optional disclaimer: small footer.
3. Render text locally:
   - Use a Cyrillic-capable font such as DejaVu Sans / DejaVu Sans Bold, Liberation Sans, FreeSans, or another installed Mongolian-compatible font.
   - Use opaque or semi-opaque dark panels behind large text if background is busy.
   - Avoid patching over old burned-in text unless the cover panel is fully opaque and large enough; otherwise ghost letters remain.
4. Verify with vision before final delivery:
   - Text is readable at mobile size.
   - Text is entirely Mongolian/Cyrillic if requested.
   - No leftover/ghost letters from previous revisions.
   - Person/setting matches Mongolian audience when requested.

## Example Text-Free Image Prompt Pattern

```text
Create a powerful cinematic vertical social media poster background, NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARK. Subject: a Mongolian-looking adult ... Composition: leave clean dark negative space on top-left and lower-left for Mongolian headline and CTA overlay. Mood: serious, premium, attention-grabbing ...
```

## Common Pitfalls

- Asking the image model to render Mongolian text directly; this often produces spelling/legibility errors.
- Re-editing an already text-burned image with translucent panels; use a clean text-free base or fully opaque cover panels.
- Making the top panel too narrow for long Cyrillic headlines; widen the panel or reduce font size before final export.
- Forgetting to include an “Онош биш” style disclaimer for psychology/self-reflection content.
