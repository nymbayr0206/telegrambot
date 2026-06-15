# Reel Production — Worked Example (June 2026)

From the AI+ Agent course sell session — a 42-second B-roll style reel promoting Vibe Coding course enrollment.

## Overview

| Component | Method | Details |
|-----------|--------|---------|
| Scene images | KIE gpt-image-2-image-to-image | 8 scenes, 9:16, reeltemp1 background |
| Voiceover | KIE ElevenLabs V3 | Lily voice, Mongolian, 42.4s |
| Captions | FFmpeg subtitles filter | Manrope Bold, white + yellow outline |
| Final assembly | FFmpeg | Merge images + audio + subtitles |

## Step 1: Generate Scene Images

Upload reeltemp1 (and instructor photo if needed) to tmpfiles.org:

```bash
curl -s -F "file=@assets/reeltemp1.jpg" https://tmpfiles.org/api/v1/upload
# Returns: https://tmpfiles.org/dl/<hash>/reeltemp1.jpg

curl -s -F "file=@assets/people/trainer-eland.jpg" https://tmpfiles.org/api/v1/upload
```

Submit each scene to KIE with aspect_ratio="9:16" (no resolution parameter — it errors):

```bash
curl -s -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -d '{
  "model": "gpt-image-2-image-to-image",
  "input": {
    "prompt": "Create a 9:16 vertical reel scene for AI Global. STRICT RULE: The reeltemp1 background image MUST be preserved EXACTLY as-is. Do NOT modify, alter, or redesign any element of the template. ONLY add visual elements on top. Do NOT add any text or letters.",
    "input_urls": ["https://tmpfiles.org/dl/<hash>/reeltemp1.jpg"],
    "aspect_ratio": "9:16"
  }
}'
```

**For scenes with instructor photo:** Add second URL + instruct to place face:
```bash
"input_urls": ["<reeltemp1_url>", "<photo_url>"]
```
Prompt addition: "Take the person's face from the second input image and place it in the portrait area."

**Key:** KIE `gpt-image-2-image-to-image` with aspect_ratio="9:16" (no resolution field).

## Step 2: Generate Voiceover

**⚠️ Use V3 Dialogue model, NOT the old TTS model.**

```bash
curl -s -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -d '{
  "model": "elevenlabs/text-to-dialogue-v3",
  "input": {
    "dialogue": [
      {"text": "Хиймэл оюун бүх мэргэжлүүдийг өөрчилж байна.", "voice": "Lily"},
      {"text": "Хэрэв та ямар мэргэжил эзэмшихээ мэдэхгүй байгаа бол сайн анхаараарай.", "voice": "Lily"},
      {"text": "Олон улсын сертификаттай, англи монгол багштай Vibe Coding-ийн сургалт эхлэх гэж байна.", "voice": "Lily"},
      {"text": "Энэ боломжийг бүү алдаарай.", "voice": "Lily"},
      {"text": "16-25 насны мэргэжлээ шинэчлэх, хиймэл оюуны эрин үед өндөр эрэлттэй мэргэжил эзэмшихийг хүсвэл манай сургалтыг сонирхоорой.", "voice": "Lily"},
      {"text": "Зөвхөн 20 хүнийг бүртгэнэ.", "voice": "Lily"},
      {"text": "Бүртгүүлэх болон мэдээлэл авахыг хүсвэл коммент бичээрэй.", "voice": "Lily"},
      {"text": "AI Global 21-р зууны супер хүнийг бэлдэнэ.", "voice": "Lily"}
    ]
  }
}'
```

Returns a single concatenated MP3. Note: V3 delivers faster than V2 (~36s vs ~42s for the same script). Always measure actual duration with ffprobe to calibrate scene timings.

## Step 3: Create TikTok-Style Word-by-Word Caption SRT

**The user wants TikTok-style animated captions** — each small word chunk appears, replaces the previous one, synchronized with voiceover. NOT static sentences.

Generate SRT where each entry is 2-3 words with timing proportional to the voiceover duration:

