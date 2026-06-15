---
name: kie-image-to-image
description: Generate ALL brand posters via KIE GPT Image 2 Image To Image — universal workflow for AI Global, Postly, AgenticForce, and any other brand
---

# KIE GPT Image 2 — Image To Image Workflow (Universal)

Use this skill when the user asks to create or modify posters, carousels, or reels for ANY brand.
This is the ONLY approved method for poster generation — never use Pillow/FFmpeg/Python drawing.

## Template Files

| Name | Use | Aspect | Path |
|------|-----|--------|------|
| `temp1` | Poster backgrounds | 1:1 square | `backgrounds/temp1.jpg` |
| `reeltemp1` | Reel backgrounds | 9:16 vertical | `assets/reeltemp1.jpg` |

**Rule:** When user says "temp1" or "reeltemp1" or just "template", ALWAYS use these files.
Never substitute with a generated image — the user will notice the difference.

### temp1 Knowledge Base

A canonical structured description of the temp1 template — its visual design, layout, colors, dimensions, rules, and full workflow — is saved at `/opt/data/knowledge_bases/ai-global-temp1/`. The actual image and a comprehensive README.md are there.

**When to load it:**
- You need to understand temp1's visual appearance (colors, layout, elements) but your model has no vision support
- The user asks "transcribe temp1" or "what does temp1 look like"
- You need to verify exact dimensions (1254×1254), brand colors (black/gold/white), or element positions without re-analyzing the image

A condensed summary is also in `references/temp1-knowledge-base-reference.md`.

## 🔴 CRITICAL: temp1 Is IMMUTABLE

**temp1 template MUST NEVER be modified or altered when used for generation.** This is a hard rule, not a suggestion.

- temp1 passes through **exactly as-is** — no changes to its background, layout, design elements, colors, logo position, or any visual aspect
- The AI is only allowed to **add text on top** and optionally **fill a pre-existing portrait frame** with a provided photo
- **Never** let the AI "redesign" or "reinterpret" temp1 in any way
- Prompt must explicitly say: "Use the first image (temp1) as the background EXACTLY as-is — do NOT modify or alter the template design at all, keep every element unchanged"
- When the poster looks wrong (e.g., temp1 got modified), **re-generate with a stronger preservation instruction**, don't accept a modified version

### 🔴 Stronger Preservation: Name Each Element

When a simple "keep unchanged" instruction fails and the AI still modifies temp1, **name every specific element that must NOT change**. The AI needs explicit prohibitions per element:

```
CRITICAL — these template elements MUST remain EXACTLY as-is:
- Do NOT change: the logo at top-right
- Do NOT change: the phone number XXXXXX at bottom
- Do NOT change: the website address at bottom
- Do NOT change: the dark/light background
- Do NOT change: any gold/color decorative elements
- Do NOT move, resize, or remove any existing element
- ONLY add new text and place the face photo — nothing else
```

Generic instructions like "keep unchanged" are sometimes ignored by the model. Explicit element-by-element prohibition works more reliably.

### 🔴 temp1 Can Be Replaced By User

The user may send a new temp1 image at any time (when the current one is wrong/outdated). When they do:
1. **Overwrite** `/opt/data/social-content/brands/ai-global/assets/backgrounds/temp1.jpg` with the new file immediately
2. **Always re-upload** to tmpfiles.org before each generation — previous upload URLs become stale when the file changes
3. Update the skill's linked `carousel-prompt-instructions.md` if the new template has a different style (dark vs light, different layout, etc.)

## Model

`gpt-image-2-image-to-image` (NOT `gpt-image/1.5-image-to-image` — that one fails with Internal Error)

## Full Workflow

### Step 1: Upload template to public URL

```bash
result=$(curl -s -F "file=@/opt/data/social-content/brands/ai-global/assets/backgrounds/temp1.jpg" \
  https://tmpfiles.org/api/v1/upload)
```

**⚠️ Pitfall:** The URL format is `https://tmpfiles.org/dl/<hash>/<filename>`. Do NOT strip the hash.
Correct extraction:
```python
import json
data = json.loads(result)
url_path = data['data']['url']  # e.g. "https://tmpfiles.org/wXyZabcDEFg/file.jpg"
hash_part = url_path.rstrip('/').split('/')[-2]  # "wXyZabcDEFg"
filename = url_path.split('/')[-1]
public_url = f"https://tmpfiles.org/dl/{hash_part}/{filename}"
```

### Step 2: Submit image-to-image task

**Always use `terminal()` with curl** — KIE_API_KEY env var is available in shell but NOT in `execute_code` Python.

