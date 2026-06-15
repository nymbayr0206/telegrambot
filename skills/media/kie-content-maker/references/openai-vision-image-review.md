# OpenAI GPT-4o Vision Image Review Workflow

## Overview

After generating KIE carousel slides (background via GPT Image 2 + deterministic asset overlay), run an **automated quality review** using OpenAI GPT-4o vision. This catches brand compliance issues, overlapping elements, text errors, and visual artifacts before the user sees the result.

## Workflow

```
KIE generate → OpenAI vision review → PASS / FAIL
                                   ↓            ↓
                             deliver to     fix instructions →
                             user           re-review → PASS?
```

## The Review Script

Location: **`/opt/data/scripts/review_image.py`**

A standalone Python script that sends a carousel image to GPT-4o with a structured review prompt and returns structured JSON. Uses the `openai` Python library (not `requests`).

### Usage

```bash
# Simple review (grade + scores + issues + fix instructions)
python3 /opt/data/scripts/review_image.py /path/to/image.jpg

# Verbose — shows progress and file size
python3 /opt/data/scripts/review_image.py /path/to/image.jpg --verbose

# Machine-readable JSON
python3 /opt/data/scripts/review_image.py /path/to/image.jpg --json
```

### Environment

```bash
export OPENAI_API_KEY='sk-...'
```

The script reads `OPENAI_API_KEY` from the environment. Requires the `openai` Python package:

```bash
pip install openai
```

### What It Checks (6 criteria, each scored 1-10)

| # | Criterion | What's evaluated |
|---|-----------|------------------|
| 1 | **text_readability** | Text clear, properly sized, readable. No cut-off, no overlap |
| 2 | **layout_alignment** | Elements properly positioned. No awkward spacing, no misalignment |
| 3 | **logo_placement** | Brand logo correctly positioned and sized. Not too big/small, not overlapping |
| 4 | **image_quality** | High resolution. No artifacts, pixelation, distortion |
| 5 | **brand_consistency** | Matches brand style (colors, fonts, overall aesthetic) |
| 6 | **professionalism** | Would a paying client accept this? No AI artifacts, weird faces/text |

### Scoring Rubric

- **Grade A** — All scores ≥ 7, image is professional → **PASS**
- **Grade B** — Some scores 6-7, minor issues → **PASS** (quick fixes encouraged)
- **Grade C** — Multiple scores 5-6, significant issues → **FAIL**
- **Grade D** — Scores 3-4, major rework needed → **FAIL**
- **Grade F** — Scores ≤ 3, unusable → **FAIL**

### Example JSON Output (PASS)

```json
{
  "grade": "A",
  "verdict": "PASS",
  "scores": {
    "text_readability": 9,
    "layout_alignment": 9,
    "logo_placement": 9,
    "image_quality": 9,
    "brand_consistency": 9,
    "professionalism": 9
  },
  "issues": [],
  "fix_instructions": [],
  "summary": "Зураг бэлэн байна."
}
```

### Example JSON Output (FAIL)

```json
{
  "grade": "F",
  "verdict": "FAIL",
  "scores": {
    "text_readability": 7,
    "layout_alignment": 5,
    "logo_placement": 4,
    "image_quality": 6,
    "brand_consistency": 3,
    "professionalism": 2
  },
  "issues": [
    "Text contains spelling errors.",
    "Logo is misspelled and not clearly positioned.",
    "Poor layout alignment with awkward spacing.",
    "Lack of brand consistency in colors and fonts.",
    "Overall unprofessional appearance."
  ],
  "fix_instructions": [
    "Correct spelling errors in the text.",
    "Ensure the logo is correctly spelled and positioned.",
    "Improve layout alignment and spacing.",
    "Use brand-consistent colors and fonts.",
    "Enhance overall professionalism of the design."
  ],
  "summary": "Энэ зураг нь мэргэжлийн бус байна."
}
```

### Integration Into KIE Generation Pipeline

After compositing the assets onto the template, call review immediately:

