# Postly AI spokesperson video pattern

Use this reference when creating Postly Facebook/Instagram Reels, AI video ads, or Veo prompts that feature a person explaining Postly.

## Core story that tested well

Postly videos should avoid a generic talking-head opener. The stronger narrative is:

1. **Messy founder / content chaos** — a Mongolian business owner is stressed in a cluttered office, stuck on what to post, captions, design, reels, and scheduling.
2. **Discovery** — she finds `Postly marketing agents` on her laptop/phone.
3. **Transformation** — sticky notes and chaos become turquoise SaaS UI cards: ideas, captions, carousel, AI reel, calendar, auto-post, analytics.
4. **Freedom** — she is now polished, happy, and focused on business growth, optionally in a premium environment such as a nice car, rooftop café, glass office, or Ulaanbaatar city lights.

The emotional arc is: **stress → discovery → relief/confidence → business freedom**.

## Character direction

- Mongolian / East Asian woman, late 20s to mid 30s.
- Founder / small business owner / marketing strategist energy.
- Before Postly: relatable, tired, slightly stressed, less polished outfit, messy desk.
- After Postly: same woman, polished outfit, turquoise/aqua accent, confident smile, stylish founder look.
- Tone: not stiff presenter; expressive, natural, slightly playful, credible.

## First 2-second hook

The first two seconds must show the pain visually before explaining the service.

Recommended opener:

- Close-up of messy desk: sticky notes, crossed-out ideas, blank Facebook/Instagram draft, empty content calendar, many laptop tabs.
- She sighs, rubs forehead, deletes a draft, or closes a notebook.
- She looks directly at camera and says a concise Mongolian pain line.

Good hook lines:

- `Өдөр бүр юу постлох вэ гэж бодсоор ядардаг байлаа.`
- `Контент хийх гэж өдөр бүр цаг алдаж байна уу?`
- `Нэг пост хийх гэж бүтэн өдөр алдаад байна уу?`

## Three-part Veo 3.1 Fast structure

Use `veo3_fast`, 9:16 vertical, and generate in sequence. Save each task/seed/reference id and pass it into the next generation for continuity.

### Generation 1 — messy start / problem

Scene: cluttered business office, evening, sticky notes, laptop tabs, blank social post draft, empty calendar. Woman is stressed and relatable.

Short narration:

```txt
Өдөр бүр юу постлох вэ гэж бодсоор ядардаг байлаа. Caption, дизайн, постлох цаг гээд контент өөрөө бүтэн ажил болчихсон.
```

### Generation 2 — discovers Postly / transformation

Scene: same woman taps a glowing Postly marketing agents card. Messy notes transform into clean turquoise UI cards. Outfit and lighting become polished SaaS style.

Short narration:

```txt
Тэгээд би Postly marketing agents-ийг олсон. AI маань санаа гаргаж, caption бичиж, carousel дизайн, reel хүртэл бэлддэг.
```

### Generation 3 — freedom / business growth

Scene: same woman now happy and confident in a premium environment: nice car, rooftop café, glass office, Ulaanbaatar city lights. Phone/tablet shows scheduled Facebook/Instagram posts and analytics.

Short narration:

```txt
Постууд өөрөө цагтаа нийтлэгддэг. Би одоо контентод санаа зовохгүй, бизнесийнхээ өсөлт дээр төвлөрч чаддаг болсон.
```

### Optional Generation 4 — price / huge value

Use when the user wants a short value/price objection-handling clip after the main 3-part story. Keep the price message to one tight 8-second line; do not over-explain.

Scene: same woman in the polished after-state, ideally in a premium car / city lights / clean business environment, holding a tablet with Postly dashboard. Make it feel like a strong-value business offer, not cheap discounting.

Current Postly price/value narration from the user:

```txt
Postly сарын 360,000 төгрөгөөс эхэлнэ. Төлөвлөлт, санаа гаргалт, 7 carousel, 5 reel бүгд багтана — маш өндөр үнэ цэнтэй.
```

## Still-image preflight before video

Before spending Veo credits, generate a vertical concept image first to approve:

- main character look,
- messy office / transformation visual,
- turquoise Postly SaaS UI style,
- premium after-state mood.

For this user, KIE GPT Image 2 worked well for a concept still with this direction. Save stills under:

```txt
/opt/data/social-content/brands/postly/generated/concept-model-look/
```

Use the approved still as visual style guidance for Veo prompts.

## Production notes

- Veo Mongolian speech may be imperfect. If audio is weak, use the generated videos as visuals and add a clean Mongolian female voiceover + exact subtitles later.
- Avoid relying on generated long text inside video frames. Use simple UI concepts visually, and add exact CTA/subtitles in editing.
- Suggested CTA overlay: `Postly — Контентоо AI agent-аар автоматжуул`.
- Postly should feel like a premium, useful AI marketing team, not just another design service.
- For user review, send the three clips separately with the exact narration, task id, and seed for each clip. This lets the user judge continuity, voice, and scene quality before editing or regenerating.
