---
name: ai-global-reel-workflow
description: AI Global reel generation — reeltemp1 scenes + dialogue V3 voiceover + TikTok captions and quick image-to-reel with sound + FFmpeg lighting effects. Always ask user for approval before each step.
---

# AI Global Reel Workflow (Consistent Rules)

**Always confirm with the user before starting any step.** Never generate without approval.

Two distinct reel modes:
1. **Multi-scene KIE reel** (standard) — KIE-generated scenes + voiceover + captions
2. **Quick single-image reel** — one image + sound/music + FFmpeg lighting effects

---

## Mode A: Multi-Scene KIE Reel (Standard)

### Step 1: Plan & Get Approval

Present the reel plan: scene descriptions, voiceover text, duration. Wait for user approval.

### Step 2: Scene Images

Use KIE `gpt-image-2-image-to-image`:
- Model: `gpt-image-2-image-to-image`
- Aspect: `9:16`
- Background: `reeltemp1` (assets/reeltemp1.jpg) — MUST keep it EXACTLY as-is
- For instructor scenes: input_urls = [reeltemp1_url, instructor_photo_url]
- For other scenes: input_urls = [reeltemp1_url]
- Resolution: omit (default works)
- NO text on images — captions added by FFmpeg

### Step 3: Voiceover

Use KIE `elevenlabs/text-to-dialogue-v3`:
```json
model: elevenlabs/text-to-dialogue-v3
input:
  dialogue:
    - text: "..."
      voice: "Lily"
```
- Split text into dialogue entries matching scene structure
- Total chars ≤ 5000

### Step 4: Captions (TikTok Style)

SRT format with word-chunk animation:
- Font: Manrope-Bold (~/.fonts/manrope/Manrope-Bold.ttf)
- FontSize: 10
- PrimaryColour: yellow (`&H0000FFFF`)
- OutlineColour: black (`&H00000000`)
- Outline: 0.5 (thin)
- Alignment: 2 (bottom center)
- MarginV: 40
- Split text into 2-word chunks per subtitle entry
- Each chunk timed proportionally to scene duration

### Step 5: Speed & Assembly

- Calculate `atempo` dynamically: `atempo = actual_audio_duration / target_duration`. Default target ~40s, so for typical ~50s VO use atempo=1.25. Always measure actual audio duration first, then calculate.
- Use FFmpeg ONLY for: merging scene images, adding audio, burning captions
- NEVER use FFmpeg for generation (images, audio)

### Step 6: Deliver

- Show final reel to user for approval
- If approved: send to Make.com webhook with `content_type=reel`
- Webhook: https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e

---

## Mode B: Quick Single-Image Reel (Sound + Lighting Effects)

Use this when the user provides a single image and says "make a reel" with sound and effects — no KIE scene generation needed.

### Step 1: Prepare the Image

- Input image should ideally be 9:16 portrait (720x1280 or 1080x1920)
- If the image is a different aspect ratio, pad/crop to 9:16 with FFmpeg:
  ```bash
  ffmpeg -y -i input.jpg -vf "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=black" padded.jpg
  ```

### Step 2: Get the Sound/Audio

- If the user says "манай sound" / "our sound", check for:
  - `bg_music.mp3` at `/opt/data/social-content/brands/ai-global/generated/free-workshop-video/bg_music.mp3` (40s, brand background music)
  - Any voiceover .mp3 files in the reels directories
- If the user wants a **strong/powerful intro audio**, use `bg_music.mp3` and trim the first 20s (it starts strong)
- If the user provides a custom audio file, accept it via Telegram upload

### Step 3: Create 20-Second Reel with Lighting Effects

Use FFmpeg to create a 20-second video from the single image with audio and lighting effects. Key FFmpeg filter chain:

