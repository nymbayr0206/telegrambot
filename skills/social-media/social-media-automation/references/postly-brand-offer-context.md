# Postly brand offer/context

Use this reference when creating Postly social content, carousels, reels, captions, campaigns, or brand automation.

## Workspace and assets

- Workspace: `/opt/data/social-content/brands/postly`
- Logo: `assets/logos/postly-logo-turquoise-p.jpg`
- Offer/pricing infographic reference: `assets/references/postly-offer-pricing-infographic.jpg`
- Brand guide: `brand-guide.md`
- Extracted offer context: `offer-context.md`

## Positioning

Postly is an AI agent-based content marketing automation service/system for Mongolian businesses. It acts like an automated AI marketing team: idea research, planning, copy/captions, carousel design, AI reels, scheduling/autoposting, analytics/reporting, boost setup, and optional workflow/CRM integrations.

Core promise/tagline:

> `1 social media manager-ын цалингаар бүтэн AI marketing team ажиллуулна.`

Emphasize automation, consistency, lower cost, time savings, and professional marketing output.

## Language, audience, platforms

- Language: mostly Mongolian.
- English: use selectively for SaaS/AI/content-marketing terms when it sounds natural.
- Audience: Mongolian SMEs and growth businesses; also useful for clinics, education, e-commerce, restaurants, salons, cafes, service businesses, franchises, branches, and personal brands.
- Platforms: Facebook and Instagram first.
- Publishing rule: approval-first unless the user explicitly gives a webhook/autopost instruction for a specific asset.

## Visual style

Combine both directions:

1. Existing Postly infographic style:
   - turquoise/aqua gradients
   - rounded cards
   - light cyan/white background
   - circular icons
   - clean automation/calendar/dashboard visuals
   - friendly AI/robot assistant mascot can be used

2. Premium modern SaaS style:
   - polished rounded UI cards
   - subtle gradients and soft shadows
   - clean bold typography
   - social-content automation dashboards
   - Facebook/Instagram/calendar/analytics motifs

Default carousel/image model for final posters when typography/style matters:

- KIE GPT Image 2: `gpt-image-2-text-to-image`
- Generate one separate slide/image per task, not contact sheets, unless the user asks for preview sheets.

## Carousel Design Preferences (Postly-specific)

These preferences were corrected by the user and should be applied to ALL Postly carousel content:

### Logo placement
- **ALWAYS include the Postly logo** on every branded carousel image, placed **top-right corner**
- Logo file: `assets/logos/postly-logo-turquoise-p.jpg` (JPG format — paste without alpha mask)

### Comparison content format
- **Prefer side-by-side single slides** for WITH vs WITHOUT / Before vs After comparisons
- Do NOT split comparisons across two sequential slides — the user explicitly corrected this
- Layout: left panel (dark/red theme) for WITHOUT, right panel (turquoise/bright) for WITH
- Thin vertical divider in center
- Prices and totals prominent on each side

### Concept approval workflow
- Test ONE sample slide first before generating the full carousel set
- Send the test slide for review and get explicit approval before continuing
- This saves KIE credits and avoids rework

### Font
- Preferred: Nunito Bold (`/opt/data/fonts/Nunito-Bold.ttf`)
- Fallback: DejaVu Sans Bold (at `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`)
- Always verify font loads with `ImageFont.truetype()` before compositing

### Two-stage generation (recommended for comparison content)
- Stage 1: Generate text-free background via KIE GPT Image 2 with `NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS`
- Stage 2: Pillow compositing — overlay actual Postly logo + all text locally
- See `kie-content-maker` skill's `templates/postly-comparison-slide-composer.py` for the reusable script

## Offer/package facts

Content formats:

- Carousel post: `40,000₮ / 1 carousel`
- AI Reel Video, 24 sec: `25,000₮ / 1 reel`

Monthly plans:

### Starter Plan

- `390,000₮ / сар`
- 7 carousel posts
- 4 AI reel videos
- 3 content-type balance
- caption + hashtag
- 7-day posting plan
- auto-post system
- content calendar
- knowledge base usage
- bonus: 1 boost setup free (`100,000₮ value`)
- frequency: 3–4 posts / 7 days
- ideal for cafes, salons, small businesses, personal brands

### Growth Plan

- `690,000₮ / сар`
- 12 carousel posts
- 8 AI reel videos
- brand awareness + sales balance
- weekly content strategy
- CTA optimization
- messenger funnel idea
- auto-post system
- content calendar
- knowledge base usage
- bonus: 2 boost setups free (`200,000₮ value`)
- frequency: 1 post every day
- ideal for education, clinics, e-commerce, restaurants, service businesses

### Enterprise Plan

- `1,190,000₮ / сар`
- 20 carousel posts
- 16 AI reel videos
- strategic content for every brand
- promotional campaigns
- offer campaign content
- AI optimized engagement flow
- competitor monitoring idea
- full automation workflow
- priority support
- bonus: 4 boost setups free (`200,000₮ value`)
- frequency: 2 posts every day
- ideal for large companies, franchises, national/local brands, multi-branch businesses

Boost/ad setup:

- Single boost setup: `100,000₮`
- 3 boost setup package: `270,000₮` after 10% off, original `300,000₮`
- 5 boost setup package: `450,000₮` after 10% off, original `500,000₮`

Add-ons:

- Additional carousel: `40,000₮`
- Additional AI Reel: `25,000₮`
- Urgent same-day content: `+20%`
- Advanced Sales Funnel Copy: `80,000₮`
- Landing Page Copywriting: `150,000₮`
- Messenger Automation Setup: `250,000₮+`
- Odoo CRM Integration: custom price
- Custom Workflow Automation: custom price

## Content pillars

1. Brand Awareness — tips, hacks, educational content, "Та мэдэх үү?", problem awareness, storytelling, industry insights.
2. Product/Service Consideration — benefits, before/after, comparison, customer cases, why choose us, feature highlights, FAQ.
3. Promotional/Sales — offer, discount, limited campaign, CTA, event push, conversion message, website/messenger action, boost-ready ads.

## Lead targeting and sales reminders

When the user asks who needs Postly marketing/sales agents, prioritize businesses where Facebook/Instagram content directly creates leads, bookings, inquiries, or sales but posting is inconsistent or weak. Start with three verticals before broad outreach:

1. Clinics / medical / beauty clinics — high-ticket trust-building services; need education, FAQ, before/after, and service explanation content.
2. Education centers — enrollment campaigns, course announcements, testimonials, FAQ, student lead generation.
3. E-commerce / online shops — product posts, offers, bundles, UGC-style reels, and sales captions.

Also consider restaurants/cafes, salons/spas/fitness, real estate, and B2B service companies. Strong buying signals: already running Meta ads/boosts, weak or inconsistent page content, last post older than 7 days, hiring social/content/marketing staff, many services/products but little structured content, recent branch opening, frequent promotions, or competitors posting better.

Default outreach CTA: offer a free 5-minute content audit or 3 tailored content ideas before pitching a package. Daily sales reminder target: find 20 qualified leads, contact 10, follow up overdue replies, and set a next action/date for every interested lead.
