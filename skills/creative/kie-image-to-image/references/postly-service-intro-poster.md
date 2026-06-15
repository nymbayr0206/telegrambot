# Postly Service Introduction Poster — KIE Image-to-Image Worked Example

This reference documents the KIE GPT Image 2 Image-to-Image approach for Postly (a brand without a dedicated template file like AI Global's temp1).

## Key Difference from AI Global

Postly has **no dedicated poster template** (no temp1/reeltemp1). Instead:
- Use an existing brand reference asset as the template (e.g. `postly-offer-pricing-infographic.jpg`)
- The prompt must be **comprehensive** — it defines the full layout, colors, and text content since there's no fixed template to preserve

## Brand Reference

| Attribute | Value |
|---|---|
| Brand colors | Turquoise `#5ED4C0`, Aqua `#4CBFDD`, Deep teal `#063B4A` |
| Font style | Nunito Bold (rounded modern sans-serif) — reference in prompt |
| Background | White to light cyan gradient |
| Format | 1:1 square (1080×1080) |
| Phone | **94594000** (Postly contact) |
| Website | www.postly.mn |
| Logo | `/opt/data/social-content/brands/postly/assets/logos/postly-logo-turquoise-p.jpg` |
| Style reference | `/opt/data/social-content/brands/postly/assets/references/postly-offer-pricing-infographic.jpg` |

## Related Poster Patterns

- **Service Intro / Pricing** — this reference (service categories + pricing cards)
- **Digital Worker Workshop** — `references/postly-digital-worker-workshop-poster.md` (trainer photo + agent cards + free training CTA) |

## Workflow

### Step 1: Upload Reference Image to tmpfiles.org

Use the existing pricing infographic as a style reference:

```python
import subprocess, json
result = subprocess.run(
    ["curl", "-s", "-F", "file=@/opt/data/social-content/brands/postly/assets/references/postly-offer-pricing-infographic.jpg",
     "https://tmpfiles.org/api/v1/upload"],
    capture_output=True, text=True, timeout=30
)
data = json.loads(result.stdout)
url_path = data["data"]["url"]
parts = url_path.rstrip('/').split('/')
template_url = f"https://tmpfiles.org/dl/{parts[-2]}/{parts[-1]}"
```

### Step 2: Submit to KIE

```python
task_data = {
    "model": "gpt-image-2-image-to-image",
    "input": {
        "input_urls": [template_url],
        "prompt": "<see prompt structure below>",
        "aspect_ratio": "1:1",
        "resolution": "1K"
    }
}
```

### Step 3: Poll and Download

Standard KIE poll loop (see main SKILL.md). Use the signed download URL endpoint for download.

## Prompt Structure for Service Intro Poster

The prompt must be a complete layout specification since there's no fixed template. Structure it as:

```
Create a single 1:1 square social media poster for POSTLY — AI content marketing service.

BRAND STYLE:
- Background: clean white with light turquoise/aqua gradient
- Accent colors: turquoise (#5ED4C0) and aqua (#4CBFDD)
- Headings: deep teal (#063B4A)
- Clean SaaS style with rounded cards

LAYOUT (top to bottom):

TOP SECTION:
- Logo + "POSTLY" in deep teal at top
- Tagline bar: "🤖 AI АГЕНТ СУУРИТАЙ КОНТЕНТ МАРКЕТИНГ"

PURPOSE SECTION (Контентын зориулалт):
1. 🏷️ БРЭНД ТАНИЛЦУУЛГА
2. 📚 БОЛОВСРОЛЫН
3. 🔧 ҮЙЛЧИЛГЭЭНИЙ ТАНИЛЦУУЛГА
4. ✨ БРЭНД КОНТЕНТ
5. 🚀 БООСТ / СУРТАЛЧИЛГАА

PRICING SECTION (Үнийн саналууд):
Three side-by-side cards...

[Include ALL text in the prompt — bullet points, prices, labels]
```

## All Text MUST Be in Cyrillic Mongolian

Hard rule: every label, bullet, price, and description in Cyrillic Mongolian only. No English/Latin letters for Mongolian words, even in punctuation or abbreviation.

## Source Script

The working KIE submission script is at:
`/opt/data/social-content/brands/postly/generate_via_kie.py`
