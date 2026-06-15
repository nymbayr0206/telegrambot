# Kinetic Typography Reel — AI Global Brand (Worked Example)

This document captures the pattern used to create a 15-second kinetic typography reel for AI Global using HyperFrames. Reuse this as a template for future brand reels.

## Reel Structure (15 seconds / 450 frames @ 30fps)

| Scene | Duration | Content | Animation Style |
|-------|----------|---------|-----------------|
| 1 | 0-4s | Logo reveal: **AI GLOBAL** | Gold glow, scale-in from center, divider line animate |
| 2 | 4-7.5s | Kinetic words: AI ВИБЕ КОД / AI+ АГЕНТ СУРГАЛТ | Words fly in from different directions (left, top, right, bottom) with rotation + scale |
| 3 | 7.5-11s | Tagline: **21-Р ЗУУНЫ СУПЕР ХҮН — ТА БОЛОХ УУ?** | Scale-in from small, color pulse (white↔gold) |
| 4 | 11-15s | CTA: ⚡ **ИРЭЭДҮЙГЭЭ ӨӨРЧЛӨӨРЭЙ** + contact info | Icon spin, text slide up, background flash gold at end |

## Dimensions

- AI Global reels use **720×1280** (9:16 portrait, Instagram/Facebook Reel format)
- Set in HTML: `<meta name="viewport" content="width=720, height=1280" />`
- Set in data attributes: `data-width="720" data-height="1280"`

## Brand Colors

```css
--bg: #000;                  /* Black background */
--gold: #D7AB46;             /* Primary accent */
--gold-dim: rgba(215,171,70,0.3);  /* Subtle gold */
--white: #fff;
--muted: rgba(255,255,255,0.5);  /* Secondary text */
```

## Font

Use system fonts for reliable rendering (no Google Fonts in headless Chrome):
```css
font-family: 'DejaVu Sans', sans-serif;
/* Good Cyrillic/Mongolian support, no network fetch needed */
```

## Key GSAP Patterns

### Scene 1 — Logo Reveal
```js
// Split-color logo: gold "AI" + white "GLOBAL"
tl.from(".logo-ai", { opacity: 0, scale: 0.5, rotation: -15, duration: 0.8, ease: "back.out(2)" }, 0.3);
tl.from(".logo-global", { opacity: 0, scale: 0.5, rotation: 15, duration: 0.8, ease: "back.out(2)" }, 0.5);
// Gold glow pulse
tl.to(".logo-ai", { textShadow: "0 0 30px rgba(215,171,70,0.6)", duration: 1 }, 1);
tl.to(".logo-ai", { textShadow: "0 0 10px rgba(215,171,70,0.3)", duration: 1 }, 2);
```

### Scene 2 — Kinetic Words
Each word enters from a different direction with different easing:
```js
// From left with rotation
tl.from(".kw1", { opacity: 0, x: -200, rotation: -30, duration: 0.6, ease: "power3.out" }, 4.2);
// From top with back easing
tl.from(".kw2", { opacity: 0, y: -150, rotation: 20, duration: 0.5, ease: "back.out(1.5)" }, 4.4);
// From right with elastic scale
tl.from(".kw3", { opacity: 0, x: 200, scale: 0, duration: 0.6, ease: "elastic.out(1,0.4)" }, 4.6);
// Floating animation
tl.to(".kw1", { y: -8, duration: 0.8, ease: "sine.inOut", yoyo: true, repeat: 1 }, 5.0);
```

### Scene 4 — CTA with Flash
```js
// End with a gold flash
tl.to("#s4", { backgroundColor: "#D7AB46", duration: 0.2 }, 14.5);
tl.to(".cta-text", { color: "#000", duration: 0.1 }, 14.5);
tl.to("#s4", { backgroundColor: "#000", duration: 0.3 }, 14.7);
```

## Scoping GSAP Selectors

Always scope selectors to avoid lint warnings:
```js
const R = "[data-composition-id=\"main\"]";
tl.from(R + " .logo-ai", { ... });
tl.from(R + " .kw1", { ... });
```

## Audio

HyperFrames' built-in `<audio>` element often doesn't produce audio in the rendered output (especially in screenshot fallback mode). Always add audio via ffmpeg post-processing:

```bash
ffmpeg -y -i rendered.mp4 -i assets/bg_music.mp3 -t 15 -c:v copy -c:a aac -shortest final.mp4
```

## Complete Render Command

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use --delete-prefix v22.22.3 --silent
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
export NPM_CONFIG_CACHE=/tmp/hf-cache
export PRODUCER_FORCE_SCREENSHOT=true

cd /tmp/project
hyperframes render --quality standard --output reel.mp4
ffmpeg -y -i reel.mp4 -i assets/audio.mp3 -t 15 -c:v copy -c:a aac -shortest final.mp4
```

## Output

- Source files: `/tmp/project/` (project root)
- Final MP4: 700-1000 KB for 15s at 30fps, 720×1280
- Audio-backed file: ~945 KB with audio (aac 128k)

## Variations

- For **25-30 second reels** (Certified Agent Builder style): 5 scenes instead of 4, extend duration and audio
- For **product promo**: replace kinetic words with bullet-point benefits
- For **success story**: use testimonial quote as kinetic text, add person photo
