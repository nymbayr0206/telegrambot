---
name: brand-book-creator
description: "Guide the user through providing brand book details manually (NOT AI-generated). Takes user-provided brand info (logo, colors, fonts, industry, vibe) and saves structured brand notes. The user rejected AI-generated brand books — this skill is a checklist / interview guide for manual brand entry."
version: 2.0.0
author: Hermes Agent
tags: [branding, brand-book, manual-input, interview-guide]
---

# Brand Book Creator

## When to Use

Use this skill when the user wants to **create or update a brand book / brand guide** for a new brand, OR when the user announces a new brand workspace and wants to start generating content for it. Do NOT generate any visuals or backgrounds unless explicitly asked. The user prefers to provide all brand details **manually** — this skill is a structured interview guide for collecting those details and onboarding the brand into the content system.

## Overview: Brand Onboarding into the Social Content System

This user operates **multiple brands** (AI Global, Supernova, Postly, USI Machinery, AgenticForce, and now IdeaBeMed) in a shared content ecosystem at `/opt/data/social-content/brands/`. The recurring pattern is:

1. User announces new brand name (e.g. "I created IdeaBeMed folder")
2. User provides brand details: logo (as image), phone, address, knowledge base, content direction
3. Agent sets up the brand workspace, registers it, and generates content (carousel, poster, news)

This skill covers BOTH the brand-guide interview AND the system setup that follows.

## Brand Workspace Setup

### Folder Structure Convention

Every brand workspace follows:
```
/opt/data/social-content/brands/<brand-slug>/
├── brand-guide.md              # Brand info (this skill's output)
├── assets/
│   ├── logos/                  # Logo files (user-provided or extracted)
│   ├── backgrounds/            # Template backgrounds (e.g. temp1.jpg)
│   └── references/             # Reference images for KIE generation
├── templates/
│   └── <template-name>/        # Brand-specific templates
├── generated/                   # Output content
└── scripts/                     # Brand-specific generation scripts
```

### Brand Registration

After creating the workspace folder, register the brand in `/opt/data/social-content/brands/brand-registry.json`:

```json
{
  "<brand-slug>": {
    "name": "Brand Name",
    "slug": "<brand-slug>",
    "workspace": "/opt/data/social-content/brands/<brand-slug>",
    "default_language": "mn",
    "approval_required": true
  }
}
```

### Content Type Mapping

When the user asks for brand content, map to a generation approach:

| Content Type | Recommended Approach |
|---|---|
| Carousel (multi-slide) | KIE image-to-image with reference background + user images |
| Single poster / News poster | KIE image-to-image with reference template + news image |
| News post (news-post-1 style) | Two-stage: KIE generates content, then Pillow overlays real logo |

If the brand has no reference template yet, use **text-to-image** (gpt-image-2-text-to-image) with a descriptive prompt that includes brand colors, logo placement, and contact info — OR ask the user for a design reference.

## Workflow

### Step 1: Ask for the Logo

The user may upload a logo image. If they do:
- Save it to `assets/logos/` in the brand directory
- Note the file path and dimensions

**Do NOT** attempt to analyze the logo with vision to extract colors or vibe unless the user asks. Keep it simple.

### Step 2: Interview for Brand Details (User Provides Everything)

Ask the user for each field below, one at a time. Let them tell you; do not infer.

- **Brand name** (how it's written — Mongolian, English, or both)
- **Tagline / slogan** (Mongolian and/or English)
- **Industry** (tech, education, luxury, health, etc.)
- **Brand voice / vibe** (professional, playful, educational, luxury, modern)
- **Primary language** (Mongolian, English, or bilingual)
- **Contact** (phone, email, website)
- **Target platforms** (Facebook, Instagram, etc.)

### Step 3: Colors

Ask: "Do you have 2-3 brand colors? Provide hex codes or describe them."
If they provide them, note them. If they don't, just write "TBD — user will provide later."

**Do NOT** try to extract colors from the logo image. The user will give them.

### Step 4: Fonts

Ask: "What font(s) do you want for headlines and body text?"
If they know, note it. If they don't, write "TBD".

### Step 5: Save to brand-guide.md

Write all collected info to the brand's `brand-guide.md` file. Use this structure:

```markdown
# [Brand Name] — Brand Guide

**Status:** ⏳ In progress — some fields pending user input

## Brand Identity

| Field | Value |
|---|---|
| Brand name | ... |
| Tagline | ... |
| Industry | ... |
| Brand voice | ... |
| Primary language | ... |
| Contact | ... |
| Platforms | ... |

## Brand Colors

- ... (user to provide)

## Typography

- Font: ... (user to provide)

## Logo

- File: `assets/logos/...`

## Still needed from user

- [ ] Colors
- [ ] Fonts
- [ ] Any other pending items
```

### Step 6: Offer to Save as Skill

If the brand has enough structure to warrant a dedicated content-generation skill (templates, color palette, layout rules), ask the user: "Do you want me to save this as a reusable skill for generating content?"

Do NOT create a skill without asking.

## Pitfalls

1. **Vision model may not support images** — Some models (deepseek-v4-flash, etc.) cannot process image attachments via the vision tool. When the user sends a logo or design reference image and vision fails, upload to a temp host (catbox/litterbox) and try browser-based vision, OR ask the user to describe what the image shows (logo style, colors, layout elements).
2. **Brand workspace may not exist yet** — When the user says they "created" a folder, check `/opt/data/social-content/brands/` first. They may be telling you to create it, or it may exist elsewhere.
3. **Brand-registry.json must stay in sync** — After creating a workspace, always register it. Other tools (Make.com webhooks, cron jobs) read this registry to find brands.

## Do NOT

- ❌ Do NOT generate AI brand book images (KIE GPT Image 2 or otherwise) unless the user explicitly asks
- ❌ Do NOT extract colors from the logo automatically
- ❌ Do NOT suggest fonts based on industry
- ❌ Do NOT generate poster backgrounds
- ❌ Do NOT composite brand book images

The user provides everything. You just write it down and organize it.

## Important Notes

- This user has explicitly rejected AI-generated brand books ("I don't like this. Just discard.")
- The brand guide lives at `/opt/data/social-content/brands/<brand>/brand-guide.md`
- Assets go in `/opt/data/social-content/brands/<brand>/assets/`
- Generated content goes in `/opt/data/social-content/brands/<brand>/generated/`