```bash
curl -s -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -d '{
  "model": "gpt-image-2-image-to-image",
  "input": {
    "prompt": "...",
    "input_urls": ["...temp1-url...", "...photo-url..."],
    "aspect_ratio": "1:1",
    "resolution": "1K"
  }
}'
```

Returns: `{"code":200,"msg":"success","data":{"taskId":"<tid>"}}`

**Multi-image input (temp1 + person photo):** When the user provides a real instructor/student photo (e.g., M. Eland or Munkh-Uchral):
1. Upload BOTH images to tmpfiles.org (temp1 + person photo)
2. Submit with both URLs in `input_urls`: `"input_urls": [temp1_url, person_photo_url]`
3. Prompt must say: "Use the first image (temp1) as background EXACTLY as-is. Take the person's face from the second image and place it in the circular portrait frame that already exists on the template. Keep everything else unchanged."
4. ⚠️ If AI generates a generic person instead, regenerate with stronger "use input_urls[1] exactly" instruction
5. ⚠️ When the AI keeps modifying temp1 despite "keep unchanged", list each specific element name (logo, phone, background, decorations) in the prompt (see Stronger Preservation section above)

### Step 3: Poll for completion

Check `GET /api/v1/jobs/recordInfo?taskId={tid}`.
- State `"success"` → read `resultJson.resultUrls[0]` for the generated image URL
- State `"fail"` or `"failed"` → read `failMsg` for error

### Step 4: Download result

**Always use curl**, not urllib (urllib gets 403 Forbidden from tempfile.aiquickdraw.com):
```bash
curl -s "<url>" -o "<output.png>"
```

### Step 5: Send to Make.com webhook

Single poster:
```bash
curl -s -X POST "https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e" \
  -F "image=@poster.png;type=image/png" \
  -F "caption=..." \
  -F "poster_number=N" \
  -F "total_posters=4" \
  -F "source=kie_gpt_image_2_img2img" \
  -F "brand=AI Global"
```

Multiple (carousel = 4):
```bash
curl -s -X POST "https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e" \
  -F "image1=@poster1.png;type=image/png" \
  -F "image2=@poster2.png;type=image/png" \
  -F "image3=@poster3.png;type=image/png" \
  -F "image4=@poster4.png;type=image/png" \
  -F "caption1=..." \
  -F "caption2=..." \
  -F "caption3=..." \
  -F "caption4=..." \
  -F "total_posters=4" \
  -F "source=kie_gpt_image_2_img2img" \
  -F "brand=AI Global" \
  -F "content_type=carousel"
```

**⚠️ Required: `content_type` field.** Make.com webhook expects `content_type=carousel` for carousel posts, `content_type=reel` for reels. Always include this field — without it Make may accept the request (HTTP 200) but not process it.

## Text Language: CRITICAL — Cyrillic Mongolian Only (ALL Brands)

**All text on ALL brand posters MUST be in proper Cyrillic Mongolian.** Never use English/Latin letters to write Mongolian words. This is a hard, universal rule that applies to AI Global, Postly, AgenticForce, and every other brand.

✅ Correct: `ЦАЛИНГИЙН СУДАЛГАА`, `ТӨГСӨГЧДИЙН ДУНДАЖ ЦАЛИН`, `БҮРЭН АВТОМАТ`
❌ Wrong: `Tsalingiin sudalgaa`, `Tugsugchdiin dundaj tsalin`, `Buren avtomat`

The prompt must explicitly say: "Text in CYRILLIC MONGOLIAN only — do NOT use English/Latin letters for Mongolian words." GPT Image 2 sometimes generates Latinized Mongolian when prompted for "Mongolian" — the explicit prohibition is required.

### ⚠️ Critical: English Brand Names Get Cyrillic-ized Too

Problem: When the prompt says "Cyrillic Mongolian only," GPT Image 2 converts English brand names like "AI" and "IO" into Cyrillic — writing АИ instead of AI and ИО instead of IO Institute.

Fix — Two-step rule in every prompt:
1. First say: "Text in CYRILLIC MONGOLIAN only for Mongolian words"
2. Then immediately add: "EXCEPTION — English brand names like AI and IO Institute must stay in LATIN letters (AI, IO Institute). Do NOT write them in Cyrillic as АИ or ИО."

Example prompt fragment:
```
IMPORTANT TEXT RULE: English brand names like "AI" and "IO Institute" must stay in LATIN letters (AI, IO Institute). Do NOT write them in Cyrillic. Only Mongolian words should be in Cyrillic.

CRITICAL: AI must be written as AI in English/Latin, NOT as АИ or ай. IO Institute must stay as IO Institute in English, NOT as ИО.
```

