# Worked Example: 9:16 Social Intro Video (Smart City AI Hackathon 2026)

A 30-second vertical intro video for the [Smart City AI Hackathon 2026](https://www.postly.mn/aithon2026) event.

## What It Produces

- **Format:** 1080×1920 (9:16 portrait) MP4
- **Duration:** 30 seconds
- **Style:** Dark theme with gold/orange gradient accents (brand colors from the event website)
- **Content:** Logo → "Smart City" → "AI Hackathon 2026" → Tagline → Date → Location → Fade to black
- **Audio:** Background music overlaid via FFmpeg post-processing

## Project Structure

```
aithon2026-intro/
├── index.html          # Main composition (GSAP-driven)
├── assets/
│   ├── hero.png        # Background image from event site
│   └── bg_music.mp3    # Background music track
└── (scaffolded by hyperframes init)
```

## Key Techniques

### 1. Vertical aspect ratio

Set the root `data-composition-id` div to portrait dimensions:
```html
<div id="root" data-composition-id="main" data-start="0" data-duration="30"
     data-width="1080" data-height="1920">
```

### 2. Layered backgrounds

Three stacked layers for visual depth:
1. **Grid overlay** — SVG-like repeating grid lines at 72px intervals (from site CSS)
2. **Hero image** — event background image with parallax-style crop
3. **Gradient overlay** — radial gold glow + linear gradient to dark edges

### 3. Entrance animation sequence

All elements start invisible (via `gsap.set()`) and animate in staggered:

| Element | Start | Animation |
|---------|-------|-----------|
| Glow lines | 0s | ScaleX 0→1 |
| Logo icon | 0.5s | Scale 0→1 + rotation -180→0 (back.out) |
| "Smart City" | 1.8s | Y 40→0, fade in |
| "AI Hackathon 2026" | 2.7s | Y 40→0, fade in |
| Tagline | 3.7s | Y 30→0, fade in |
| Separator | 4.5s | ScaleX 0→1 |
| Date row | 5.3s | X -40→0, fade in |
| Location row | 6.0s | X -40→0, fade in |
| Brand label | 6.8s | Fade in |

### 4. Hold phase with subtle pulsing (10–24s)

Gentle breathing animation on key text to keep it alive:
```js
tl.to(".ai-hackathon", { scale: 1.03, duration: 2, ease: "sine.inOut" }, 10);
tl.to(".ai-hackathon", { scale: 1, duration: 2, ease: "sine.inOut" }, 12);
```

### 5. Outro fade to black (24–28s)

Content fades upward, layers fade out, then background turns black:
```js
tl.to("#root", { backgroundColor: "#000", duration: 1.5 }, 26.5);
```

### 6. Audio post-processing

HyperFrames screenshot fallback mode (`PRODUCER_FORCE_SCREENSHOT=true`) drops audio. Add it after render:
```bash
ffmpeg -y -i rendered.mp4 -t 30 -i assets/bg_music.mp3 \
       -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest final.mp4
```

## Pitfalls Encountered

- **`<audio>` elements need `data-start` and `data-duration`** — without these `hyperframes lint` fails with `media_missing_data_start`
- **`PRODUCER_FORCE_SCREENSHOT=true`** required when `/dev/shm` < 256 MB (Docker containers)
- **Node.js v20 works** but emits `EBADENGINE` warning — HyperFrames v0.6.96 runs fine on v20
- **npm cache EACCES** — if `~/.npm` cache has root-owned files from prior `npx` usage, set env vars to bypass:
  ```bash
  export npm_config_prefix=/tmp/npm-global-$$
  export npm_config_cache=/tmp/npm-cache-$$
  export PRODUCER_FORCE_SCREENSHOT=true
  ```
