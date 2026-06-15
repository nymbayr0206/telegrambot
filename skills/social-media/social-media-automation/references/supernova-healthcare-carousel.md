# Supernova Healthcare Carousel Guidelines

Use when the user asks for Supernova carousel posters or healthcare/wellness carousel content from books/PDFs.

## Brand workspace

```text
/opt/data/social-content/brands/supernova/
```

Key files created during setup:

```text
brand-guide.md
assets/logos/supernova-logo-sky-background.jpg
assets/references/supernova-logo-reference-sky-background.jpg
assets/references/carousel-style-reference-health-heart-runner.jpg
source-materials/ebooks/die-entschluesselung-des-alterns-der-telomer-effekt-blackburn.pdf
carousel-plans/telomer-effect-4-slide-carousel-plan.md
carousel-plans/carousel-design-guidelines.md
```

## Fixed carousel layout

- Aspect ratio: **1:1 square**.
- Recommended export size: **1080 x 1080 px**.
- Top-left fixed phrase: `Мэдлэгт дусал нэмэр`.
- Top-right: Supernova logo.
- Bottom-right phone: `Утас: 70000303`.
- Keep safe margins around fixed elements so Facebook/Instagram cropping does not cut them.

## Typography and colors

Default installed fonts selected for Mongolian Cyrillic support:

```text
Headline: /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
Body:     /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
CTA:      /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
```

Use Supernova medical colors:

```text
Primary red:      #F20B2E
Primary blue:     #1768B5
Soft sky blue:    #DDEFF8
White background: #FFFFFF
Neutral dark:     #1F2937
```

Main poster text should be red and blue; use neutral dark only for secondary readability.

## Visual style

Reference style: clean healthcare/wellness poster, white/light-blue background, ECG line/grid motifs, heart/longevity/cell/DNA/medical wave concepts, strong whitespace, premium educational hospital look.

If people are shown, they should look Mongolian / East Asian / appropriate for a Ulaanbaatar healthcare audience.

## Generation workflow

For KIE.AI / Nano Banana 2, generate the background/visual with:

```text
NO TEXT
NO LETTERS
NO RANDOM LOGO
NO WATERMARK
```

Then overlay all Mongolian text, phone number, and logo locally using the chosen font and brand layout. This avoids misspelled Cyrillic and random model-generated logos.

## Standard 4-slide structure

1. Hook / big question.
2. Simple science explanation.
3. Practical habit or action.
4. Key takeaway + CTA / phone.

## Ebook-to-carousel planning lesson

For long PDF/book carousel planning, inspect the PDF table of contents and estimate content packages at two levels:

- **Recommended campaign:** one 4-slide carousel per major content section/chapter.
- **Expanded campaign:** one 4-slide carousel per detailed subsection for a longer daily campaign.

For the Telomer Effect ebook, the inspected TOC supported:

- 18 major carousel posts x 4 slides = 72 images.
- Optional expanded plan: about 120 micro carousel posts x 4 slides = 480 images.

Keep outputs copyright-safe: paraphrase into original educational summaries; do not copy long book passages.