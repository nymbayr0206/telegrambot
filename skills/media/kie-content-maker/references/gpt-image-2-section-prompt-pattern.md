# GPT Image 2 Section-Based Prompt Pattern for Carousel Slides

## Why Section-Based Structuring Works

GPT Image 2 responds well to explicit **visual zoning** — breaking the layout into named regions (TOP/MIDDLE/BOTTOM) with specific content, colors, and styling instructions for each. This produces more predictable layouts than freeform description.

## The Pattern

```
TOP SECTION — [content: title text, color, font style, size]
MIDDLE SECTION — [content: body elements, layout: list/grid/cards, colors]
BOTTOM — [content: CTA bar/total/button, color, style]
Visual style — [brand rules, mood, background]
NO EXTERNAL LOGOS. Use [brand colors]. ONE [format] image.
```

## Concrete Example (Postly Slide 2 — WITHOUT Marketing)

```
TOP SECTION — Bold title text: "МАРКЕТИНГИЙН БАГГҮЙГЭЭРЭЭ..." in dark teal, large bold rounded font.
MIDDLE SECTION — Four person icons/avatar circles in a vertical list, each with a role label and salary amount:
1. 📊 Судлаач — 1,000,000₮
2. ✏️ Контент зохиолч — 1,500,000₮
3. 🎨 Дизайнер — 1,500,000₮
4. 🎬 Видео редактор — 1,500,000₮
Use small price tags next to each role. The icons should look stressed/overworked.
BOTTOM — Highlighted total bar: "НИЙТ 4 ХҮН = 5,500,000₮/сар" in white text on a turquoise gradient bar.
Visual style: Clean modern SaaS, rounded cards with soft shadows, white background with turquoise accent elements. Professional but relatable. Rounded bold typography.
NO EXTERNAL LOGOS. Use Postly brand colors (turquoise, aqua, deep teal). ONE 1:1 square image.
```

## Key Rules

1. **Explicit color hexes** — always include brand hex codes inline (e.g. `#4CBFDD`, `#063B4A`)
2. **Layout anchors** — name screen positions (top, middle, bottom, left, right, center)
3. **Role-specific styling** — describe the visual job of each zone (title bar, list body, CTA footer)
4. **Negative constraints** — always include `NO EXTERNAL LOGOS`, `NO WATERMARKS`, `ONE 1:1 square` (not a collage)
5. **Text content** — quote the exact text you want to appear, despite GPT Image 2 misspelling non-English text (QA is still required)
6. **Brand emission** — the model will invent logos even with detailed descriptions; use two-stage (background only + Pillow overlay) when exact brand logo fidelity matters

## When to Use Two-Stage Instead

This prompt pattern is **direct generation** — good for testing concepts, rough drafts, and speed. Switch to **two-stage** (text-free background + local Pillow overlay) when:

- Exact Mongolian/Cyrillic spelling is critical for publishing
- The official brand logo must appear accurately
- Phone numbers or prices must be pixel-perfect
- The user rejected prompt-only generation for visual inaccuracy
