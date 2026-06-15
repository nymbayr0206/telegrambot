# Brand Video Watermark Overlay

## When to Use

When compositing a branded social video (Reel/Short) and the brand requires its watermark logo on the output. Invoke the brand's watermark script or run the ffmpeg command manually.

## Universal FFmpeg Command

```bash
ffmpeg -y -i input_video.mp4 -i /path/to/logo/watermark.png \
  -filter_complex "[1:v]scale='iw/10':-1[logo];[0:v][logo]overlay=W-w-20:20" \
  -c:a copy output_watermarked.mp4
```

Where:
- `scale='iw/10':-1` — logo width = 1/10th of video width, height auto
- `overlay=W-w-20:20` — top-right corner with 20px padding
- `-c:a copy` — copy audio stream (no re-encode)

## Brand-Specific Paths

### AI Global
- Logo: `assets/logos/watermark-ai-global.png` (1024x1024, black+gold)
- Script: `scripts/add_ai_global_watermark.py`
- Usage: `python3 scripts/add_ai_global_watermark.py input.mp4`

The script handles:
- Logo scaling to 1/10th video width
- Top-right placement with 20px padding
- Audio passthrough
- Auto-naming output as `input_watermarked.mp4`

### Postly
- Path: `social-content/brands/postly/assets/logos/` (turquoise logo)
- Same ffmpeg command with brand logo path

## Verification

After adding watermark, check:
1. Logo is visible at top-right
2. Logo is not distorted (width/height ratio preserved via `scale='iw/10':-1`)
3. Audio is intact
4. Video dimensions unchanged
