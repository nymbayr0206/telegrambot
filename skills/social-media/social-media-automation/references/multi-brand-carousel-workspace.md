# Multi-brand carousel workspace pattern

Use this when the user wants one Hermes server to manage content for multiple brands and generate carousel posters from books/PDFs/knowledge bases.

## Directory layout

Prefer a central `brands/` directory so each brand has isolated assets, drafts, approvals, and publishing logs:

```text
/opt/data/social-content/brands/
  brand-registry.json
  <brand-slug>/
    brand-guide.md
    setup-checklist.md
    assets/
      logos/
      fonts/
      references/
      backgrounds/
    source-materials/
      ebooks/
      docs/
    carousel-plans/
    drafts/
    generated/
    approved/
    published/
    reports/
    scripts/
```

`brand-registry.json` should map each brand slug to its workspace, default language, approval requirement, and content sources. This prevents accidental cross-brand logo/color/tone mixups.

Example:

```json
{
  "supernova": {
    "name": "Supernova",
    "workspace": "/opt/data/social-content/brands/supernova",
    "default_language": "mn",
    "approval_required": true,
    "content_sources": [
      "/opt/data/social-content/brands/supernova/source-materials/ebooks/example.pdf"
    ]
  }
}
```

## Brand setup checklist

For a new brand:

1. Create the workspace folders above.
2. Save a draft `brand-guide.md` with brand name, current source materials, visual rules, copyright-safe repurposing rule, and missing assets.
3. Copy uploaded PDFs/books into `source-materials/ebooks/` with a stable slug filename.
4. Update `brand-registry.json`.
5. Create `carousel-plans/<source>-4-slide-carousel-plan.md` after PDF/knowledge-base inspection.

## Estimating 4-image carousel count from an ebook

Use the PDF table of contents rather than page count alone.

Recommended levels:

- **High-quality campaign:** one 4-image carousel per major chapter/section.
- **Long daily campaign:** one 4-image carousel per detailed subsection, only if there is enough unique substance and the user wants a multi-month schedule.

Formula:

```text
recommended_carousels = count(major content sections before appendix/index)
total_images = recommended_carousels × 4
expanded_carousels = count(detailed subsections before appendix/index)
expanded_images = expanded_carousels × 4
```

For a 4-image educational carousel, use:

1. Hook / problem statement
2. Core idea rewritten simply
3. Practical action / habit
4. Summary + CTA

## Copyright-safe rule

Use books/PDFs as source material for original educational summaries. Do not copy long passages. Keep carousel copy paraphrased, practical, and brand-aligned.

## Publishing rule

Drafting, generating, and Telegram preview are allowed. Facebook/Instagram/LinkedIn publishing or scheduling requires explicit approval of the exact carousel and caption.