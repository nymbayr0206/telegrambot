# KIE GPT Image 2 carousel poster workflow

Use this when the user wants carousel posters whose typography, frames, logo cards, and footer waves closely match a visual reference. In the Supernova session, the user preferred GPT Image 2's rendered poster typography over local DejaVu/Pillow overlays.

## Endpoint and model

Use the KIE marketplace jobs endpoint:

```json
{
  "model": "gpt-image-2-text-to-image",
  "input": {
    "prompt": "...",
    "aspect_ratio": "1:1"
  }
}
```

Submit via:

```text
POST https://api.kie.ai/api/v1/jobs/createTask
GET  https://api.kie.ai/api/v1/jobs/recordInfo?taskId=...
```

Parse `data.resultJson` if present; it may contain a JSON string such as `{"resultUrls":["https://..."]}`. Download outputs immediately.

## Prompting pattern for four-slide carousels

Generate each slide separately. Include this instruction explicitly:

```text
Create ONE separate 1:1 square social media carousel slide, not a collage and not four slides in one image.
```

For each slide, provide:

- Brand layout details: title capsule, logo placement, slide ribbon, content panel, icon badge, phone capsule, footer waves.
- Exact slide number: `1/4`, `2/4`, etc.
- Exact headline and body text.
- Typography direction: thick rounded bold modern display style; avoid plain Arial/thin fonts.
- Color palette and target audience.
- Human depiction rule: Mongolian/East Asian-looking people when relevant.

## QA rule

GPT Image 2 can render Mongolian text and poster typography much closer to a reference than deterministic local overlays, but model-rendered Cyrillic can still have spelling or spacing errors. Visually inspect every slide before publishing or webhook delivery when approval is required.

## When to prefer this over local overlay

Prefer GPT Image 2 full-poster generation when:

- The user complains that local fonts do not match the reference.
- The requested style depends on integrated typography, frames, and decorative layout.
- The receiving workflow wants final images, not editable text layers.

Fallback to text-free generation + local overlay when exact legal/medical wording must be guaranteed and model-rendered text is unreliable.
