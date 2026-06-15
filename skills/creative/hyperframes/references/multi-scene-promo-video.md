# Multi-Scene Promo Video Pattern

Created during Smart City AI Hackathon 2026 intro video (63s, 1080×1920 9:16).
This pattern handles sequential scene-by-scene animation with fade transitions,
staggered element entrances, and audio post-processing.

## Scene Architecture

Each scene is a separate `<div class="scene" id="scene-X">` inside the root composition.
Every scene gets its own GSAP timeline block:

```
Scene 1a: Hero (0-6s)     → fade out → 
Scene 1b: Organizers (7-14s) → fade out → 
Scene 1c: Details (15-18s) → fade out → 
Scene 2: Audience (19-26s) → fade out → 
...continues to final CTA scene
```

## Key HTML Structure

```html
<div id="root" data-composition-id="main" data-start="0" data-duration="63"
     data-width="1080" data-height="1920">
  <div class="scene-content">
    <!-- Persistent background elements -->
    <div class="grid-overlay clip" data-start="0" data-duration="63" data-track-index="1"></div>
    <div class="grad-overlay clip" data-start="0" data-duration="63" data-track-index="2"></div>

    <!-- SCENE 1: Title -->
    <div class="scene" id="scene-hero">
      <div class="hero-bg clip" data-start="0" data-duration="6.5" data-track-index="3">
        <img src="assets/hero.png" alt="hero" />
      </div>
      <div class="smart-city clip" data-start="1.2" data-duration="5" data-track-index="12">Smart City</div>
    </div>

    <!-- SCENE 2: Organizers -->
    <div class="scene" id="scene-organizers">
      <div class="org-card clip" data-start="8.0" data-duration="6" data-track-index="22">...</div>
    </div>

    <audio data-audio-id="bg-music" data-start="0" data-duration="63"
           src="assets/bg_music.mp3" loop></audio>
  </div>
</div>
```

## GSAP Timeline Pattern

Always set initial states with `tl.set()`, then animate in, hold, fade out:

```js
const tl = gsap.timeline({ paused: true });

// ==== SCENE N ====
tl.set("#scene-N .title", { opacity: 0, y: -30 });
tl.set("#scene-N .cards", { opacity: 0, y: 30, scale: 0.9 });
tl.set("#scene-N .sep-line", { scaleX: 0 });

tl.to("#scene-N .title", { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }, startTime);
tl.to("#scene-N .sep-line", { scaleX: 1, duration: 0.4, ease: "power2.inOut" }, startTime + 0.5);
tl.to("#scene-N .cards", { opacity: 1, y: 0, scale: 1, duration: 0.4, stagger: 0.35,
    ease: "back.out(1.5)" }, startTime + 1.0);

// Fade out entire scene
tl.to("#scene-N > *", { opacity: 0, duration: 0.3, stagger: 0.03,
    ease: "power2.in" }, endTime - 0.5);
```

## Timing Constants

```
startTime = scene start
endTime   = scene end (exclusive)
duration  = endTime - startTime
```

Each scene's clip `data-duration` should match or exceed the scene's timeline duration.

## Audio Post-Processing

HyperFrames `<audio>` elements often render without audio in the MP4
(especially in screenshot fallback mode). Always add audio via FFmpeg:

```bash
ffmpeg -y -i rendered.mp4 -t <duration_sec> -i bg_music.mp3 \
       -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest final.mp4
```

Flags explained:
- `-t <duration_sec>` on the audio input: trim music to match video length
- `-shortest`: stop when the shorter stream ends (video)
- `-map 0:v:0 -map 1:a:0`: take video from input 0, audio from input 1

## Staggering Patterns

| Goal | GSAP Parameter | Example |
|------|---------------|---------|
| Cards appear one by one | `stagger: 0.35` | 4 cards → each 0.35s apart |
| Text lines fade in sequence | `stagger: 0.15` | 3 lines → each 0.15s apart |
| Row by row | `stagger: 0.25` | 2 info rows → 0.25s apart |
| Batch fade out | `stagger: 0.03` | Quick ~0.1s staggered fade |

## Rendering with Limited /dev/shm

```bash
export PRODUCER_FORCE_SCREENSHOT=true
hyperframes render --quality draft --output video.mp4
```

## Full Pipeline Example

```bash
# 1. Set up
export PATH="/tmp/npm-global-139179/bin:$PATH"
export npm_config_prefix=/tmp/npm-global-139179
export PRODUCER_FORCE_SCREENSHOT=true

# 2. Create project
cd /tmp && npx hyperframes init my-video --non-interactive

# 3. Copy assets
cp hero.png my-video/assets/
cp bg_music.mp3 my-video/assets/

# 4. Write index.html with multi-scene composition

# 5. Check
cd my-video && npm run check

# 6. Render (no audio from hyperframes)
npm run render -- --quality draft --output video.mp4

# 7. Add audio
ffmpeg -y -i video.mp4 -t 63 -i assets/bg_music.mp3 \
       -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest final.mp4

# 8. Verify
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4
ffprobe -v error -show_streams -select_streams a -of default=nw=1:nk=1 final.mp4
```