```python
scene_texts = [
    "Хиймэл оюун бүх мэргэжлүүдийг өөрчилж байна.",
    "Хэрэв та ямар мэргэжил эзэмшихээ мэдэхгүй байгаа бол сайн анхаараарай.",
    "Олон улсын сертификаттай, англи монгол багштай Vibe Coding-ийн сургалт эхлэх гэж байна.",
    "Энэ боломжийг бүү алдаарай.",
    "16-25 насны мэргэжлээ шинэчлэх, хиймэл оюуны эрин үед өндөр эрэлттэй мэргэжил эзэмшихийг хүсвэл манай сургалтыг сонирхоорой.",
    "Зөвхөн 20 хүнийг бүртгэнэ.",
    "Бүртгүүлэх болон мэдээлэл авахыг хүсвэл коммент бичээрэй.",
    "AI Global — 21-р зууны супер хүнийг бэлдэнэ."
]

# Scene durations summing to total audio duration (e.g. 36.3s)
scene_durs = [4.0, 4.5, 6.0, 4.0, 5.5, 4.5, 4.5, 3.3]

time_offset = 0.0
for text, dur in zip(scene_texts, scene_durs):
    words = text.split()
    chunk_size = 2  # show 2 words at a time
    word_dur = dur / len(words)
    for w_idx in range(0, len(words), chunk_size):
        chunk_end = min(w_idx + chunk_size, len(words))
        caption = " ".join(words[w_idx:chunk_end])
        start = time_offset + (w_idx * word_dur)
        end = start + word_dur * chunk_size
        # Write SRT: index, time range, caption
    time_offset += dur
```

Output SRT entries look like:
```
1
00:00:00,000 --> 00:00:01,333
Хиймэл оюун

2
00:00:01,333 --> 00:00:02,666
бүх мэргэжлүүдийг

3
00:00:02,666 --> 00:00:03,999
өөрчилж байна.

4
00:00:04,000 --> 00:00:04,900
Хэрэв та
...
```

**Caption styling values (June 2026):**
| Style | Value |
|-------|-------|
| FontName | Manrope-Bold |
| FontSize | 10 (small — user said "2 дахин жижиг" from 22pt) |
| PrimaryColour | &H00FFFFFF (white) |
| OutlineColour | &H00FFFF00 (yellow glow) |
| Outline | 2.5 |
| BorderStyle | 1 (outline + shadow) |
| Alignment | 2 (bottom-center) |
| MarginV | 40 |

## Step 4: Assemble with FFmpeg

### 4a: Create slideshow video from scene images

Create a concat file listing each image + duration:
```
file scene1.png
duration 5
file scene2.png
duration 5
...
```

Generate raw video:
```bash
ffmpeg -y -f concat -safe 0 -i concat.txt \
  -c:v libx264 -pix_fmt yuv420p -r 30 \
  -vf "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=black" \
  raw_video.mp4
```

### 4b: Add audio + burn captions with styling

```bash
ffmpeg -y -i raw_video.mp4 -i voiceover.mp3 \
  -c:v libx264 -pix_fmt yuv420p -r 30 \
  -vf "subtitles=captions.srt:fontsdir=/path/to/manrope:force_style='FontName=Manrope-Bold,FontSize=10,PrimaryColour=&H00FFFFFF,OutlineColour=&H00FFFF00,Outline=2.5,BorderStyle=1,Alignment=2,MarginV=40'" \
  -c:a aac -b:a 128k -shortest \
  final_reel.mp4
```

**Caption styling reference:**
| Style | Value | Description |
|-------|-------|-------------|
| FontName | Manrope-Bold | User's brand font |
| FontSize | 10-11 | Small — user corrected to "2 дахин жижиг" from 22pt |
| PrimaryColour | &H00FFFFFF | White text |
| OutlineColour | &H00FFFF00 | Yellow outline/glow |
| Outline | 3 | Outline thickness |
| BorderStyle | 1 | Outline + shadow |
| Alignment | 2 | Bottom-center |
| MarginV | 60 | Vertical margin from bottom |

## Critical Reel Rules

1. ❌ **NEVER use FFmpeg for image generation** — KIE generates all visuals
2. ✅ **KIE `gpt-image-2-image-to-image`** with aspect_ratio="9:16" for all scene images
3. ✅ **KIE ElevenLabs V3 — Lily voice** for voiceover
4. ✅ **FFmpeg** is ONLY for: merging scene frames into video, adding audio track, overlaying captions
5. 📐 **reeltemp1 is IMMUTABLE** — same preservation rules as temp1
6. 💬 **Captions**: Cyrillic Mongolian, Manrope Bold, white + yellow outline
7. 🚫 **No text in the scene images** — all text is overlaid via FFmpeg subtitles

## Make.com Delivery

For reel posts, send to webhook with `content_type=reel`:
```bash
curl -s -X POST "https://hook.eu1.make.com/<webhook_id>" \
  -F "video=@final_reel.mp4" \
  -F "caption=<caption text>" \
  -F "content_type=reel" \
  -F "brand=AI Global"
```
