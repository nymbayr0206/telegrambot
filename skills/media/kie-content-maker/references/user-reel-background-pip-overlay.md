# User-Provided Reel Background with Picture-in-Picture Overlay

## Pattern

When the user sends their own JPEG/PNG image and says "use this as the reel video background" (e.g. `reeltemp1`):

1. **Save** the user's image to `assets/reeltemp1.jpg` (or similar name in the brand's assets directory)
2. **Check dimensions** — it's typically already 720×1280 (9:16), which is the correct aspect ratio for social reels
3. **Use it as a full-screen background** — scale to 720×1280 in ffmpeg
4. **Overlay scene images** as picture-in-picture (PiP) — smaller, centered, with optional thin white border
5. **Add captions** on top of everything via ffmpeg `drawtext` with `textfile=` approach (to avoid `:` parsing issues with phone numbers)
6. **Mix audio**: voiceover (ElevenLabs Rachel or edge-tts Mongolian) + background music (volume ~0.12)

## FFmpeg Composition Pattern

```python
# Key parameters
W, H = 720, 1280
ts = 14.5  # seconds per scene (4 scenes = ~58s total)
pip_w = 300  # overlay image width
pip_x = int((W - pip_w) / 2)  # center
pip_y = int(H * 0.35)  # ~35% from top

# ffmpeg filter chain:
# [background image scaled to 720x1280]
# [scene image scaled to pip_w, with thin white border]
# overlay at (pip_x, pip_y)
# concat 4 scenes
# mix voiceover + bgm audio
```

## Captions Position

When the background image has its own visual elements (cards, text spaces, layout zones), place captions in the **upper area** (y=15-35% of height) or in clean space. Avoid overlapping the PiP scene image area (center of frame).

## When to Use This Pattern

- User explicitly sends a reel template image
- User says "this is the background" or "ashiglan" (use this)
- User does NOT want KIE to re-generate the background (they've already designed it)
- The PiP scene images come from a separate KIE generation (Nano Banana 2 or GPT Image 2)
