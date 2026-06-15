# KIE GPT Image 2 Automated Cron Script Pattern

Session-derived notes from creating a `no_agent: true` cron job that generates 4 Supernova carousel slides via KIE GPT Image 2 and sends them to Make.com daily.

## Full Working Script

The production script lives at:
- Source: `/opt/data/social-content/brands/supernova/scripts/supernova_daily_carousel.py`
- Cron installed copy: `~/.hermes/scripts/supernova_daily_carousel.py`
- Cron job ID: `46232e14720b` — see `cronjob action=list`

## Key Lessons

### 1. Shell Escaping is Critical

Mongolian/Cyrillic prompts CANNOT be passed through `curl -d '...'` — the shell mangles UTF-8 bytes. This fails:

```bash
curl -X POST ... -d '{"prompt": "Монгол текст"}'  # BROKEN — shell garbles Cyrillic
```

**Working approach — Python `urllib.request`:**

```python
body = json.dumps({"prompt": "Монгол текст"}).encode("utf-8")
req = urllib.request.Request(url, data=body, headers=headers)
with urllib.request.urlopen(req) as resp:
    ...
```

**Alternative — temp JSON file + `curl -d @file`:**

```python
with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    json.dump(payload, f)
    tmp = f.name
subprocess.run(["curl", "-d", f"@{tmp}", ...])
```

### 2. KIE GPT Image 2 Response Shape

- `data.state`: `"generating"` / `"success"` / `"failed"`
- `data.resultJson`: a STRING containing JSON like `{"resultUrls": ["https://...png"]}`
  - Must be parsed: `json.loads(result_json)` before accessing `resultUrls`
- Generation time: ~3 minutes per slide at medium quality
- Completed URL: `https://tempfile.aiquickdraw.com/gpt-image-2-kie/...png`
- Use `/api/v1/common/download-url` to convert to temporary download URL, then save immediately
  - **Response shape:** `{"code":200, "msg":"success", "data":"https://signed-download-url..."}` where `data` is a **string** (the signed URL), not a dict
  - **Correct parsing:** `signed_url = json.loads(resp.read())["data"]` — do NOT call `.get("downloadUrl")` on it
  - **Pitfall:** Accessing the original `tempfile.aiquickdraw.com` URL without signed query params returns 403

### 3. Background Process Observation

- Python's stdout buffering prevents live Hermes log output
- `process(action="log")` may show 0 lines while process is running
- Prefer `terminal(timeout=600)` in foreground during testing
- Production cron: `no_agent: true` delivers stdout automatically on completion

### 4. Cron Timing & Cost

- 4 slides × ~3 min = 12-15 min per carousel
- Credits: ~$0.04-0.06/slide × 4 = ~$0.20-0.24/day
- Script timeout: at least 900s
- Schedule: 09:00 Ulaanbaatar = 01:00 UTC

### 5. State Invariant

```python
state["next_carousel"] += 1  # Only after Make.com HTTP 200
```

Non-zero exit on webhook failure → cron status = `error` → next tick retries same carousel number.

### 6. Script Path

Cron scripts must be bare filenames in `~/.hermes/scripts/`:
```yaml
script: "supernova_daily_carousel.py"  # ✅
script: "/absolute/path/script.py"     # ❌ rejected
```

### 7. ⚠️ CRITICAL: GPT Image 2 Does Not Use Real Brand Assets

**GPT Image 2 prompt-only generation invents its own logo and uses random colors.** Even with extremely detailed prompts specifying exact color hexes, logo descriptions, and brand element placement, the model produces a made-up logo and color scheme that looks plausible but is wrong. This was confirmed across 4 tested slides.

**Do NOT rely on GPT Image 2 prompts to reproduce actual brand assets.** Instead use a **two-stage deterministic overlay** pattern:

1. **Stage 1 — KIE GPT Image 2 or Nano Banana 2**: Generate a visually appealing **text-free background** matching the brand's visual style (medical/healthcare/premium). Prompt for `NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS` with clean negative space in the logo/title areas.

2. **Stage 2 — Pillow overlay (Python)**: Locally composite:
   - The actual brand logo (from `assets/logos/` PNG file)
   - Brand colors (exact hex codes from brand guide)
   - Fixed text elements (brand name, tagline, phone)
   - Slide numbers, title frames, ribbon/bookmark elements
   - Phone capsule, footer waves, icon badges

This guarantees brand fidelity and text accuracy regardless of model output quirks.

This guarantees brand fidelity and text accuracy regardless of model output quirks. See the full Supernova two-stage overlay reference at `references/supernova-two-stage-carousel-overlay.md`. The Pillow compositing template is at `social-media-automation` skill → `templates/supernova-carousel-overlay-v3.py`.

### 8. Prompt for Background-Only Generation

When using Stage 1, query the user for:
- The exact brand logo file (PNG with transparency preferred, JPG as fallback)
- Brand color hex codes
- The approved style reference image (visible reference file path)

Then write the background prompt as:

```python
prompt = (
    f"Create ONE separate 1:1 square social media carousel background image. "
    f"NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS. "
    f"Color palette: red (#F20B2E) and blue (#1768B5) accents on light sky-blue background (#DDEFF8). "
    f"Visual style: clean medical/healthcare infographic. "
    f"DNA helix, cells, medical icons, glowing bubbles. "
    f"Dark navy (#071B4D) ribbon at bottom. "
    f"White glowing highlights. "
    f"Leave negative space at top-right for logo, top-left for title, bottom-right for phone. "
    f"Mongolian healthcare aesthetic. "
    f"NO other slides, NO collage."
)
```

### 9. Pillow Compositing Checklist

```python
from PIL import Image, ImageDraw, ImageFont

# 1. Open background image
bg = Image.open("background.jpg").convert("RGBA")

# 2. Paste brand logo (top-right)
logo = Image.open("assets/logos/supernova-logo.png").convert("RGBA")
logo = logo.resize((180, 180), Image.LANCZOS)
bg.paste(logo, (bg.width - logo.width - 30, 30), logo)

# 3. Draw title capsule (top-left)
draw = ImageDraw.Draw(bg)
font = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
draw.rounded_rectangle((20, 20, 350, 90), radius=20, fill="#071B4D")
draw.text((40, 30), "Мэдлэгт дусал нэмэр", fill="white", font=font)

# 4. Draw slide ribbon
draw.text((30, 120), "1/4", fill="#1768B5", font=font)

# 5. Draw phone capsule (bottom-right)
draw.rounded_rectangle((bg.width - 250, bg.height - 70, bg.width - 20, bg.height - 20), radius=25, outline="#F20B2E", width=3)
draw.text((bg.width - 230, bg.height - 58), "Утас: 70000303", fill="#F20B2E", font=font)

# 6. Save
bg.save("final-slide-01.jpg", "JPEG", quality=95)
```

Font paths on this server:
- Bold: `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`
- Regular: `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`

### 10. User Preference: Brand Fidelity is Priority

When the user complains that generated slides don't match brand colors/logo, the root cause is almost always "GPT Image 2 prompt-only generation produces invented assets." The fix is deterministic overlay, not better prompts. The user's preferred approach for Mongolian branded carousels is:
- Background image from KIE (any model)
- All text/logo/phone/frames overlaid locally via Pillow
- Brand colors from brand-guide.md, not prompted in the AI image
