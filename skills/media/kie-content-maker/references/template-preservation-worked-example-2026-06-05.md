# Template Preservation Prompt Pattern — Worked Example

## Session: June 5, 2026 — Ireeduimed edutemp1

The user provided a template JPEG and said: "only the headline can change, do not change logo or anything else."

### Pattern That Worked

When using `gpt-image-2-image-to-image` with a user-provided template reference, use this prompt structure:

```
Create ONE 1:1 square social media educational poster (1254x1254) using the attached reference image as the EXACT template background and layout.

CRITICAL - PRESERVE THESE TEMPLATE ELEMENTS:
- Logo — do NOT change, move, or replace the logo
- Background design, colors, gradients — keep EXACTLY as in the template
- Contact information / footer — do NOT change
- Brand name and positioning — do NOT change
- All decorative elements, frames, borders, and layout structure — keep IDENTICAL
- Overall proportions, margins, spacing — preserve exactly

CHANGE these elements ONLY:
1. HEADLINE text: "[NEW HEADLINE]" (in the headline/title area)
2. BODY CONTENT AREA — replace with REAL content:
   "[bullet-style content with emoji/checkmark indicators]"
3. Add a SMALL ILLUSTRATION/IMAGE — a soft, warm illustration related to the content

Style: Professional, warm, clean. Mongolian Cyrillic text ONLY.
Do NOT add any other new elements.
```

### Key Lessons

1. **Explicit fixed/dynamic separation** — List FIXED elements first, then what CHANGES. This trains the model to preserve the template.
2. **"DO NOT change" is not enough alone** — Must be paired with "ONLY change these N things."
3. **Real body content required** — The user rejected an empty template with just a headline. Add actionable tips/bullets.
4. **Image-to-image works well** — With a proper reference URL (catbox.moe or tmpfiles.org), the model preserves layout better than text-to-image description.
5. **catbox.moe is reliable** — 72h expiry, accepts KIE's `input_urls` directly, no conversion needed.

### Run Data
- Model: gpt-image-2-image-to-image
- Reference: catbox.moe URL
- Gen time: ~65-120s per slide
- Credits: 6 per slide
- All 4 slides approved on first batch generation
