---
name: hyperframes
description: Create HTML-based video compositions, animated title cards, social overlays, captioned talking-head videos, audio-reactive visuals, and shader transitions using HyperFrames. HTML is the source of truth for video. Use when the user wants a rendered MP4/WebM from an HTML composition, wants to animate text/logos/charts over media, needs captions synced to audio, wants TTS narration, or wants to convert a website into a video.
version: 1.0.0
author: heygen-com
license: Apache-2.0
platforms: [linux, macos, windows]
prerequisites:
  commands: [node, ffmpeg, npx]
metadata:
  hermes:
    tags: [creative, video, animation, html, gsap, motion-graphics]
    related_skills: [manim-video, meme-generation]
    category: creative
    requires_toolsets: [terminal]
---

# HyperFrames

HTML is the source of truth for video. A composition is an HTML file with `data-*` attributes for timing, a GSAP timeline for animation, and CSS for appearance. The HyperFrames engine captures the page frame-by-frame and encodes to MP4/WebM with FFmpeg.

**Complement to `manim-video`:** Use `manim-video` for mathematical/geometric explainers (equations, 3B1B-style). Use `hyperframes` for motion-graphics, talking-head with captions, product tours, social overlays, shader transitions, and anything driven by real video/audio media.

## When to Use

- User asks for a rendered video from text, a script, or a website
- Animated title cards, lower thirds, or typographic intros
- Captioned narration video (TTS + captions synced to waveform)
- Audio-reactive visuals (beat sync, spectrum bars, pulsing glow)
- Scene-to-scene transitions (crossfade, wipe, shader warp, flash-through-white)
- Social overlays (Instagram/TikTok/YouTube style)
- Website-to-video pipeline (capture a URL, produce a promo)
- Any HTML/CSS/JS animation that must render deterministically to a video file

Do **not** use this skill for:
- Pure math/equation animation (→ `manim-video`)
- Image generation or memes (→ `meme-generation`, image models)
- Live video conferencing or streaming

## Quick Reference

```bash
npx hyperframes init my-video               # scaffold a project
cd my-video
npx hyperframes lint                        # validate before preview/render
npx hyperframes preview                     # live-reload browser preview (port 3002)
npx hyperframes render --output final.mp4   # render to MP4
npx hyperframes doctor                      # diagnose environment issues
```

Render flags: `--quality draft|standard|high` · `--fps 24|30|60` · `--format mp4|webm` · `--docker` (reproducible) · `--strict`.

Full CLI reference: [references/cli.md](references/cli.md).
Setup troubleshooting (this system): [references/setup-troubleshooting.md](references/setup-troubleshooting.md).
AI Global brand kinetic typography reel (worked example): [references/kinetic-typography-reel.md](references/kinetic-typography-reel.md).
Multi-scene promo video pattern — sequential scenes, fade transitions, staggered entrances, audio post-processing: [references/multi-scene-promo-video.md](references/multi-scene-promo-video.md).  
Social intro video 9:16 (worked example — Smart City AI Hackathon 2026): [references/aithon2026-social-intro.md](references/aithon2026-social-intro.md).

## Prerequisites

- **Node.js >= 22** — On this system, Node v20 is installed (`v20.19.2`). HyperFrames v0.6.81 installs with a warning on v20 and most features work, but some rendering features may have issues. Upgrade to v22 if possible.
- **FFmpeg** — Must be installed and in PATH.
- **npm** — Global install may fail with EACCES on `/usr/local/lib/node_modules`. Fix: set npm prefix to a user-writable directory:

```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
export PATH="$HOME/.npm-global/bin:$PATH"
# Then install or run hyperframes
```

## Environment Setup (this system — hermes-agent on Debian)

