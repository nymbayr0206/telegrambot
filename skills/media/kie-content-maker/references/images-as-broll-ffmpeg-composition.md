# Images-as-B-Roll FFmpeg Composition

Pattern for creating short social video ads (Reels/Shorts) using KIE-generated still images as B-roll, with voiceover, captions, and background music composed via ffmpeg.

## Workflow

1. Generate 4 text-free photorealistic images via KIE (Nano Banana 2 preferred — GPT Image 2 may return 500 Internal Error)
2. Generate Mongolian female voiceover via edge-tts: `mn-MN-YesuiNeural`
3. Generate/obtain background music (synthetic or downloaded)
4. Compose video with ffmpeg: image slideshow + audio mix + captions

## ffmpeg Composition Pattern

### Step 1: Base video (images + voiceover + music)

```bash
ffmpeg -y \
  -loop 1 -t 10 -i "scene_1.jpg" \
  -loop 1 -t 10 -i "scene_2.jpg" \
  -loop 1 -t 10 -i "scene_3.jpg" \
  -loop 1 -t 10 -i "scene_4.jpg" \
  -i "voiceover_full.mp3" \
  -i "bg_music.mp3" \
  -filter_complex "
    [0:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:black[v0];
    [1:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:black[v1];
    [2:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:black[v2];
    [3:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:black[v3];
    [v0][v1][v2][v3]concat=n=4:v=1:a=0[final_v];
    [4:a]volume=1.0[voice];
    [5:a]volume=0.15[bgm];
    [voice][bgm]amix=inputs=2:duration=first[final_a]
  " \
  -map "[final_v]" -map "[final_a]" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k -pix_fmt yuv420p -t 40 \
  "base_video.mp4"
```

Key parameters:
- `-loop 1 -t N`: each image repeats for N seconds (total should match voiceover)
- `scale=720:1280...pad=720:1280`: fit any image into 9:16 720p frame
- `bgm volume=0.15`: background music at 15% to not overpower voice
- `duration=first`: end music when voiceover ends
- `-t 40`: clip to exactly 40 seconds

### Step 2: Add captions with drawtext

**CRITICAL: Use `textfile=` not `text=` for Mongolian text containing `:`** — the colon character breaks ffmpeg's filter parser with `No option name near` errors. Phone numbers like `Бүртгүүлэх: 89097454` always trigger this.

**Working approach — write caption text files then reference them:**

```python
import subprocess, os

text_dir = "/tmp/caption_texts"
os.makedirs(text_dir, exist_ok=True)

captions = [
    ("c01.txt", "Section 1 headline", 32, "white", 0.15, 0, 10),
    ("c02.txt", "Section 1 sub", 28, "white", 0.22, 0, 10),
    ("c03.txt", "Section 1 highlight", 28, "#FFD700", 0.32, 0, 10),
    # ... repeat for sections 2-4
]

for fn, content, *_ in captions:
    with open(f"{text_dir}/{fn}", "w") as f:
        f.write(content)

filter_parts = []
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
H = 1280

for fn, content, size, color, y_ratio, ts, te in captions:
    shadow = "shadowcolor=black:shadowx=3:shadowy=3" if color == "#FFD700" else "shadowcolor=yellow:shadowx=3:shadowy=3"
    filter_parts.append(
        f"drawtext=textfile={text_dir}/{fn}:fontfile={font}:fontsize={size}:fontcolor={color}:{shadow}:x=(w-text_w)/2:y={int(H*y_ratio)}:enable='between(t,{ts},{te})'"
    )

vf_str = ",".join(filter_parts)

subprocess.run(["ffmpeg", "-y", "-i", "base_video.mp4",
    "-vf", vf_str,
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-c:a", "copy", "final_video.mp4"])
```

## Mongolian TTS via edge-tts

The Hermes `text_to_speech` edge provider fails for Mongolian Cyrillic. Install and use the `edge-tts` Python package:

```python
import asyncio, edge_tts

text = "Mongolian text here..."
voice = "mn-MN-YesuiNeural"  # female; also available: mn-MN-IreeduiNeural (male)
output = "voiceover_full.mp3"

async def main():
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output)

asyncio.run(main())
```

## Synthetic Background Music (fallback)

When no royalty-free source is available, generate a simple playful track via ffmpeg:

```bash
ffmpeg -f lavfi -i "sine=frequency=523.25:duration=0.5,volume=0.08" \
  -f lavfi -i "sine=frequency=587.33:duration=0.5,volume=0.08" \
  -f lavfi -i "sine=frequency=659.25:duration=0.5,volume=0.08" \
  -f lavfi -i "sine=frequency=698.46:duration=0.5,volume=0.08" \
  -filter_complex "[0][1][2][3]concat=n=4:v=0:a=1,aloop=loop=-1:size=88200,afade=t=in:st=0:d=2,afade=t=out:st=38:d=2" \
  -t 40 "bg_music.mp3" -y
```

## Caption Text File Structure

| Section | Time | Lines | Style |
|---------|------|-------|-------|
| Hook | 0-10s | 3 lines (headline + sub + highlight) | White → gold CTA |
| Problem | 10-20s | 3 lines | Same pattern |
| Solution | 20-30s | 3 lines | Same pattern |
| CTA | 30-40s | 4-5 lines (workshop + phone + location) | Gold headline |

For this user's Mongolian text content, use **Cyrillic Mongolian** (not Latin transliteration). The user explicitly corrected: "Кириллээр caption tai bh". DejaVu Sans Bold font supports Cyrillic rendering correctly in ffmpeg drawtext.

**CRITICAL:** Use `textfile=` parameter (not inline `text=`) when caption text contains `:` — phone numbers like `Бүртгүүлэх: 89097454` trigger ffmpeg filter parser colons-as-option-separator bug. Write each caption line to a separate text file, then reference via `drawtext=textfile=/path/to/caption.txt:fontfile=...:fontsize=...`.