Affected terms to always protect: AI, Agent, IO Institute, LLC, URL, API, any English brand/product name. When in doubt, explicitly list each English term that must remain in Latin.

## Reel Workflow (B-Roll + Voiceover + Merge)

Use this workflow when the user asks to create a reel, short video, or B-roll content.

### Templates

| Name | Use | Aspect | Path |
|------|-----|--------|------|
| `reeltemp1` | Reel scene backgrounds | 9:16 vertical | `assets/reeltemp1.jpg` |

**Rule:** reeltemp1 is the user's approved reel template. Never substitute with a generated background.

### Step-by-Step

1. **Generate B-roll scene images** — Submit to KIE `gpt-image-2-image-to-image` with reeltemp1 as input_url, aspect_ratio `"9:16"`. Each scene gets its own image with different text/prompts. Same preservation rules as temp1 apply — do NOT modify reeltemp1 elements.

2. **Generate voiceover audio** — Use KIE ElevenLabs V3 model (`elevenlabs/text-to-speech-multilingual-v2`) with voice "Lily", language_code "mn". Text in Cyrillic Mongolian.

3. **Merge with FFmpeg** — FFmpeg is ONLY allowed for:
   - Merging generated scene images into a slideshow video
   - Adding voiceover audio track to the video
   - Adding caption/subtitle overlay on top of the video

### Worked Example

See `references/reel-production-worked-example.md` for a complete worked example from June 2026 — AI+ Agent Vibe Coding reel (8 scenes, 42s, instructor photo, ElevenLabs Lily voiceover, Cyrillic captions with Manrope + yellow glow). Includes full FFmpeg commands, SRT timing, caption styling reference, and voiceover script.

### 🔴 TikTok-Style Word-by-Word Captions for Reels

The user wants TikTok-style animated captions — each word (or small word chunk) appears individually, replacing the previous one, synchronized with the voiceover. NOT static sentences.

**Approach:** Generate SRT subtitles where each entry is a small word chunk (2-3 words) with its own timing slice.

```python
# Word-by-word chunk timing
words = text.split()
num_words = len(words)
word_dur = scene_duration / num_words
chunk_size = 2  # show 2 words at a time

for w_idx in range(0, num_words, chunk_size):
    chunk_end = min(w_idx + chunk_size, num_words)
    caption = " ".join(words[w_idx:chunk_end])
    start = scene_offset + (w_idx * word_dur)
    end = start + word_dur * chunk_size
    # write SRT entry: caption between start and end
```

### 🔴 Caption Styling (Final — June 2026 Correction)

After user feedback, the final caption styling for AI Global reels uses:

| Style | Value | Description |
|-------|-------|-------------|
| FontName | Manrope-Bold | Brand font (at ~/.fonts/manrope/Manrope-Bold.ttf) |
| FontSize | 10-11 | Small — user said "2 дахин жижиг" from 22pt |
| PrimaryColour | `&H0000FFFF` | **Yellow text** — user changed from white to yellow |
| OutlineColour | `&H00000000` | **Black outline** — thin, for readability |
| Outline | 0.5 | Thin — user said outline was too wide before |
| BorderStyle | 1 | Outline |
| Alignment | 2 | Bottom-center |
| MarginV | 40 | Vertical margin from bottom |

**Evolution:** Initial version used white text + yellow glow outline (2.5px). User corrected: "caption outline color to yellow and less weight — text not clear." Final: yellow text + thin black outline.

FFmpeg command:
```bash
ffmpeg -y -i raw_video.mp4 -i voiceover.mp3 \
  -c:v libx264 -pix_fmt yuv420p -r 30 \
  -vf "subtitles=captions.srt:fontsdir=/home/hermes/.fonts/manrope:force_style='FontName=Manrope-Bold,FontSize=10,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,Outline=0.5,BorderStyle=1,Alignment=2,MarginV=40'" \
  -c:a aac -b:a 128k -shortest \
  final_reel.mp4
```

FFmpeg command:
```bash
ffmpeg -y -i raw_video.mp4 -i voiceover.mp3 \
  -c:v libx264 -pix_fmt yuv420p -r 30 \
  -vf "subtitles=captions.srt:fontsdir=/home/hermes/.fonts/manrope:force_style='FontName=Manrope-Bold,FontSize=10,PrimaryColour=&H00FFFFFF,OutlineColour=&H00FFFF00,Outline=2.5,BorderStyle=1,Alignment=2,MarginV=40'" \
  -c:a aac -b:a 128k -shortest \
  final_reel.mp4
```

