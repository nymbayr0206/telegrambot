# Brand Carousel Prompt Authoring Workflow

## When to Use

When a user wants to create detailed image generation prompts for branded carousel posters — either for themselves (to paste into ChatGPT/DALL-E) or for KIE GPT Image 2. This workflow extracts brand identity, layout rules, slide structure, and content type labels into a reusable prompt document.

## Workflow

### Step 1: Extract Brand Identity

Collect from the user:

| What to ask | Example |
|-------------|---------|
| Brand name | "AI Global" |
| Logo file | logo-ai-global.jpg |
| Brand colors | Primary, accent, background |
| Font | Manrope |
| Tagline | "21-р зууны супер хүнийг бэлдэнэ" |
| Contact info | Phone, website, email |
| Brand voice | Professional / Friendly / Luxury |
| Platforms | Facebook, Instagram |
| Language | Mongolian only |

### Step 2: Define Layout Rules

Ask the user for element placement on each slide:

```
┌─────────────────────────────────┐
│ [TYPE LABEL]              [LOGO] │  ← Top-Left & Top-Right
│                                   │
│         MAIN CONTENT AREA          │
│                                   │
│   📞 CONTACT   🌐 WEBSITE        │  ← Bottom-Left
└─────────────────────────────────┘
```

Common questions:
- Where does the logo go? → Ask explicitly, user usually has preference
- Where does the contact info go? → Bottom-left is common
- Slide counter? → Ask — some want it, some don't
- Background style? → Light/cream vs dark vs custom image
- Text color? → Dark on light, white on dark

### Step 3: Define Content Type Labels

Different carousel types need different labels. Common categories:

| Carousel Type | Example Label |
|---------------|---------------|
| Educational | "🎓 Боловсрол" |
| Industry Updates | "🌍 Салбарын мэдээ" |
| Product/Service | "📦 Сургалт" |
| Success Story | "🏆 Амжилтын түүх" |

### Step 4: Define Slide Structure

Standard carousel slide structure (always ask user for exact count):

| Slide | Role | Content | Typography |
|-------|------|---------|------------|
| 1 | Hook | Big headline + visual | 64px+ bold |
| 2 | Explain | 2-3 bullets | Headline 44px + body 28px |
| 3 | Deepen | Stats, proof, numbers | Gold/accent numbers 56-72px |
| 4 | CTA | Call to action | CTA headline gold 50px |

### Step 5: Handle Style References

If the user provides reference images (Pinterest, other carousels):
1. Ask them to describe the style they like from each reference
2. Incorporate key style elements into the prompt: "Italian minimal magazine", "light cream background", "clean whitespace with subtle marble texture"
3. Document the reference image path in the prompt file so it can be re-consulted

### Step 6: Handle Image Placement Rules

Decide per-content-type whether to include images:

| Carousel Type | Images allowed? |
|---------------|-----------------|
| Industry Updates | ✅ Include actual news/article images (right side, 30-40% width) |
| Educational | ❌ Text-only |
| Product/Service | ❌ Text-only |
| Success Story | ⚠️ Text-only by default, BUT when user provides a student photo → use **two-stage overlay** (see Step 6a below) |

### Step 6a: Two-Stage Overlay for Testimonial/Person Photos

When a user provides an actual person photo (student testimonial, instructor portrait, client photo) for a carousel slide:

1. **Stage 1 — KIE GPT Image 2 generates the branded slide** with the brand layout (labels, logo, contact, text content) and a reserved blank photo area (circular or rounded rectangle frame, right side ~30-35% width)
2. **Stage 2 — Pillow overlays the actual photo** onto the reserved area:
   - Resize photo to fill the placeholder dimensions
   - Create a rounded-corner mask (radius ~30px for a polished look)
   - Paste the masked photo onto the KIE-generated slide at the target coordinates
   - Save as final output

**Key details:**
- The KIE prompt should describe the photo frame but NOT attempt to generate a person — KIE will invent a face that doesn't match the real person. Instead describe: *"a large circular photo frame on the right side (approximately 35% of width) — reserved for a Mongolian IT professional portrait"*
- The user typically wants the photo on ALL slides of the testimonial carousel, not just one
- **ALWAYS use the concept approval workflow** (test Slide 1 first) when doing this — the photo placement and slide layout may need adjustment before generating the remaining 3 slides
- Font dependency check: verify `Pillow` is importable and Manrope/fallback fonts exist before generating backgrounds

**Pillow compositing code pattern:**

```python
from PIL import Image, ImageDraw

slide = Image.open('kie_generated_slide.jpg').convert('RGB')
photo = Image.open('person_photo.jpg').convert('RGB')

w, h = slide.size
pw = int(w * 0.32)  # 32% of slide width
ph = int(h * 0.50)  # 50% of slide height
photo_resized = photo.resize((pw, ph))

# Position: right side with margin
x = w - pw - int(w * 0.06)
y = int((h - ph) / 2)

# Rounded corner mask
mask = Image.new('L', (pw, ph), 0)
draw = ImageDraw.Draw(mask)
draw.rounded_rectangle([(0, 0), (pw, ph)], radius=30, fill=255)

slide.paste(photo_resized, (x, y), mask)
slide.save('final_slide.jpg', quality=95)
```

### Step 7: Save as Reusable Prompt Document

Save the final prompt instructions to the brand workspace as `carousel-prompt-instructions.md`:

```
/opt/data/social-content/brands/<brand-slug>/carousel-prompt-instructions.md
```

The document should contain:
1. Style reference description
2. Brand identity (colors, font, style)
3. Fixed layout elements with ASCII diagram
4. Content type labels table
5. Per-slide structure details
6. Image placement rules (per type)
7. Do's and Don'ts

### Step 8: Two Delivery Options

Present to the user:

| Option | How it works | When to use |
|--------|-------------|-------------|
| **User designs** | Give them the prompt to paste into ChatGPT/DALL-E with their Pinterest references | User wants creative control |
| **I generate** | Use the prompt to generate via KIE GPT Image 2 API | User wants automated generation |