```python
import subprocess, json

script = "/opt/data/scripts/review_image.py"
result = subprocess.run(
    ["python3", script, output_path, "--json"],
    capture_output=True, text=True, timeout=60
)
review = json.loads(result.stdout.strip())

if review.get("verdict") == "PASS":
    print("✅ PASS — sending to user")
else:
    print(f"❌ FAIL (Grade {review.get('grade')}): {review.get('summary')}")
    for fix in review.get("fix_instructions", []):
        print(f"  🔧 {fix}")
```

## FAIL-Case Testing Pattern

When onboarding a new user to the review pipeline, demonstrate both PASS and FAIL cases explicitly:

### Step 1: Generate a deliberately bad image

```python
from PIL import Image, ImageDraw
img = Image.new('RGB', (1080, 1080), (80, 80, 80))  # wrong brand color
draw = ImageDraw.Draw(img)
draw.text((50, 100), 'AI GLOBL', fill='#FF0000')    # misspelled, wrong color
img.save('test-bad.jpg', quality=50)
```

### Step 2: Review — expect FAIL (F) with fix instructions

```bash
python3 /opt/data/scripts/review_image.py test-bad.jpg --verbose
```

The agent returns 5-6 specific issues AND 5-6 ordered fix instructions.

### Step 3: Fix based on agent's instructions

Follow the `fix_instructions` array item by item: correct text, add brand colors, position logo, fix layout.

### Step 4: Re-review to measure improvement

```bash
python3 /opt/data/scripts/review_image.py test-bad-fixed.jpg --verbose
```

Expected: grade improves (e.g. F → C), issue count drops, scores rise. Residual issues may remain if the fix was partial — this is expected and demonstrates the pipeline's honesty.

### Why this works with the user

The user (Battushig, AI Global / Postly) explicitly wanted to see the agent's **fix-instruction flow** before trusting automated review. Showing FAIL → fix instructions → re-review improvement builds confidence in the pipeline.

## Setup Requirements

- **OpenAI API key** with GPT-4o access (model: `gpt-4o`)
- `pip install openai` (the script uses the `openai` Python library, not `requests`)

### Quick setup check

```bash
python3 -c "from openai import OpenAI; print('openai lib OK')"
```

## Adding to a Cron Job (Auto-Review Before Publish)

If the daily carousel cron should auto-review before publishing, add a review step in the script:

```python
import subprocess, json, sys

result = subprocess.run(
    ["python3", "/opt/data/scripts/review_image.py", output_path, "--json"],
    capture_output=True, text=True, timeout=60
)
review = json.loads(result.stdout.strip())
if review.get("verdict") != "PASS":
    print(f"❌ Review FAILED: {review.get('summary')}")
    for fix in review.get("fix_instructions", []):
        print(f"  FIX: {fix}")
    sys.exit(1)
# If PASS, continue to webhook publish
```

## Pitfalls

- **False positives:** GPT-4o vision sometimes passes images with subtle issues. The review is a hygiene gate, not a replacement for human QA.
- **False negatives:** Very occasionally flags a good image for imaginary issues. If the user approves despite a FAIL, re-run with `temperature=0` (edit the script's `temperature=0.3` line).
- **API cost:** ~2000 tokens/image at `detail:high`. At GPT-4o pricing (~$5/1M input, ~$15/1M output) this is ~$0.03/image — negligible.
- **API key env var required:** `OPENAI_API_KEY` must be set in the shell. The `execute_code` tool does NOT have access to shell env vars — always use the `terminal` tool, not `execute_code`, to run the review script.
- **Path confusion:** The script lives at `/opt/data/scripts/review_image.py`, NOT under any brand subdirectory. Do not look for it at brand-specific paths like `social-content/brands/*/scripts/`.
- **No `--brand` flag exists:** Our script is brand-agnostic — it evaluates on general professionalism, text, layout, and logo criteria. Brand-specific checking comes from the SYSTEM_PROMPT's general criteria, not a per-brand flag. If brand-specific criteria are needed, modify the SYSTEM_PROMPT variable in the script (the 6-score structure stays the same).