**Pitfall:** The SRT file path must be absolute (e.g. `$PWD/captions.srt`) or the subtitles filter can't find it.

- ❌ **NEVER use FFmpeg for generation** — only for merging + caption overlay
- ✅ **KIE gpt-image-2-image-to-image** (9:16) for all scene images
- ✅ **KIE ElevenLabs V3 — Lily voice** for all voiceover
- ✅ **FFmpeg** only after all KIE outputs are ready, for final composition
- All text on scenes must be in Cyrillic Mongolian (same rule as posters)
- English brand names (AI, IO, etc.) must stay in Latin — apply the same two-step language rule
- Send to Make.com webhook with `content_type=reel`

### ⚠️ Voiceover via KIE API — Use V3 Dialogue Model, Not V2 TTS

**The user corrected this in June 2026 — always use `elevenlabs/text-to-dialogue-v3` with `dialogue[]` array, NOT the old `elevenlabs/text-to-speech-multilingual-v2` API.**

The correct API uses a `dialogue` array where each entry has `text` and `voice`:

```bash
curl -s -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -d '{
  "model": "elevenlabs/text-to-dialogue-v3",
  "input": {
    "dialogue": [
      {"text": "<text segment 1>", "voice": "Lily"},
      {"text": "<text segment 2>", "voice": "Lily"}
    ]
  }
}'
```

**Key details:**
- Model: `elevenlabs/text-to-dialogue-v3` (NOT `elevenlabs/text-to-speech-multilingual-v2`)
- Format: `input.dialogue[]` — array of `{text, voice}` objects
- Voice name: `"Lily"` works as a plain string (no voice ID needed)
- Language: Mongolian text works naturally with Lily voice (no `language_code` param needed in v3)
- Split longer scripts into ~8 dialogue entries (one per scene) for cleaner segment management
- Total text across all entries must not exceed ~5000 characters
- Returns a single MP3 with all dialogue segments concatenated

**Pitfall:** Do NOT use `elevenlabs/text-to-speech-multilingual-v2` — the user will correct you. The V3 dialogue model has different delivery speed too (typically faster/shorter than V2).

## Content Type Rules

| Poster Content | Use Person Photo? | Use Graph/Chart? | Example |
|---|---|---|---|
| Course intro, instructor bio | ✅ Yes (M. Eland in circular frame) | ❌ No | Vibe Coding intro poster |
| Salary survey, research data | ❌ No | ✅ Yes (bar/pie/comparison charts) | Цалингийн судалгаа posters |
| General promotion, CTA | ❌ No | ❌ No | Standard text-only |

When the poster type is "цалингийн судалгаа" (salary survey/research), the content area should show statistical data visualizations (bar charts, pie charts, comparison graphs) instead of a person photo. Prompt: "Do NOT add any person photo. Instead, in the portrait area, add a professional bar chart/graph showing..."

## Prompt Engineering

The prompt needs to:
1. **Reference the background** — "On this dark tech background with gold decor" to keep temp1 intact
2. **Preserve temp1 exactly** — When using temp1, say: "Use the first image (temp1) as the background EXACTLY as-is — do NOT modify or alter the template design at all"
3. **Specify text placement** — "at top", "in center", "at bottom"
3. **Specify text color** — "gold", "white", "yellow"
4. **Specify language** — "Text in CYRILLIC MONGOLIAN only — do NOT use English/Latin letters for Mongolian words"
5. **Specify content type** — person photo vs graph/chart depending on poster purpose (see Content Type Rules above)
6. **End with** — "Keep the original background unchanged. Professional design, 1:1 square"

### Successful prompt examples (see references/successful-prompts.md)

## 🔴 Approval-First Workflow (ALL Content Types)

**This user requires approval BEFORE sending anything to Make.com or publishing.** This is a hard rule — not a suggestion.

For any generated content (carousel, poster, reel):
1. ✅ Generate one sample first and send it to the user via MEDIA: path on Telegram
2. ✅ Wait for explicit approval or correction request
3. ✅ Only after approval, generate the remaining items (if carousel: remaining 3 slides)
4. ✅ Only after ALL visuals are approved, send to Make.com webhook
5. ❌ NEVER send directly to Make.com without showing the user first

**Exception:** If the user explicitly says "send to Make" or "release" or "post it," you may skip the approval step for THAT content. But for new types of content (first reel, new course, new template), always show first.

## Critical Reel Rules