### Node.js
System node is v20.19.2 (Debian stable). HyperFrames requires >= v22.
Install with nvm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 22
nvm use --delete-prefix v22.22.3  # --delete-prefix needed if ~/.npmrc has prefix set
```

### npm prefix (EACCES fix)
Global npm install fails with EACCES on `/usr/local/lib/node_modules`. Fix:

```bash
mkdir -p ~/.npm-global
echo "prefix=$HOME/.npm-global" >> ~/.npmrc
export PATH="$HOME/.npm-global/bin:$PATH"
npm install -g hyperframes@latest
```

### Chrome-headless-shell
HyperFrames needs Chrome for rendering. System Chrome not available; install:

```bash
# 1. Make sure unzip is available (not installed on this system)
#    Use Python as fallback:
python3 -c "
import zipfile, os, shutil, urllib.request
url = 'https://storage.googleapis.com/chrome-for-testing-public/130.0.6723.91/linux64/chrome-headless-shell-linux64.zip'
urllib.request.urlretrieve(url, '/tmp/chrome.zip')
with zipfile.ZipFile('/tmp/chrome.zip', 'r') as z:
    z.extractall('/tmp/chrome-extract')
for root, dirs, files in os.walk('/tmp/chrome-extract'):
    for f in files:
        if 'chrome-headless-shell' in f:
            os.makedirs(os.path.expanduser('~/.local/bin'), exist_ok=True)
            shutil.copy2(os.path.join(root, f), os.path.expanduser('~/.local/bin/chrome-headless-shell'))
            os.chmod(os.path.expanduser('~/.local/bin/chrome-headless-shell'), 0o755)
"

# 2. Add to PATH
export PATH="$HOME/.local/bin:$PATH"
export PUPPETEER_EXECUTABLE_PATH="$HOME/.local/bin/chrome-headless-shell"
```

### /dev/shm size
Chrome needs ≥256 MB of /dev/shm. Container has only 64 MB.
Fix by running the container with `--shm-size=512m`, or set env var:

```bash
export PRODUCER_FORCE_SCREENSHOT=true   # fallback mode, works without /dev/shm
```

### Verify installation

```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
hyperframes doctor
```

Expected output: ✓ Version, ✓ Node.js, ✓ FFmpeg, ✓ Chrome (if shm issue is worked around).

## Procedure

### 1. Plan before writing HTML

Before touching code, articulate at a high level:
- **What** — narrative arc, key moments, emotional beats
- **Structure** — compositions, tracks (video/audio/overlays), durations
- **Visual identity** — colors, fonts, motion character (explosive / cinematic / fluid / technical)
- **Hero frame** — for each scene, the moment when the most elements are simultaneously visible. This is the static layout you'll build first.

**Visual Identity Gate (HARD-GATE).** Before writing ANY composition HTML, a visual identity must be defined. Do NOT write compositions with default or generic colors (`#333`, `#3b82f6`, `Roboto` are tells that this step was skipped). Check in order:

1. **`DESIGN.md` at project root?** → Use its exact colors, fonts, motion rules, and "What NOT to Do" constraints.
2. **User named a style** (e.g. "Swiss Pulse", "dark and techy", "luxury brand")? → Generate a minimal `DESIGN.md` with `## Style Prompt`, `## Colors` (3-5 hex with roles), `## Typography` (1-2 families), `## What NOT to Do` (3-5 anti-patterns).
3. **None of the above?** → Ask 3 questions before writing any HTML:
   - Mood? (explosive / cinematic / fluid / technical / chaotic / warm)
   - Light or dark canvas?
   - Any brand colors, fonts, or visual references?

   Then generate a `DESIGN.md` from the answers. Every composition must trace its palette and typography back to `DESIGN.md` or explicit user direction.

### 2. Scaffold

```bash
npx hyperframes init my-video --non-interactive
```

Templates: `blank`, `warm-grain`, `play-mode`, `swiss-grid`, `vignelli`, `decision-tree`, `kinetic-type`, `product-promo`, `nyt-graph`. Pass `--example <name>` to pick one, `--video clip.mp4` or `--audio track.mp3` to seed with media.

### 3. Layout before animation

Write the static HTML+CSS for the **hero frame first** — no GSAP yet. The `.scene-content` container must fill the scene (`width:100%; height:100%; padding:Npx`) with `display:flex` + `gap`. Use padding to push content inward — never `position: absolute; top: Npx` on a content container (content overflows when taller than the remaining space).

Only after the hero frame looks right, add `gsap.from()` entrances (animate **to** the CSS position) and `gsap.to()` exits (animate **from** it).

### 4. Animate with GSAP

