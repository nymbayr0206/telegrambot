# Supernova carousel brand guidelines

Supernova healthcare carousel defaults and automation notes from the Telomer Effect carousel workflow.

## Workspace and source

- Workspace: `/opt/data/social-content/brands/supernova`
- Source ebook: `/opt/data/social-content/brands/supernova/source-materials/ebooks/die-entschluesselung-des-alterns-der-telomer-effekt-blackburn.pdf`
- Primary master style reference: `/opt/data/social-content/brands/supernova/assets/references/approved-carousel-style-reference-v2.jpg`
- Make.com webhook config: `/opt/data/social-content/brands/supernova/automation/make-webhook.json`
- Daily state file: `/opt/data/social-content/brands/supernova/automation/daily-carousel-state.json`

## Design rules

- Carousel format: 1:1 square, recommended 1080×1080 px.
- Generate **4 separate slide images** for publishing/webhook. Do not send an all-in-one contact sheet unless the user explicitly asks for preview QA.
- Top large rounded white title capsule: `Мэдлэгт дусал нэмэр`.
- Top-right: Supernova logo in a white rounded square/card with soft shadow.
- Left under title: blue ribbon/bookmark slide number `1/4`, `2/4`, etc.
- Main content: large rounded white panel across lower-middle area.
- Left of content panel: circular healthcare icon badges with blue outline/shadow.
- Bottom-right: white phone pill/capsule with red outline, red phone icon, text `Утас: 70000303`.
- Footer: red and blue wave ribbons across lower-left/bottom edge.
- Typography: heavy rounded bold sans-serif feel; dark navy/blue main text and red emphasis words/underlines. The user rejected the plain local DejaVu overlay look as not matching the reference closely enough.
- Colors: navy `#071B4D`, red `#E60023`/`#F20B2E`, blue `#0068B7`/`#1768B5`, sky blue/white healthcare background.
- People: if humans are visualized, make them Mongolian/East Asian-looking and respectful.
- Visual motifs: clean healthcare illustration style; sky-blue background, DNA helix, cells, telomeres/chromosomes, ECG, heart, sleep, stress, nutrition, movement, longevity motifs.

## Model preference

- For Supernova and other brand carousels, default to KIE GPT Image 2: `gpt-image-2-text-to-image` when the user wants the model-rendered reference style, font feel, logo card, phone frame, and overall poster design to match closely.
- GPT Image 2 can render the full poster more stylistically than local Pillow/DejaVu overlays, but every Mongolian/Cyrillic word must be visually QA'd before posting.
- If exact spell-checked text is more important than matching a reference font, fall back to two-stage workflow: generate no-text image, then local overlay with a better Cyrillic-capable font.
- The user may prefer style/font fidelity over deterministic local text overlay. Ask/choose GPT Image 2 for this kind of reference-matching carousel.

## User "simpler/lighter" design preference (May 2026)

After carousel #3 was published, the user said the existing Supernova carousel design was **"too heavy"** and asked for a **"lighter, simpler, cleaner"** version. They provided a reference image (light beige/cream tones, minimal, uniform brightness ~205/255, no strong contrasts).

When the user says "too heavy" or "make it lighter/simpler":
- Reduce visual density: fewer decorative elements, more white/negative space
- Use lighter color palette: cream/beige/soft pastel backgrounds instead of intense sky-blue
- Simplify text: shorter headlines, fewer body lines per slide
- Remove non-essential decorative elements (excessive bubbles, complex wave patterns)
- Consider a completely different layout structure rather than patching the existing one
- The reference image was portrait (853×1280, ~1:1.5 ratio), suggesting the user may prefer a taller canvas for simpler layouts

**⚠️ Action needed:** The existing brand guide, logo assets, and generation scripts are designed around the original "heavy" style. If the user provides a viewable reference, extract its layout and color palette, then either generate a one-off KIE prompt that reproduces the reference's simpler style, or rebuild the carousel template scripts with the new simplified design. Until then, reduce visual density when asked.

## Pitfalls

- Do not assume `origin` delivery is enough for important daily Telegram reminders; when the user says messages did not appear, update cron delivery to direct `telegram` home channel.
- Do not use a contact sheet as the asset sent to Make.com unless requested; Make/Facebook carousel workflows need separate image files.
- Cron shell scripts with inline Python (`python3 -c "..."`) using bash variable `${NEXT}` inside Python f-strings can break because Python sees f'{NEXT}' as an f-string variable, not a bash expansion. Always use a standalone `.py` file for complex cron logic rather than inline Python in shell scripts. Bug symptom: `NameError: name 'NEXT' is not defined`.
## Make.com autopost payload

When the user provides a Make.com webhook for carousel publishing, send multipart form data with these fields:

- `brand`: `supernova`
- `campaign`: e.g. `Telomer Effect Ebook Carousel Series`
- `carousel_number`: integer, 1–18
- `topic`: English or internal topic title
- `model`: `gpt-image-2-text-to-image`
- `language`: `mn`
- `format`: `1:1 square carousel`
- `caption`: Mongolian caption and hashtags
- `slide1`: JPEG file
- `slide2`: JPEG file
- `slide3`: JPEG file
- `slide4`: JPEG file

Use `curl -F` multipart upload. Consider webhook success only when HTTP status is 200 and the response is accepted by Make.com. Advance any daily state counter only after the webhook succeeds.

## Daily automation pattern

For daily 18-carousel series:

1. Store webhook URL in the brand workspace under `automation/make-webhook.json`.
2. Store state in `automation/daily-carousel-state.json` with `next_carousel`, `completed`, and `last_status`.
3. Schedule at the requested local time. For Asia/Ulaanbaatar 09:00, use `0 1 * * *` UTC.
4. Generate the next 4 separate slides using GPT Image 2.
5. Send the 4 files to Make.com as multipart form data.
6. Increment `next_carousel` only after webhook success.
7. Stop or report no-op after carousel 18.

## Pitfalls

- Do not assume `origin` delivery is enough for important daily Telegram reminders; when the user says messages did not appear, update cron delivery to direct `telegram` home channel.
- Do not use a contact sheet as the asset sent to Make.com unless requested; Make/Facebook carousel workflows need separate image files.
- The user may prefer style/font fidelity over deterministic local text overlay. Ask/choose GPT Image 2 for this kind of reference-matching carousel.