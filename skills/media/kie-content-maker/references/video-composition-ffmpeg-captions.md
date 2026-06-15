# FFmpeg Video Composition for Social Ads

## Overview

Compose a vertical (9:16) social video ad from:
- 4+ still images as B-roll
- 1 voiceover audio file (MP3)
- Cyrillic Mongolian captions via drawtext
- (Optional) Background music

## Image Preparation

### Scale to 1080x1920

Use direct scale (not force_original_aspect_ratio) when source is close to 9:16:

```bash
ffmpeg -y -loop 1 -i input.png -c:v libx264 -t 7 -pix_fmt yuv420p \
  -vf "scale=1080:1920" \
  scene.mp4
```

If source aspect ratio differs significantly, use crop:

```bash
ffmpeg -y -loop 1 -i input.png -c:v libx264 -t 7 -pix_fmt yuv420p \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
  scene.mp4
```

## Adding Cyrillic Mongolian Captions

### CRITICAL: Colons Break drawtext

FFmpeg's `drawtext` filter uses `:` as an option separator. Mongolian Cyrillic text commonly contains colons (e.g. `утас: 89097454`, `сарын 2-нд:`) which the filter parser interprets as delimiters, causing `No option name near` errors.

**NEVER use inline `text=` with Cyrillic text. Always use `textfile=` instead.**

### Correct Approach: textfile

Write each caption to a UTF-8 text file:

```python
with open("caption.txt", "w", encoding="utf-8") as f:
    f.write("Бүртгүүлэх утас 89097454")
```

Then reference it in ffmpeg:

```bash
ffmpeg -y -loop 1 -i input.png -c:v libx264 -t 7 -pix_fmt yuv420p \
  -vf "scale=1080:1920,drawtext=textfile=caption.txt:fontfile=/path/to/font.ttf:fontsize=38:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=10:x=(w-text_w)/2:y=h-300" \
  scene.mp4
```

### Time-Based Caption Animation

Use `enable='between(t,START,END)'` for timed caption appearance. Each `enable` must reference text from a separate textfile:

```bash
# Scene with two captions appearing sequentially
-vf "scale=1080:1920,
     drawtext=textfile=caption1.txt:fontfile=${FONT}:fontsize=36:
       fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=10:
       x=(w-text_w)/2:y=h-300:enable='between(t,0,3)',
     drawtext=textfile=caption2.txt:fontfile=${FONT}:fontsize=36:
       fontcolor=yellow:box=1:boxcolor=black@0.5:boxborderw=10:
       x=(w-text_w)/2:y=h-240:enable='between(t,3.5,7)'"
```

### Caption Styling

| Parameter | Value | Effect |
|-----------|-------|--------|
| `fontcolor` | `white` | White text |
| | `yellow` | Yellow/gold accent (emphasis) |
| `box` | `1` | Background box |
| `boxcolor` | `black@0.5` | Semi-transparent black background |
| `boxborderw` | `10` | Padding around text |

### Font Path

The system font DejaVuSerif-Bold supports Cyrillic Mongolian:

```
/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf
```

DejaVuSans-Bold also works:

```
/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
```

## Scene Concatenation

### Method 1: Concat Demuxer (simpler, no crossfade)

Create a file list:

```
file '/path/to/scene1.mp4'
file '/path/to/scene2.mp4'
file '/path/to/scene3.mp4'
file '/path/to/scene4.mp4'
```

Then:

```bash
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c:v libx264 combined.mp4
```

### Method 2: Crossfade with Filter Complex

```bash
ffmpeg -y \
  -i scene1.mp4 -i scene2.mp4 -i scene3.mp4 -i scene4.mp4 \
  -filter_complex "\
    [0:v]fade=t=out:st=6:d=1[v0];\
    [1:v]fade=t=in:st=0:d=1,fade=t=out:st=6:d=1[v1];\
    [2:v]fade=t=in:st=0:d=1,fade=t=out:st=6:d=1[v2];\
    [3:v]fade=t=in:st=0:d=1[v3];\
    [v0][v1][v2][v3]concat=n=4:v=1:a=0[vid]" \
  -map "[vid]" -c:v libx264 -preset medium -crf 22 \
  combined.mp4
```

Where `st=6:d=1` means: start fade at 6s (last second of 7s scene), duration 1s.

## Adding Voiceover Audio

```bash
ffmpeg -y -i video_novoice.mp4 -i voiceover.mp3 \
  -c:v copy -c:a aac -b:a 128k -map 0:v:0 -map 1:a:0 -shortest \
  final.mp4
```

`-shortest` trims to the shorter of video or audio duration.

## Output Format

- Resolution: 1080x1920 (9:16 vertical)
- Codec: H.264 (libx264)
- Audio: AAC 128kbps
- Profile: `yuv420p` for maximum compatibility

## Adding Background Music

For social video ads that need background music, use ffmpeg to generate a
short royalty-free synth track or layer an existing music file:

### Generate a simple synth track

```bash
ffmpeg -y -f lavfi -i "sine=frequency=440:duration=28" \
  -af "volume=0.15" \
  music.mp3
```

- `sine` filter generates a pure test tone — not musical. For actual background
  music, download a royalty-free MP3 or use KIE ElevenLabs/MusicGen.
- Mix with voiceover using the `amix` filter (voice at higher volume than music):

```bash
ffmpeg -y -i voiceover.mp3 -i music.mp3 \
  -filter_complex "[0:a]volume=1.0[v];[1:a]volume=0.15[m];[v][m]amix=inputs=2:duration=first" \
  -c:a aac -b:a 128k \
  mixed_audio.mp3
```

- Apply fade-out to music at the end:

```bash
[1:a]volume=0.15,afade=t=out:st=24:d=4[m]
```

### Mix with video in one command

```bash
ffmpeg -y -i combined_video.mp4 -i voiceover.mp3 -i music.mp3 \
  -filter_complex "[1:a]volume=1.0[v];[2:a]volume=0.15,afade=t=out:st=24:d=4[m];[v][m]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 128k \
  final.mp4
```

## Full Composition Script (Python)

See the production script at `/opt/data/scripts/compose_video.py` for a complete working example that handles:
1. Text file creation for each caption
2. Per-scene ffmpeg generation with drawtext
3. Scene concatenation
4. Voiceover overlay

## Observed Production Values

- Voiceover duration: ~28s for ~80-word Mongolian script
- Per-scene duration: 7s (4 scenes = 28s total)
- Total file size: ~1.6 MB for 28s 1080x1920 H.264
- Generation time per scene: ~5-10s (ffmpeg)
