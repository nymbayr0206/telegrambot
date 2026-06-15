# FFmpeg Reel from Static Image

Create a short video reel from a single static image with audio overlay and lighting/motion effects.

## Basic Pattern: 20s Reel from Image + Audio

```bash
ffmpeg -y \
  -loop 1 -i input.jpg \
  -i audio.mp3 \
  -t 20 \
  -vf "
    zoompan=z='min(zoom+0.002,1.12)':d=20*30:s=720x1280:fps=30,
    vignette=PI/4:mode=forward,
    colorbalance=rs=0.1:gs=0.05:bs=-0.05:rh=-0.05:gh=0:bh=0.05,
    eq=brightness='0.02*sin(2*PI*t/4)':saturation='1.0+0.1*sin(2*PI*t/3)'
  " \
  -af "volume=1.5,afade=t=in:st=0:d=1" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  -shortest \
  output_reel.mp4
```

## Filter Breakdown

| Filter | Effect | Parameters |
|--------|--------|------------|
| `zoompan` | Slow Ken Burns zoom-in | `z='min(zoom+0.002,1.12)'` = zoom from 1.0x to 1.12x over duration |
| `vignette` | Spotlight center, dark edges | `PI/4:mode=forward` = soft vignette |
| `colorbalance` | Warm tone shift | `rs=0.1:gs=0.05:bs=-0.05` = red+green boost, blue cut |
| `eq brightness` | Pulsing light effect | `0.02*sin(2*PI*t/4)` = brightness oscillates every 4s |
| `eq saturation` | Pulsing color intensity | `1.0+0.1*sin(2*PI*t/3)` = saturation varies every 3s |
| `volume` | Audio boost | `1.5` = 50% louder |
| `afade` | Audio fade-in | `t=in:st=0:d=1` = 1s fade-in at start |

## Image Requirements

- Input image should be **9:16 portrait** (720×1280 or 1080×1920) for vertical reels
- If image is landscape, add `scale` and `crop` filters before zoompan
- JPEG is fine; PNG also works

## Audio Requirements

- Audio is trimmed to match `-t 20` (or whatever duration)
- If audio is shorter than target duration, remove `-shortest` and loop image for full audio
- Supported formats: mp3, aac, ogg, wav, m4a

## Variations

### No audio, just video with effects
```bash
ffmpeg -y -loop 1 -i input.jpg -t 20 \
  -vf "zoompan=z='min(zoom+0.003,1.15)':d=20*30:s=720x1280:fps=30,vignette=PI/4" \
  -c:v libx264 -preset fast -crf 23 output.mp4
```

### Faster zoom, more dramatic lighting
```bash
# Change zoom rate: 0.005 = faster, 1.20 = more zoom
# Change brightness: 0.05 = more dramatic pulsing
# Change period: /2 = faster pulse
```

### Add AI Global watermark overlay
```bash
# After the video is created, add logo watermark:
ffmpeg -y -i output_reel.mp4 \
  -i /opt/data/social-content/brands/ai-global/assets/logos/logo-ai-global-transparent.png \
  -filter_complex "overlay=W-w-20:20" \
  -c:a copy output_watermarked.mp4
```

## Known Issues

- `colorbalance` and `eq` filters need high `zoompan` frame count to avoid judder
- Very high `crf` (>28) causes compression artifacts on Ken Burns zooms
- For 1080×1920 output: change `s=720x1280` to `s=1080x1920` in zoompan