```bash
ffmpeg -y -loop 1 -i padded_image.jpg -i audio.mp3 \
  -vf "
    # Vignette — darkens edges, draws focus to center
    vignette=PI/4:max(0.6-0.2*mod(t,2),0.3),

    # Subtle brightness pulse
    curves=b=0.1/0.1:0.5/0.65:1.0/0.9,

    # Warm tint overlay
    colorbalance=rs=0.05:gs=0.0:bs=-0.05:rh=0.02:gh=0.0:bh=-0.02,

    # Gentle zoom in
    zoompan=z='min(zoom+0.001,1.08)':d=20*25:s=720x1280:fps=25,

    # White flash at start for strong intro
    drawbox=x=0:y=0:w=iw:h=ih:color=white@0.3:t=fill:enable='between(t,0,0.3)'
  " \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k -shortest -pix_fmt yuv420p \
  reel_output.mp4
```

**Effect breakdown:**
| Effect | Purpose |
|--------|---------|
| `vignette` | Darkens edges, cinematic look. `mod(t,2)` creates a subtle breathing pulse |
| `curves` | Adjusts brightness curve for gentle pulsing |
| `colorbalance` | Adds warm tint (more red, less blue) |
| `zoompan` | Slow zoom-in from 1.0x to 1.08x over 20s — adds motion to static image |
| `drawbox` (white flash) | White overlay for 0.3s at start — strong intro flash effect |

### Step 3b: Alternative — More Dramatic Lighting Effects

If the user wants more dynamic effects:

```bash
ffmpeg -y -loop 1 -i padded_image.jpg -i audio.mp3 \
  -vf "
    # Vignette with pulse
    vignette=PI/4:max(0.7-0.3*sin(2*PI*t/2),0.2),

    # Color shift over time — warm to cool sweep
    colorbalance=rs=0.1*sin(2*PI*t/10):bs=-0.08*sin(2*PI*t/10),

    # Brightness flash at start
    drawbox=x=0:y=0:w=iw:h=ih:color=white@0.5:t=fill:enable='between(t,0,0.2)',

    # Light rays / glow sweep
    drawbox=x='iw/2-iw*0.3*abs(sin(2*PI*t/4))':y=0:w='iw*0.6*abs(sin(2*PI*t/4))':h=ih:color=white@0.08:t=fill,

    # Slow zoom
    zoompan=z='min(zoom+0.002,1.12)':d=20*25:s=720x1280:fps=25
  " \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k -shortest -pix_fmt yuv420p \
  reel_output.mp4
```

### Step 4: Deliver

- Show the final reel to user via MEDIA: path
- If approved for publishing: send to Make.com webhook with `content_type=reel`
- Webhook: https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e

### Common FFmpeg Lighting Effects Reference

| Effect | FFmpeg Filter | Parameters to Tweak |
|--------|--------------|---------------------|
| **Vignette (dark corners)** | `vignette` | Angle (PI/4), max intensity (0.3-0.7) |
| **Brightness pulse** | `curves` | Use `mod(t,N)` or `sin(2*PI*t/N)` for oscillation |
| **Color shift** | `colorbalance` | rs/gs/bs (shadows), rh/gh/bh (highlights), -0.1 to 0.1 |
| **White flash intro** | `drawbox` | `enable=between(t,0,0.3)`, color=white@0.3-0.5 |
| **Light sweep** | `drawbox` (animated x/w) | Sinusoidal x-position for moving light bar |
| **Slow zoom** | `zoompan` | z rate (0.001-0.005), max zoom (1.05-1.15) |
| **Film grain** | `noise` | `cif=uf=8:cf=allf=4` for subtle grain |

### Audio Extraction Cheat Sheet

```bash
# Extract audio from a reel (to reuse as "our sound")
ffmpeg -y -i reel_input.mp4 -vn -c:a copy audio_only.mp4
ffmpeg -y -i reel_input.mp4 -vn -c:a libmp3lame -q:a 2 audio_only.mp3

# Trim audio to 20 seconds
ffmpeg -y -i audio.mp3 -t 20 audio_20s.mp3

# Fade in/out audio
ffmpeg -y -i audio.mp3 -af "afade=t=in:d=1,afade=t=out:d=2:st=18" audio_faded.mp3
```

## Reference Files

- `references/authority-reel-worked-example.md` — worked example from June 2026: AI CERTs + ISO standards + AI Global Authority reel. Includes full voiceover script, scene structure, research sources, and authority angles.

## Step 7: Memory

Save any new settings or corrections to memory for future consistency.
