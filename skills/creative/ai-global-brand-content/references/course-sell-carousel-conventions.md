# AI Global Course Sell Carousel — Conventions (v1)

From June 2026 session — AI+ Agent course sell carousel (4 slides).

## Slide Structure

| Slide | Title | Content |
|-------|-------|---------|
| 1 | Instructor Intro | Hook tagline + instructor name (full) + 3 credential lines (with institution names) |
| 2 | Time Savings | 4 automation bullet points with weekly hours + monthly total |
| 3 | Workforce Efficiency | 1 AI Builder vs traditional team + ₮ cost comparison |
| 4 | CTA | Course name + 3 benefits + limited spots + no-code requirement + CTA |

## CTA Rules (User Preference — Hard Rules)

- ❌ NEVER include a start date on posters
- ❌ NEVER use "Бүртгүүлэх" / "Register" — user explicitly rejects this
- ✅ Use "Мэдээлэл авах → Коммент бичээрэй" or "Коммент бичээрэй 👇"
- ✅ ALWAYS include limited spots: "Зөвхөн X хүнийг бүртгэнэ" (e.g. 20)
- ✅ Slide 1 MUST feature instructor's real photo on temp1 background
- ✅ All text in Cyrillic Mongolian

## Text Handling in Prompts

GPT Image 2 auto-converts English brand names to Cyrillic when "Cyrillic Mongolian only" is specified:
- "AI" → "АИ" or "ай" ❌
- "IO Institute" → "ИО" ❌
- "Med Koders LLC" may also get Cyrillic-ized

**Fix:** Two-step language instruction:
1. "Text in CYRILLIC MONGOLIAN only for Mongolian words"
2. "EXCEPTION: English brand names like AI and IO Institute must stay in LATIN letters (AI, IO Institute). Do NOT write them as АИ or ИО."

## Slide 1 Instructor Photo

- Upload temp1 + instructor photo to tmpfiles.org
- Submit image-to-image with both URLs in input_urls
- Slide 1 uses instructor photo embedded in circular portrait frame
- Slides 2-4 use temp1 text-only (no photo)

## Approved Template

temp1.jpg at `/opt/data/social-content/brands/ai-global/assets/backgrounds/temp1.jpg`
- User may replace this file at any time — always overwrite and re-upload
- temp1 is IMMUTABLE during generation — name each element that must NOT change (logo, phone, background, decorations)
