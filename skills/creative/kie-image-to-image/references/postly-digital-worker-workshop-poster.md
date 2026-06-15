# Postly "Digital Worker" Workshop Poster — KIE Image-to-Image Worked Example

**Session:** June 6, 2026 — Created for Battushig, AI Agentic Force trainer at Postly

## Poster Type: Free Training Workshop with Trainer Photo

A custom workshop poster advertising a free 1-hour training on building AI agents/digital workers. Features:
- **Trainer photo** in circular portrait frame (user-provided)
- **3 agent cards** side by side (social media, sales, accountant)
- **Phone CTA**: 94594000
- **Brand**: Postly (no dedicated template — uses pricing infographic as style reference)

## Brand Reference

| Attribute | Value |
|---|---|
| Brand colors | Turquoise `#5ED4C0`, Aqua `#4CBFDD`, Deep teal `#063B4A` |
| Font style | Nunito Bold (rounded modern sans-serif) |
| Background | White to light cyan/aqua gradient |
| Format | 1:1 square |
| Phone | **94594000** (Postly contact — NOT 9459-400) |
| Website | www.postly.mn |
| Logo | `/opt/data/social-content/brands/postly/assets/logos/postly-logo-turquoise-p.jpg` |
| Style reference | `/opt/data/social-content/brands/postly/assets/references/postly-offer-pricing-infographic.jpg` |

## Prompt Structure

The prompt must be a **complete layout specification** since Postly has no fixed template. Structure:

### Section 1: Critical Rules
- Use the FIRST image (Postly pricing infographic) as STYLE REFERENCE only — for colors, aesthetic, design language
- Take the person's face from the SECOND image (trainer photo) and place in a circular portrait frame
- Do NOT modify the trainer's face — use exactly as-is from input image
- No other person photos, only this one trainer

### Section 2: Brand Style
- Background: Clean white to very light turquoise/aqua gradient
- Primary accent: Turquoise #5ED4C0 for buttons, icons, highlights, borders
- Secondary accent: Aqua #4CBFDD for decorative elements
- Headings: Deep teal #063B4A
- Body text: Dark gray #2D2D2D
- Font: Nunito Bold or clean rounded sans-serif
- Cards: White rounded cards with soft shadows, turquoise left border accent
- Overall: Clean modern SaaS product feel

### Section 3: Layout (top to bottom)

1. **TOP**: Postly logo at top-right; badge at top-left "ҮНЭГҮЙ СУРГАЛТ" (Free Training)
2. **HEADLINE**: "ӨӨРИЙН ДИЖИТАЛ АЖИЛТНАА БҮТЭЭ" (deep teal bold) → "AI АГЕНТҮҮДТЭЙ ТАНИЛЦАХ" (turquoise) → "1 ЦАГИЙН ҮНЭГҮЙ СУРГАЛТ" (gray)
3. **TRAINER**: Circular portrait with trainer face → Name "Т. БАТТҮШИГ" (deep teal) → Title "AI АГЕНТИК ФОРС ТРЕНЕР" (turquoise)
4. **CONNECTIVITY**: Icon row — Имэйл • Календарь • ERP — turquoise line connecting them
5. **CARDS** (3 side by side, rounded white with turquoise accent):
   - СОШИАЛ МЕДИА АГЕНТ: "Пост, reel, видео контент\naвтомат бэлтгэнэ"
   - БОРЛУУЛАЛТЫН АГЕНТ: "Автомат имэйл бичиж\nборлуулалтад туслана"
   - НЯГТЛАН БОДОГЧ АГЕНТ: "Зарлага, орлого, ERP\nсистемд бүртгэнэ"
6. **CTA**: Turquoise rounded button — "94594000 РУУ ЗАЛГАЖ" white bold → "ҮНЭГҮЙ СУРГАЛТАА ЗАХИАЛААРАЙ" white smaller
7. **FOOTER**: "POSTLY — Таны дижитал туслах · 94594000" in turquoise

### Section 4: Text Language Rules
- ALL Mongolian text in CYRILLIC only
- EXCEPTION: POSTLY, AI, ERP must stay in LATIN letters
- POSTLY stays POSTLY (not ПОСТЛИ), AI stays AI (not АИ)

## KIE Submission

Upload two images:
1. Postly pricing infographic (style reference) — from `/opt/data/social-content/brands/postly/assets/references/postly-offer-pricing-infographic.jpg`
2. Trainer photo — from user-provided image

Submit to `gpt-image-2-image-to-to-image` with `input_urls: [postly_ref_url, trainer_photo_url]`.

## Generation Time

Observed: ~376 seconds (~6 min) for first generation. The second attempt (same prompt, correct phone) may be faster. Poll every 10s for up to 40 polls.

## Source Script

Working Python script: `/opt/data/social-content/workshop-poster/generate_poster_v2.py`
Download output: `/opt/data/social-content/workshop-poster/postly-digital-worker-poster.png`
