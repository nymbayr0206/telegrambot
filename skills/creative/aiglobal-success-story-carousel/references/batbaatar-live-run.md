# Batbaatar Live Run — First Full Workthrough (May 31, 2026)

## Overview

First end-to-end test of the success story carousel system using KIE image-to-image.

**Student:** Батбаатар, 28, IT-ийн мэргэжилтэн
**Story:** Built an AI agent after being unable to code/understand AI
**Template reference:** `assets/references/success-story-template-ref.jpg` (user-provided)
**Real photo:** `assets/testimonials/batbaatar-testimonial.jpg` (user-provided, used in Slide 1)

## Pipeline Executed

### Step 1: Generate Content
```bash
scripts/generate_success_story.py \
  --student "Батбаатар, 28, IT-ийн мэргэжилтэн, эрэгтэй" \
  --story "AI-г ойлгодоггүй байсан хүн agent бүтээсэн|..." \
  --output carousel-plans/batbaatar-agent/
```

**Content generated:**
- Slide 1: "AI-г ойлгодоггүй байсан хүн agent бүтээсэн" — Batbaatar, 28
- Slide 2: 3 problems (❌) — didn't understand AI, didn't know agents, manual work
- Slide 3: 3 wins (✅) — learned AI Agent, built his own, saves 3-4 hrs/week
- Slide 4: 3 metrics — own AI agent, 3-4 hrs/week savings, +50% productivity

### Step 2: Upload Images to KIE
```bash
curl -X POST 'https://kieai.redpandaai.co/api/file-stream-upload' \
  -F "file=@template-ref.jpg" \
  -F "uploadPath=images/aiglobal-templates"
```
Both images uploaded successfully.

### Step 3: Submit Image-to-Image (Slide 1)
Model: `gpt-image-2-image-to-image`
Parameters: `input_urls: [template_url, photo_url]`, `aspect_ratio: "1:1"`
Prompt included: full layout description + all Mongolian text content
Task ID: `40a2807e385b99b26ead6b76fb3d9ca3`
Generation time: ~50s
Result: 1.3MB, complete branded slide

### Step 4: Remaining Slides (2-4)
Submitted all 3 in parallel. Only template reference in `input_urls` (no student photo needed for B, C, D).
- Slide 2: struggling student visual (KIE generated)
- Slide 3: happy student with laptop (KIE generated)
- Slide 4: dashboard visual (KIE generated)

### Results
- 4 credits used total
- ~100s total generation time (parallel submission)
- All text embedded by KIE
- Consistent brand styling across all 4 slides
- User approved the approach ("Pillow бол huuchin" — rejected compositing)

## Key Lessons

1. **No Pillow** — User explicitly rejected compositing. KIE image-to-image is the only approved pipeline.
2. **Upload first** — Images must be uploaded via file-stream-upload before using in input_urls.
3. **Embed ALL text in prompt** — Describe exact Mongolian text at exact layout positions.
4. **Student photo only for Slide 1** — Only include real photo in input_urls for slide 1 (intro). Slides 2-4 don't need it.
5. **Test Slide 1 first** — Don't generate all 4 upfront. Show slide 1, get approval, then proceed.
