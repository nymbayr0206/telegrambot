# New Brand Social Media Content Plan Template

Use this when a user sends a brand image/logo and asks for a social media content plan. The workflow handles the case where the active model may not support vision.

## Workflow

### Step 1: Identify the Brand
- If user sends an image and `vision_analyze` fails (model doesn't support vision), use the fallback in `references/vision-fallback-when-model-doesnt-support-vision.md`
- Extract from analysis: brand name, colors (hex codes), industry, location, contact info, logo description, target audience

### Step 2: Create the Content Plan Structure

A comprehensive content plan has these sections:

1. **Platforms & Frequency** — table: Facebook, Instagram, TikTok, YouTube with content type per platform
2. **Weekly Content Calendar** — each day has a theme:
   - Monday: Product showcase (Carousel)
   - Tuesday: Behind-the-scenes / Work footage (Reel)
   - Wednesday: Testimonials / Client feedback (Carousel)
   - Thursday: Tips / Knowledge (Static post)
   - Friday: Special offers / Promotions (Carousel or Reel)
   - Saturday: Team introduction (Photo)
   - Sunday: Industry news (Share post)
3. **Reel Ideas** — 6-8 specific reel concepts relevant to the brand's industry
4. **Carousel Design Spec** — color scheme, slide-by-slide layout with text + image placement
5. **Post Caption Templates** — pre-written templates for product posts, reel captions, promotional posts (with emojis, bullet points, CTA, hashtags)
6. **30-Day Launch Plan** — first month broken into weekly themes with format counts (e.g. 12 Carousel + 12 Reel = 24 total)

### Step 3: Tailor to Industry

| Industry | Visual Style | Reel Focus | Example Hashtags |
|----------|-------------|-----------|-----------------|
| Construction/Machinery | Bold orange/black, industrial | Machine operation, before/after | #Construction #Mongolia #HeavyEquipment |
| Education | Clean cream/gold, professional | Student stories, course previews | #Education #AI #Mongolia |
| SaaS/Tech | Bright turquoise/teal, modern | Product demos, comparisons | #Tech #SaaS #Innovation |
| Medical | Red/blue, clinical | Equipment demos, health tips | #Medical #Health #Mongolia |

### Step 4: Save & Offer Next Steps

Save the plan to `/opt/data/social-content/brands/<brand-name>/content-plan.md` and offer:
1. 🎨 Generate first Carousel via KIE
2. 🎬 Write first Reel script
3. ✏️ Adjust the plan
4. 📤 Auto-publish to platforms

## Delivered Format

The content plan is delivered directly in chat (Telegram) so the user can see it immediately, and saved to disk for future reference.