Every composition must:
- Register its timeline: `window.__timelines["<composition-id>"] = tl`
- Start paused: `gsap.timeline({ paused: true })` — the player controls playback
- Use finite `repeat` values (no `repeat: -1` — breaks the capture engine). Calculate: `repeat: Math.ceil(duration / cycleDuration) - 1`.
- Be deterministic — no `Math.random()`, `Date.now()`, or wall-clock logic. Use a seeded PRNG if you need pseudo-randomness.
- Build synchronously — no `async`/`await`, `setTimeout`, or Promises around timeline construction.

### 5. Transitions between scenes

Multi-scene compositions require transitions. Rules:
1. **Always use a transition between scenes** — no jump cuts.
2. **Always use entrance animations** on every scene element (`gsap.from(...)`).
3. **Never use exit animations** except on the final scene — the transition IS the exit.
4. The final scene may fade out.

### 6. Audio, captions, TTS, audio-reactive, highlighting

- **Audio:** always a separate `<audio>` element (video is `muted playsinline`). Every `<audio>` element MUST have `data-start` and `data-duration` attributes, otherwise `hyperframes lint` throws a hard error (`media_missing_data_start`). Example:
  ```html
  <audio data-audio-id="bg-music" data-start="0" data-duration="30" src="assets/bg_music.mp3" loop></audio>
  ```
- **TTS:** `npx hyperframes tts "Script text" --voice af_nova --output narration.wav`. List voices with `--list`.
- **Captions:** `npx hyperframes transcribe narration.wav` → word-level transcript.

### 7. Lint, validate, inspect, preview, render

```bash
npx hyperframes lint              # catches missing data-composition-id, overlapping tracks, unregistered timelines
npx hyperframes validate          # WCAG contrast audit at 5 timestamps
npx hyperframes inspect           # visual layout audit — overflow, off-frame elements, occluded text
npx hyperframes preview           # live browser preview
npx hyperframes render --quality draft --output draft.mp4    # fast iteration
npx hyperframes render --quality high --output final.mp4     # final delivery
```

### 8. Website-to-video (if the user gives a URL)

Use the 7-step capture-to-video workflow in `references/website-to-video.md`.

## Pitfalls

- **`HeadlessExperimental.beginFrame' wasn't found`** — Chromium 147+ removed this protocol. Ensure you're on `hyperframes@>=0.4.2` (auto-detects and falls back to screenshot mode). Escape hatch: `export PRODUCER_FORCE_SCREENSHOT=true`.
- **System Chrome (not `chrome-headless-shell`)** — renders hang for 120s then timeout. Run `npx puppeteer browsers install chrome-headless-shell`.
- **`repeat: -1` anywhere** — breaks the capture engine. Always compute a finite repeat count.
- **Building timelines async** — the capture engine reads `window.__timelines` synchronously after page load. Never wrap timeline construction in `async`, `setTimeout`, or a Promise.
- **Using video for audio** — always muted `<video>` + separate `<audio>`.
- **`/dev/shm` too small (64 MB)** — Chrome needs ≥256 MB for rendering. In Docker containers, size is often locked. Workaround: `export PRODUCER_FORCE_SCREENSHOT=true` (falls back to screenshot-based capture, uses less shm).
- **Rendered video has no audio** — `<audio data-audio-id="...">` in the HTML may not produce audio in the output file, especially in screenshot fallback mode. Always verify with `ffprobe`. Workaround: add audio via FFmpeg post-processing:
  ```bash
  ffmpeg -y -i rendered.mp4 -i assets/audio.mp3 -t <duration> -c:v copy -c:a aac -shortest final.mp4
  ```
- **Google Fonts fail in sandboxed renders** — `@import url('...fonts.googleapis.com...')` needs network access blocked during render. Use system fonts instead: DejaVu Sans (good Cyrillic/Mongolian) or DejaVu Serif.
- **`unscoped_gsap_selector` lint warnings** — Always scope GSAP selectors to the composition: `const R = "[data-composition-id=\"main\"]"; tl.from(R+" .my-class", {...})`.

## Verification

Before and after rendering:

1. **Lint + validate + inspect pass:** `npx hyperframes lint --strict && npx hyperframes validate && npx hyperframes inspect`
2. **File exists + non-zero:** `ls -lh final.mp4`
3. **Duration matches `data-duration`:** `ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4`
4. **Audio present if expected:** `ffprobe -v error -show_streams -select_streams a -of default=nw=1:nk=1 final.mp4 | head -1`
