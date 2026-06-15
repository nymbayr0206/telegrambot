---
name: brand-social-media-onboarding
description: "Onboard a new brand into the social content system: directory structure, logo, registry, info collection, template seeding."
version: 1.0.0
tags:
  - brand
  - onboarding
  - social-content
  - setup
  - brand-registry
---

# Brand Social Media Onboarding

## When to Use

User says "I created a new folder called X", "new brand Y", "setup brand Z here", or "save it as logo" for a brand not yet in the system.

## Workflow

### 1. Create Directory Structure

Base path: `/opt/data/social-content/brands/<slug>/`

```bash
mkdir -p /opt/data/social-content/brands/<slug>/{assets/logos,templates,source-materials,scripts,references,output}/
```

Standard slug: lowercase, no spaces, Mongolian cyrillic → latin (ирээдүймэд → ireeduimed).

### 2. Save Logo

When user sends an image saying "logo" or "save it as logo":

```bash
cp /path/to/source /opt/data/social-content/brands/<slug>/assets/logos/logo-<slug>.<ext>
```

Save in both .jpg and .png (the .png is actually a JPEG copy for flexibility — note this in a comment).

### 3. Register in Brand Registry

File: `/opt/data/social-content/brands/brand-registry.json`

```json
{
  "name": "Ирээдүймэд",
  "slug": "ireeduimed",
  "workspace": "/opt/data/social-content/brands/ireeduimed",
  "default_language": "mn",
  "approval_required": true,
  "created_at": "2026-06-05"
}
```

Add via Python:

```python
import json
with open('/opt/data/social-content/brands/brand-registry.json', 'r') as f:
    registry = json.load(f)
registry[slug] = { ... }
with open('...', 'w') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)
    f.write('\n')
```

### 4. Collect Remaining Info

After logo + registration, prompt for:
- **Contact phone** 
- **Address**
- **Brand description** — what does this brand do? (products, services, niche)
- **Content types needed** — social poster, news poster, carousel, etc.
- **Knowledge base** — any reference materials, source docs

Store info as memory and optionally as a text file in `references/brand-profile.md`.

## Brand Structure Reference

```
brands/<slug>/
├── assets/
│   └── logos/
│       ├── logo-<slug>.jpg
│       └── logo-<slug>.png
├── templates/
├── source-materials/
├── scripts/
├── references/
├── output/
```

### 5. Template Setup (if user provides a design template)

After brand basics (steps 1-4), if the user sends an image saying it's a poster template:

```bash
mkdir -p /opt/data/social-content/brands/<slug>/templates/<template-name>/
cp /path/to/reference-image /opt/data/social-content/brands/<slug>/templates/<template-name>/<template-name>-reference.jpg
```

#### 5a. Document Fixed vs Dynamic Elements

Create `templates/<template-name>/template-spec.md`:

```markdown
# <template-name> — <Brand> Poster Template

## 🔒 FIXED (ABSOLUTELY NEVER change):
- **Logo** — NEVER regenerate or modify. After KIE generates, overlay real logo if needed.
- **Background** — Fixed design, gradient, texture, colors. NEVER change.
- **Layout structure** — All sections, spacing, margins. NEVER rearrange.
- **Contact info** — Phone, address. NEVER change.
- **Brand name** — NEVER change.

## ✅ DYNAMIC (only these can change):
- **HEADLINE** — The main headline text. Only field to replace per-post.
```

The user's edutemp1 rule is strict: **only headline changes**. Other brands/templates may differ.

#### 5b. Upload to Hosting Service for KIE

Templates used with KIE image-to-image need public URLs:

```bash
# Upload to catbox.moe (72h expiry)
curl -s -F "reqtype=fileupload" -F "time=72h" \
  -F "fileToUpload=@<template-path>.jpg" \
  https://litterbox.catbox.moe/resources/internals/api.php
# Returns: https://litter.catbox.moe/xxxxxx.jpg
```

Save the URL in template-spec.md and in a knowledge base README.

#### 5c. Create Knowledge Base Entry

```bash
mkdir -p /opt/data/knowledge_bases/<brand>-<template>/
```

Create `README.md` with:
- Template name, dimensions, format
- Fixed vs dynamic breakdown
- Online URLs (for KIE)
- Brand info (phone, address, business type)
- Trigger phrases the user will use to reference it

#### 5d. KIE Generation Rule for Fixed Templates

When generating with a template reference:

```
Prompt: "Use the FIRST image (template) as the EXACT template. 
Preserve ALL fixed elements. ONLY change [dynamic field list].
Do NOT change the logo, background, layout, or any other element."
```

Use model: `gpt-image-2-image-to-image`
Input URLs: [template_url, logo_url]

## Related Skills

- `ai-global-brand-content` — once brand is onboarded, create content using its templates
- `news-poster` — news-specific poster pipeline (adapt template per brand)
- `aiglobal-success-story-carousel` — carousel generation pattern (adapt per brand)
- `kie-image-to-image` — KIE API integration for image-to-image generation with template references

## Pitfalls

1. **User voice messages** — may mishear brand names (e.g. "IdeaBeMed" → actually "Ирээдүймэд"). Always confirm the cyrillic name after hearing it.
2. **No vision model** — deepseek-v4-flash doesn't support images. When user sends a logo image, save it immediately on instruction ("Ene logo shuu save it as logo") without needing to see it.
3. **User is direct** — minimal words, expects immediate action. Don't explain, just execute. "Save it as logo" → save immediately.
4. **Memory is limited (2,200 chars)** — keep brand memory entries concise. Don't duplicate what's already in the registry file.
