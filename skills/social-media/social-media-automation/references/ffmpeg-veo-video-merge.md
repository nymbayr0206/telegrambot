# FFmpeg Veo Video Merge & Caption Workflow

Merge Veo 3.1 Fast multi-scene MP4 clips into one continuous Reel and add Mongolian captions with custom styling.

## Step 1: Verify Compatibility

All clips must share the same codec, resolution, and audio format before merging:

```bash
ffprobe -v error -show_entries stream=codec_name,width,height -of csv=p=0 scene-01.mp4
```

Veo 3.1 Fast typical output: h264, 720×1280, aac audio, ~8s duration.

## Step 2: Lossless Merge (Concat Demuxer)

When all clips are identical format, use `-c copy` (no re-encode, instant):

```bash
echo "file '/path/scene-01.mp4'" > /tmp/concat.txt
echo "file '/path/scene-02.mp4'" >> /tmp/concat.txt
echo "file '/path/scene-03.mp4'" >> /tmp/concat.txt
ffmpeg -f concat -safe 0 -i /tmp/concat.txt -c copy merged.mp4 -y
```

## Step 3: Crossfade Transitions (Re-encode Required)

When you want fade-in/fade-out between scenes, use filter_complex:

```bash
ffmpeg -i scene-01.mp4 -i scene-02.mp4 -i scene-03.mp4 \
  -filter_complex "\
    [0:v]fade=t=in:st=0:d=0.5,fade=t=out:st=7.5:d=0.5[v0]; \
    [1:v]fade=t=in:st=0:d=0.5,fade=t=out:st=7.5:d=0.5[v1]; \
    [2:v]fade=t=in:st=0:d=0.5,fade=t=out:st=7.5:d=0.5[v2]; \
    [v0][0:a][v1][1:a][v2][2:a]concat=n=3:v=1:a=1[outv][outa]" \
  -map "[outv]" -map "[outa]" -c:a aac -b:a 128k -preset fast output.mp4 -y
```

Adjust `st` and `d` values for different scene durations. The `concat` filter requires exactly n video+audio pairs.

## Step 4: Add Word-by-Word Captions with Glow (ASS Subtitle Format)

### Why ASS over SRT

SRT only supports basic positioning. ASS supports:
- Custom fonts (Nunito, any TTF/OTF)
- Border glow effects (`\bord` + `\blur`)
- Per-character coloring (karaoke-style)
- Precise positioning (Alignment, MarginV)

### ASS File Structure

Create an `.ass` file with this header:

```ass
[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Glow,Nunito-Bold,32,&H00FFFFFF,&H000000FF,&HC0D45E,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,2,40,40,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.50,0:00:02.00,Glow,,0,0,0,,{\blur3}Өдөр бүр
Dialogue: 0,0:00:02.00,0:00:03.50,Glow,,0,0,0,,{\blur3}юу постлох вэ?
```

### Key ASS Style Parameters

| Parameter | Value | Effect |
|---|---|---|
| `Fontname` | `Nunito-Bold` or any installed font name | Controls typeface |
| `Fontsize` | `32` | Adjust for readability |
| `PrimaryColour` | `&H00FFFFFF` | White text fill (format: &HAABBGGRR) |
| `OutlineColour` | `&HC0D45E` | Turquoise glow (#5ED4C0 in BGR) |
| `Outline` | `6` | Border/glow width (larger = bigger glow) |
| `Alignment` | `2` | 2=bottom center, 8=top center |
| `BorderStyle` | `1` | 1=outline+shadow, 3=opaque box |

Inline override `{\blur3}` adds the soft blur to the outline for a glow effect.

### Color Conversion (Hex → ASS BGR)

ASS uses `&HAABBGGRR&` format (Alpha, Blue, Green, Red).

| Color | Hex | ASS BGR |
|---|---|---|
| White | #FFFFFF | `&H00FFFFFF` |
| Turquoise | #5ED4C0 | `&HC0D45E` (R=5E, G=D4, B=C0 → BGR=C0D45E) |
| Red | #F20B2E | `&H2E0BF2` |
| Blue | #1768B5 | `&HB56817` |
| Navy | #071B4D | `&H4D1B07` |

### Tips for Word-by-Word Captions

- **2-4 words per line** — keep each subtitle cue short so it feels synced with speech
- **~1.5s per chunk** — Mongol speech averages ~2-3 words per 1.5s at natural pace
- **Offset from fades** — start first caption at 0.5s (after fade-in), end last caption before final fade-out
- **Overlap safety** — cues should not overlap; each ends before the next starts
- **Empty lines between scenes** — use ASS comment lines (`=== SCENE N ===` for readability in the file; they are ignored by the renderer)

## Step 5: Render with Custom Font

Download Nunito (or any Google Font) if not installed system-wide:

```bash
mkdir -p /opt/data/fonts
curl -sL "https://github.com/google/fonts/raw/main/ofl/nunito/static/Nunito-Bold.ttf" -o /opt/data/fonts/Nunito-Bold.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/nunito/static/Nunito-Regular.ttf" -o /opt/data/fonts/Nunito-Regular.ttf
```

Then pass `fontsdir` to the subtitles filter:

```bash
ffmpeg ... -vf "subtitles=captions.ass:fontsdir=/opt/data/fonts" ... output.mp4
```

### Combine Everything (Transitions + ASS Captions)

```bash
ASS="/tmp/captions.ass"
FONTS="/opt/data/fonts"

ffmpeg -i scene-01.mp4 -i scene-02.mp4 -i scene-03.mp4 \
  -filter_complex "\
    [0:v]fade=t=in:st=0:d=0.5,fade=t=out:st=7.5:d=0.5[v0]; \
    [1:v]fade=t=in:st=0:d=0.5,fade=t=out:st=7.5:d=0.5[v1]; \
    [2:v]fade=t=in:st=0:d=0.5,fade=t=out:st=7.5:d=0.5[v2]; \
    [v0][0:a][v1][1:a][v2][2:a]concat=n=3:v=1:a=1[outv][outa]; \
    [outv]subtitles=$ASS:fontsdir=$FONTS[finalv]" \
  -map "[finalv]" -map "[outa]" \
  -c:a aac -b:a 128k -preset fast final-reel.mp4 -y
```

**Important:** The `subtitles` filter cannot be combined with `-vf` when `-filter_complex` is already in use. Both must be inside the filter_complex chain.

## Pitfalls

1. **Non-monotonic DTS warnings** — common with concat demuxer; harmless for playback but may cause issues in editors. Use re-encode merge (`-c:v libx264`) if editing further.
2. **ASS font not found** — if the font name doesn't match what's registered, FFmpeg silently falls back to Arial. Verify with `fc-list | grep -i nunito` or pass `fontsdir` explicitly.
3. **Color format confusion** — ASS uses `&HAABBGGRR&`, NOT `&HAARRGGBB&`. Turquoise (#5ED4C0 → R=5E, G=D4, B=C0) becomes `&HC0D45E` in BGR. A common mistake is passing hex directly.
4. **`-filter_complex` + `-vf` conflict** — when using filter_complex, `-vf` is rejected. Both video filters must be inside the same filter_complex chain.
5. **SRT vs ASS for visual captions** — SRT is suitable for basic subtitles only. For custom fonts, glow effects, word-by-word sync, or positioning, ASS is required.
