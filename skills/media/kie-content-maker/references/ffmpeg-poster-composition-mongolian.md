# FFmpeg Poster Composition (Mongolian)

> ⛔ **DEPRECATED for poster generation.** The user explicitly banned FFmpeg for posters. Use KIE AI (GPT Image 2 text-to-image) instead. This reference is preserved only for historical reference and for verifying the drawtext-with-textfile technique, which is still valid for video caption overlays.
>
> See SKILL.md → "Hard Rules" section.
>
> For the correct approach, use `gpt-image-2-text-to-image` with detailed style/layout prompts. If the user provides a background template, describe its visual characteristics (colors, layout zones, card elements) in the prompt rather than compositing locally.

---

## When to Use

Create 1:1 square branded posters from a background image + text overlays. Use when:
- The user has a ready background template (JPEG/PNG)
- KIE image-to-image API is unavailable or unreliable from this server
- You need deterministic Cyrillic Mongolian text (no AI misspellings)
- Pillow is not installed and can't be installed (no root, no pip)
- You want quick iteration: change text, re-run in seconds

## Technique: FFmpeg drawtext with textfile

FFmpeg's `drawtext` filter supports a `textfile=` parameter that reads the caption
from an external UTF-8 file. This avoids the `:` colon parsing bug where Mongolian
text containing colons (e.g. phone numbers like `Бүртгүүлэх: 89097454`) is
interpreted as an option separator.

### DO NOT use inline `text=`:
```bash
# BROKEN: colon in text breaks filter parser
-vf "drawtext=text='Бүртгүүлэх: 89097454':fontfile=..."
# Error: "No option name near ' 89097454:fontfile=...'"
```

### Instead, use `textfile=`:
```bash
# Write text to file first
echo "Бүртгүүлэх утас 89097454" > /tmp/caption.txt

# Reference the file in drawtext
-vf "drawtext=textfile=/tmp/caption.txt:fontfile=...:fontsize=38:fontcolor=white:..."
```

## Poster Build Pattern

### 1. Save Background Template

The user's background template exists at:
```
/opt/data/social-content/brands/ai-global/assets/backgrounds/
```

### 2. Create Caption Files

Write each text line to a separate UTF-8 file using Python (not shell echo):

```python
with open("/tmp/p1_title.txt", "w", encoding="utf-8") as f:
    f.write("ЦАЛИНГИЙН ХАРЬЦУУЛАЛТ")
```

### 3. Compose with drawtext

Build a single ffmpeg command with multiple `drawtext` filters for different
zones of the poster. Each drawtext can have independent position, font size,
color, and box styling.

```bash
ffmpeg -y -i "$BG" -frames:v 1 \
  -vf "drawtext=textfile=/tmp/title.txt:fontfile=$FONT:fontsize=42:fontcolor=yellow:box=1:boxcolor=black@0.7:boxborderw=15:x=(w-text_w)/2:y=60,"`
    `"drawtext=textfile=/tmp/subtitle.txt:fontfile=$FONT:fontsize=28:fontcolor=white:x=(w-text_w)/2:y=140,"`
    `"drawtext=textfile=/tmp/item1.txt:fontfile=$FONT:fontsize=30:fontcolor=gold:box=1:boxcolor=black@0.5:boxborderw=10:x=100:y=350" \
  "$OUTPUT.png"
```

### 4. Key Parameters

| Parameter | Value | Effect |
|-----------|-------|--------|
| `fontfile` | `/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf` | Cyrillic-capable font |
| `fontcolor` | `white`, `yellow`, `gold`, `lime`, `aqua`, `hotpink` | Named colors work best |
| `box` | `1` | Semi-transparent background behind text |
| `boxcolor` | `black@0.5` | 50% opaque black background |
| `boxborderw` | `8-15` | Padding around text inside box |
| `x=(w-text_w)/2` | Center horizontally | Auto-calculated |
| `y=60`, `y=140` | Vertical position from top | Use pixel values |
| `y=h-100` | Near bottom | `h` = frame height |
| `-frames:v 1` | Single frame output (PNG) | Required for still images |

### 5. Font Availability

Available Cyrillic-capable fonts on this server:
- `/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf` — ✅ works best
- `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf` — ✅ works well
- `/usr/share/fonts/truetype/freefont/FreeSansBold.ttf` — ✅ available
- `/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf` — ✅ available

No Mongolian-specific fonts (e.g. Manrope) are installed. DejaVu Serif Bold
is the most visually appealing for poster titles.

### 6. Output Size

For 1:1 square posters from a 1254x1254 source, the output is the same
resolution as the background image (no scaling applied if `-vf` doesn't
contain a `scale=` filter).

## Sending Posters to Make.com Webhook

Make.com webhook (configured for N posters) expects multipart/form-data with
numbered image fields. **Send all posters in a single request** using
`image1`, `image2`, ..., `imageN` fields:

```bash
curl -s -X POST "https://hook.eu1.make.com/..." \
  -F "image1=@/path/to/poster1.png;type=image/png" \
  -F "image2=@/path/to/poster2.png;type=image/png" \
  -F "image3=@/path/to/poster3.png;type=image/png" \
  -F "image4=@/path/to/poster4.png;type=image/png" \
  -F "caption1=Poster 1 caption text" \
  -F "caption2=Poster 2 caption text" \
  -F "caption3=Poster 3 caption text" \
  -F "caption4=Poster 4 caption text" \
  -F "total_posters=4" \
  -F "source=hermes_agent" \
  -F "brand=AI Global"
```

- **Send ALL posters in ONE request** with `image1`...`imageN` fields — not individually
- Sending individual POSTs (each with `image=`) only delivers 1 poster to Make.com
  because the webhook expects numbered fields
- The webhook responds with "Accepted" text on success
- Base64-encoded images in JSON payload fail with "request entity too large"
  (Make.com payload limit exceeded)
- Confirm arrival by checking the Facebook/Make.com output

## Multiple drawtext Filters in Single Command

When adding multiple text lines to a poster, chain drawtext filters with commas:

```bash
-vf "drawtext=...:y=60,"`
    `"drawtext=...:y=140,"`
    `"drawtext=...:y=350"
```

Each filter after the first starts with a comma+double-quote.
The shell continuation (`\` followed by backtick-shell-inside-quote) or
proper escaping must preserve the comma between filter descriptors.

## Example: Salary Comparison Poster

Layout (top to bottom on 1254x1254):
1. Title: "ЦАЛИНГИЙН ХАРЬЦУУЛАЛТ" (yellow, y=60, centered)
2. Subtitle: "AI Vibe Coder vs Традиц Программист" (white, y=140, centered)
3. Item 1: "Традиц Программист - 3-5 сая ₮" (gold, y=350, left)
4. Item 2: "AI Vibe Coder - 8-12 сая ₮" (lime, y=450, left)
5. Item 3: "AI Engineer - 15-20 сая ₮" (aqua, y=550, left)
6. Item 4: "AI Architect - 25+ сая ₮" (hotpink, y=650, left)
7. CTA: "Бүртгүүлэх: 89097454" (white, y=h-100, centered)

All text items use `box=1:boxcolor=black@0.5` for readability over the dark tech background.