- ❌ **NEVER use FFmpeg for posters** — only for video/reel composition
- ❌ **NEVER use Pillow/Python drawing for posters** — KIE GPT Image 2 Image-to-Image is the ONLY approved poster generation method for ALL brands
- ❌ **NEVER use English/Latin letters for Mongolian words** — ALL text in Cyrillic Mongolian only
- ❌ **NEVER regenerate already-approved/on-Facebook posters** — only create new ones
- ✅ "Carousel" = always generate **4 posters** (for AI Global)
- ✅ Always upload the template/reference file to tmpfiles.org — local file paths don't work with KIE
- ✅ Show the generated poster to the user for approval before sending to Make (unless they say to send directly)
- ✅ All brand poster rules are the same — these rules apply universally to AI Global, Postly, AgenticForce, and any future brand

## 🔄 Brands Without Dedicated Templates

Some brands (like Postly, AgenticForce) do NOT have a dedicated poster template file (temp1/reeltemp1). For these brands:

1. **Use an existing brand reference image as the template.** Pick the most relevant existing brand asset (e.g. Postly's `postly-offer-pricing-infographic.jpg`) that represents the desired brand style.
2. **Upload that reference to tmpfiles.org** just like a template.
3. **In the prompt, describe the desired layout explicitly**, including all text content, colors, and structure. The reference image provides style guidance; the prompt provides the specific content.
4. **The prompt becomes the primary content source** — list all text, bullet points, prices, and layout positions in detail, since there's no fixed template to preserve.

### Template-Free Poster Patterns (Postly)

Two documented patterns exist:
- **Service Intro / Pricing** — `references/postly-service-intro-poster.md` (service categories + 3-tier pricing cards)
- **Digital Worker Workshop** — `references/postly-digital-worker-workshop-poster.md` (trainer photo + 3 agent cards + free training CTA + circular portrait workflow)

### Prompt Strategy for Template-Free Brands|

The prompt must be comprehensive enough to stand alone as a layout specification, because there's no visual template to "add text onto." Include:
- Background color/gradient specification
- Exact brand colors (hex or RGB)
- Section headers, bullet items, prices, and labels — all in Cyrillic Mongolian
- Layout order (top to bottom)
- Card/panel dimensions and arrangement (e.g. "three equal-width cards side by side")

See `references/postly-service-intro-poster.md` for a worked example with pricing tiers and purpose sections.

## Known Pitfalls

- **GPT Image 1.5 image-to-image** (`gpt-image/1.5-image-to-image`) returns Internal Error. Use 2.0.
- **Download 403**: tempfile.aiquickdraw.com blocks urllib but allows curl. Always use curl for download.
- **URL parsing**: tmpfiles.org returns a display URL, not a direct download. Must reconstruct with `/dl/<hash>/<filename>`.
- **Prompt text content**: GPT Image 2 may not render specific Cyrillic Mongolian text perfectly. It generates an image *in the style* described, not a literal overlay. Poster will have decorative text approximations, not exact typography. **Do NOT use Pillow/Python as a workaround** — the user has explicitly rejected this. Submit a clearer prompt instead.
- **Circular frame alignment**: When placing a person photo into temp1's portrait frame, the AI may ignore the provided photo and generate a generic face instead. Fix: strengthen prompt to say "use the person's face from the second image EXACTLY in the existing circular frame."
- **temp1 gets modified**: The AI may "redesign" temp1 instead of preserving it. Fix: prompt MUST say "EXACTLY as-is, do NOT modify or alter the template design at all, keep every element of it unchanged." If that still fails, **name each specific element** that must NOT change (logo, phone, background, decorations).
- **temp1 can be replaced**: The user may send a new temp1 at any time. Always overwrite the file and re-upload — never use a cached URL from a previous upload session. The file on disk is the authoritative temp1.
- **Generation time**: Can take 30s-3min. Poll every 10s (observed ~100s for image-to-image). Use `notify_on_complete=true` for background tasks.
- **Using Pillow/FFmpeg for posters**: This will be corrected by the user. ALWAYS use KIE GPT Image 2 Image-to-Image for posters, no exceptions. Pillow and FFmpeg are ONLY for video/reel composition.
- **KIE_API_KEY env var**: Available in `terminal()` (shell) but NOT in `execute_code` Python (returns 401). Always submit and poll KIE API tasks via `terminal()` with curl, not via `execute_code` Python with urllib/requests.
- **Polling pattern**: Use a bash for-loop with `sleep 10` and check state via `python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('state','unknown'))"` piped from curl. Break on "success" or "fail"/"failed". Observed: ~10 polls (~100s) typical for image-to-image.
- **tmpfiles hash changes per upload**: Even the same file gets a different hash each upload. Always extract the hash from the current upload response — never hardcode a previous hash.
