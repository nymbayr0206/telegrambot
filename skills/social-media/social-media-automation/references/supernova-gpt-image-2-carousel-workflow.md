# Supernova GPT Image 2 carousel workflow

Session learning from Supernova carousel #2 regeneration.

## User preference

The user preferred the reference poster's integrated font style, color, phone frame, logo placement, and overall visual layout. Local overlay with DejaVu Sans was readable but did not match the desired rounded-bold healthcare infographic font. For this brand, when visual style fidelity matters more than deterministic text control, try KIE GPT Image 2 final poster generation.

If the user says "generate only 4 separate" or similar, send exactly the four slide images; do not include a contact sheet/all-in-one preview in the final response.

## Recommended approach

1. Keep the Supernova approved style reference in the brand prompt.
2. Submit one GPT Image 2 job per slide:
   - `model: gpt-image-2-text-to-image`
   - `input.aspect_ratio: 1:1`
   - prompt: "Create ONE separate 1:1 square social media carousel slide, not a collage and not four slides in one image."
3. Include exact visible fixed elements:
   - `Мэдлэгт дусал нэмэр`
   - slide ribbon `N/4`
   - Supernova-style top-right logo card
   - phone capsule `Утас: 70000303`
   - red/blue footer waves
4. Request thick rounded bold modern display typography, not plain Arial/thin font.
5. QA each slide manually for Mongolian spelling, phone number, layout, logo card, and random text before presenting.

## Tradeoff

- GPT Image 2 produced a closer poster aesthetic and font feel than the local Pillow overlay version.
- Because text is rendered by the model, spellcheck is mandatory before publishing. If exact spelling fails, fall back to text-free generation plus deterministic overlay using a better uploaded/installed font.
