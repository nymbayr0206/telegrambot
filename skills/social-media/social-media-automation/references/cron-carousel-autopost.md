# Cron-job carousel autopost orchestration

## Overview

Two architectures for automated brand carousel generation + publishing via cron:

1. **LLM-driven** (Hermes agent generates slides, then a shell script handles upload)
2. **Script-only / no_agent:true** (pure Python script calls KIE API directly, no LLM tokens)

Choose based on complexity. The script-only pattern is simpler, cheaper, and more reliable for deterministic series.

## State file (`automation/daily-carousel-state.json`)

```json
{
  "series_total": 18,
  "next_carousel": 1,
  "completed": [],
  "last_run_at": null,
  "last_status": null,
  "timezone": "Asia/Ulaanbaatar",
  "schedule": "daily 09:00"
}
```

## Webhook config (`automation/make-webhook.json`)

```json
{
  "name": "supernova_make_carousel_autopost",
  "type": "make.com_webhook",
  "url": "https://hook.us1.make.com/YOUR_WEBHOOK_ID",
  "method": "POST",
  "content_type": "multipart/form-data",
  "purpose": "Autopost Brand 4-slide carousel images to Make.com workflow",
  "fields": {
    "brand": "supernova",
    "campaign": "Campaign Name",
    "carousel_number": "integer 1-18",
    "topic": "topic title",
    "model": "gpt-image-2-text-to-image",
    "language": "mn",
    "format": "1:1 square carousel",
    "caption": "Mongolian caption",
    "slide1": "image/jpeg file",
    "slide2": "image/jpeg file",
    "slide3": "image/jpeg file",
    "slide4": "image/jpeg file"
  },
  "schedule": {
    "timezone": "Asia/Ulaanbaatar",
    "time": "09:00",
    "frequency": "daily",
    "series_total": 18,
    "next_carousel": 1
  }
}
```

## Architecture A: LLM-driven (agent + shell script)

The cron job runs as `no_agent: false` (default). The Hermes agent:
1. Reads state file for `next_carousel`
2. Looks up topic from carousel plan
3. Generates 4 GPT Image 2 slides via the `image_generate()` tool (FAL.ai backend)
4. Saves slides to `generated/cron/carousel-NN/`
5. Runs a shell script that sends the 4 slides to Make.com webhook and advances state

### ⚠️ Shell script bug: inline Python + bash $NEXT variable

Using inline Python in a shell script to extract the topic from a plan file can fail with `NameError: name 'NEXT' is not defined` because bash's `$NEXT` may not expand inside single quotes or certain double-quote contexts. The fix is to **always use a standalone .py file** for cron logic rather than inline Python.

Symptoms: `Traceback ... NameError: name 'NEXT' is not defined` when the script runs via cron.

Fix: Write the entire cron logic as a Python script, reference it from the cron job.

### Shell script (legacy pattern — avoid for new jobs)

Must be in `~/.hermes/scripts/` — cronjob tool rejects absolute paths.

```bash
#!/usr/bin/env bash
set -euo pipefail

BRAND_DIR="/opt/data/social-content/brands/supernova"
STATE_FILE="${BRAND_DIR}/automation/daily-carousel-state.json"
WEBHOOK_FILE="${BRAND_DIR}/automation/make-webhook.json"

STATE=$(cat "$STATE_FILE")
NEXT=$(echo "$STATE" | python3 -c "import sys,json; print(json.load(sys.stdin)['next_carousel'])")
SERIES_TOTAL=$(echo "$STATE" | python3 -c "import sys,json; print(json.load(sys.stdin)['series_total'])")
WEBHOOK_URL=$(python3 -c "import json; d=json.load(open('$WEBHOOK_FILE')); print(d['url'])")

if [ "$NEXT" -gt "$SERIES_TOTAL" ]; then
  echo "Series complete."
  exit 0
fi

SLIDE_DIR="$BRAND_DIR/generated/cron/carousel-$(printf '%02d' $NEXT)"
SLIDE1=$(find "$SLIDE_DIR" -name "*01*" -o -name "*1*" | head -1)
SLIDE2=$(find "$SLIDE_DIR" -name "*02*" -o -name "*2*" | head -1)
SLIDE3=$(find "$SLIDE_DIR" -name "*03*" -o -name "*3*" | head -1)
SLIDE4=$(find "$SLIDE_DIR" -name "*04*" -o -name "*4*" | head -1)

CAPTION="Supernova — Telomer Effect | #Supernova"

RESP=$(curl -sS -w "\n%{http_code}" -X POST "$WEBHOOK_URL" \
  -F "brand=supernova" \
  -F "campaign=Telomer Effect Ebook Carousel Series" \
  -F "carousel_number=$NEXT" \
  -F "model=gpt-image-2-text-to-image" \
  -F "language=mn" \
  -F "caption=$CAPTION" \
  -F "slide1=@$SLIDE1;type=image/jpeg" \
  -F "slide2=@$SLIDE2;type=image/jpeg" \
  -F "slide3=@$SLIDE3;type=image/jpeg" \
  -F "slide4=@$SLIDE4;type=image/jpeg")

HTTP_CODE=$(echo "$RESP" | tail -1)
if [ "$HTTP_CODE" = "200" ]; then
  python3 -c "
import json, datetime
d = json.load(open('$STATE_FILE'))
d['completed'].append(d['next_carousel'])
d['next_carousel'] += 1
d['last_run_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
d['last_status'] = 'success'
json.dump(d, open('$STATE_FILE','w'))
"
  echo "SUCCESS: Carousel #$NEXT posted."
else
  echo "FAILED: HTTP $HTTP_CODE"
  exit 1
fi
```

### Cron job creation (LLM-driven)

```python
cronjob(
  action="create",
  name="Brand daily carousel autopost",
  schedule="0 1 * * *",  # 09:00 Asia/Ulaanbaatar in UTC
  deliver="origin",
  skills=["social-media-automation"],
  model={"model": "deepseek-chat", "provider": "custom:deepseek"},
  script="brand_daily_carousel.sh",
  enabled_toolsets=["terminal", "file", "skills"],
  prompt="""# Brand Daily Carousel — Cron Job
Read automation/daily-carousel-state.json for next_carousel.
Look up topic from carousel-plans/. Generate 4 GPT Image 2 slides.
Save to generated/cron/carousel-NN/. Run script brand_daily_carousel.sh."""
)
```

## Architecture B: Script-only / no_agent:true (pure Python + KIE API)

The cron job runs as `no_agent: true`. A single self-contained Python script:
1. Reads state file
2. Generates 4 slides via KIE.AI GPT Image 2 API (not FAL.ai)
3. Polls each until complete (~3 min/slide)
4. Downloads the temporary KIE URLs
5. Sends to Make.com webhook
6. Advances the state file

Benefits over LLM-driven:
- No LLM tokens consumed (cheaper)
- No Hermes agent overhead (faster)
- Deterministic — same prompt every time
- Self-contained error recovery

### Script key pattern

```python
#!/usr/bin/env python3
import json, os, sys, time, urllib.request

KIE_API_KEY = os.environ["KIE_API_KEY"]
BASE = "https://api.kie.ai"
HEADERS = {"Authorization": f"Bearer {KIE_API_KEY}", "Content-Type": "application/json"}

def kie_req(m, ep, d=None):
    url = f"{BASE}{ep}"
    h = HEADERS.copy()
    if d:
        req = urllib.request.Request(url, data=json.dumps(d).encode(), headers=h, method=m)
    else:
        req = urllib.request.Request(url, headers=h, method=m)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

def gen_slide(prompt):
    r = kie_req("POST", "/api/v1/jobs/createTask", {
        "model": "gpt-image-2-text-to-image",
        "input": {"prompt": prompt, "aspect_ratio": "1:1"}
    })
    tid = r["data"]["taskId"]
    for _ in range(30):
        time.sleep(10)
        s = kie_req("GET", f"/api/v1/jobs/recordInfo?taskId={tid}")
        st = s.get("data", {}).get("state")
        if st == "success":
            rj = s["data"].get("resultJson", "{}")
            if isinstance(rj, str): rj = json.loads(rj)
            return rj.get("resultUrls", [None])[0]
        elif st == "failed":
            return None
    return None

def dl(url, path):
    c = kie_req("POST", "/api/v1/common/download-url", {"url": url})
    dl_url = c.get("data", url)
    req = urllib.request.Request(dl_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        with open(path, "wb") as f: f.write(r.read())
```

### Cron job creation (script-only)

```python
cronjob(
  action="create",
  name="Brand daily carousel autopost via KIE",
  schedule="0 1 * * *",
  deliver="origin",
  script="brand_daily_carousel.py",
  no_agent=True,
  enabled_toolsets=["terminal"],
)
```

Model/provider not needed since no LLM runs.

## Prompt-only brand enrichment (for Architecture B / KIE GPT Image 2)

When using the script-only pattern with KIE GPT Image 2, the model ALWAYS invents a fake logo regardless of prompt detail. However, prompt enrichment IS effective for colors and layout. Use this BRAND_PROMPT pattern:

```python
BRAND_PROMPT = """EXACT brand colors: primary red #F20B2E, primary blue #1768B5, soft sky blue #DDEFF8, white #FFFFFF, gray #6B6F77.

Logo at TOP-RIGHT: white rounded square card with soft shadow. Inside: Supernova logo — red medical cross icon inside a blue circular protective swirl, with red+blue Cyrillic SUPERHOVA/SUPERNOVA wordmark. Below logo: gray tagline "ЯПОН УЛСЫН ЖИШИГ ЭМНЭЛЭГ".

Fixed elements:
- TOP-LEFT white rounded title capsule: "Мэдлэгт дусал нэмэр" in dark navy bold font with small water-drop icon.
- Blue ribbon bookmark slide counter on left side (1/4, 2/4, 3/4, 4/4).
- Large rounded white content panel in lower-middle area with a circular icon badge (blue outline) on left side.
- BOTTOM-RIGHT: phone number in white pill/capsule frame with red outline + red phone icon: "Утас: 70000303".
- BOTTOM/LEFT: red and blue wave/ribbon decorative elements across lower edge.

Colors for text: main text dark navy #071B4D, emphasized words in Supernova red #F20B2E, dividers and ribbons in healthcare blue #1768B5.

Background: bright sky-blue #DDEFF8 with soft gradient, medical bubbles/cells, DNA helix, molecule icons, and white glowing highlights. Healthcare/medical aesthetic.

Typography: heavy rounded bold sans-serif font. Large readable Mongolian Cyrillic text. No clutter, strong whitespace.

People (if shown): Mongolian/East Asian looking, positive healthcare context, respectful.

NO other slides, NO collage, NO contact sheet. Generate ONLY this single slide as a final poster image."""

slide_prompts = [
    f"ONE separate 1:1 square social media carousel slide. {BRAND_PROMPT} Slide counter: 1/4. HOOK slide about: {topic}. Big engaging headline.",
    f"ONE separate 1:1 square social media carousel slide. {BRAND_PROMPT} Slide counter: 2/4. SCIENCE EXPLANATION slide about: {topic}.",
    f"ONE separate 1:1 square social media carousel slide. {BRAND_PROMPT} Slide counter: 3/4. PRACTICAL ADVICE slide about: {topic}.",
    f"ONE separate 1:1 square social media carousel slide. {BRAND_PROMPT} Slide counter: 4/4. SUMMARY + CTA slide about: {topic}. Phone in bottom-right.",
]
```

Result: Colors and layout structure will match the brand. Logo will still be invented — alert the user and offer two-stage overlay if they need exact logo matching.

## KIE API prompt-sending: JSON temp file technique

When sending GPT Image 2 prompts containing Mongolian/Cyrillic text, shell escaping will break curl commands. The reliable fix is to write the JSON payload to a temp file and use curl's `-d @file` syntax:

```python
import json, tempfile

prompt = "ONE separate 1:1 square social media carousel slide. ... Mongolian text ..."
payload = {
    "model": "gpt-image-2-text-to-image",
    "input": {"prompt": prompt, "aspect_ratio": "1:1"}
}

# Write to temp file to avoid shell escaping issues
tmpfile = f"/tmp/kie_payload_{int(time.time())}.json"
with open(tmpfile, 'w', encoding='utf-8') as f:
    json.dump(payload, f)

result = subprocess.run([
    "curl", "-sS", "-X", "POST",
    "https://api.kie.ai/api/v1/jobs/createTask",
    "-H", "Authorization: Bearer $KIE_API_KEY",
    "-H", "Content-Type: application/json",
    "-d", f"@{tmpfile}"
], capture_output=True, text=True)

os.unlink(tmpfile)  # clean up
```

Even with `urllib.request`, the JSON-dump-to-temp-file technique is the most reliable approach for the LLM-driven cron job (Architecture A) where the agent generates slides via Python.

## One-shot cron jobs (single-use scheduled tasks)

Use `repeat=1` to create a cron job that fires once at a specific time and never again:

```python
cronjob(
  action="create",
  name="One-time brand carousel generation",
  schedule="2026-05-28T02:00:00Z",  # ISO 8601 UTC
  deliver="origin",
  skills=["social-media-automation", "kie-content-maker"],
  model={"model": "deepseek-chat", "provider": "custom:deepseek"},
  prompt="... detailed generation instructions ...",
  repeat=1,  # fires once then auto-deletes
)
```

The `schedule` field accepts both cron expressions (`"0 1 * * *"`) and ISO 8601 timestamps (`"2026-05-28T02:00:00Z"`). Combined with `repeat=1`, this creates a self-destructing scheduled task.

## Pre-generated slide template system (Architecture B)

When generating 4-slide carousels from a topic list, maintain a `_CAROUSEL_TOPIC_TEMPLATES` array indexed by carousel number (0-based), with 4 `headlines`, 4 `bodies`, and 4 `visuals` per entry. The script picks `templates = templates[next_num - 1]` and builds prompts by interpolating headline/body/visual into the BRAND_PROMPT_BASE.

For carousels beyond the template array, a fallback generates generic prompts from the topic name.

### Full self-contained Python script pattern

Most reliable Architecture B: a single Python script does everything — generate, poll, download, publish:

1. Load state, look up topic from plan
2. Get slide templates (or fallback)
3. For each of 4 slides: POST to KIE createTask, poll recordInfo until success/fail, parse resultJson → resultUrls[0], get download URL, save immediately (KIE URLs expire fast)
4. Send 4 files to Make.com via multipart POST
5. On HTTP 200: advance state file
6. Exit 0 on success, 1 on failure

Implementation details from a working script:
- **KIE resultJson is a stringified JSON** — always `json.loads()` it explicitly
- **Download URL response:** `{"data":"<signed-url>"}` — data is a plain string, not a dict
- **Use `urllib.request`** for KIE API calls (stdlib), `requests` for Make.com multipart
- **KIE_API_KEY** from env var or `/opt/data/.env`
- **Timeouts:** 120s createTask, 600s total poll/slide, 120s download
- **Slide failures are per-slide** — don't abort the series on one failure
- **Permalink copies:** save to both cron dir AND `generated/carousel-NN-<topic>/`
- KIE gen times: 2-5 min/slide typical, can hit 10+ min
- Poll every 10s, max 60 attempts per slide

## KIE GPT Image 2 timing reference

| Step | Time |
|---|---|
| Task creation | < 1s |
| Generation (GPT Image 2, medium quality) | ~3 min/slide |
| KIE gen times | 3-7 min/slide typical, up to 15+ min |
| Poll every 10s, max 60 attempts per slide

## Architecture C: Agent-driven script (hybrid — recommended for complex cron jobs)

The cron job runs as `no_agent: false` (default LLM-driven mode) but instead of the agent generating images directly, the agent delegates to a self-contained Python script via the terminal tool. The script handles KIE API calls, polling, downloading, and webhook publishing while the agent reports the result to the user.

### When to use this pattern

- The cron needs to generate images via KIE GPT Image 2 (not FAL.ai image_generate tool)
- The generation + publish logic is complex enough for a standalone Python script
- You want the agent to summarize results in Mongolian and handle edge cases
- The cron needs to report back to the user in natural language about what was published

### Implementation

1. **Write the Python script** (place at a source path under the brand's workspace, symlink to `~/.hermes/scripts/`):
   ```bash
   ln -sf /opt/data/social-content/brands/brandname/scripts/auto_generate_and_publish.py /opt/data/.hermes/scripts/auto_generate_and_publish.py
   ```

2. **Cron job config** — no_agent: false (default), script field is optional since the agent runs the script explicitly:
   ```python
   cronjob(
     action="create",
     name="Brand daily auto-generate + publish carousel",
     schedule="0 1 * * *",
     deliver="origin",
     prompt="Run the script. Check output. Report to user in Mongolian.",
     enabled_toolsets=["terminal", "file"],
     model={"model": "deepseek-chat", "provider": "custom:deepseek"},
   )
   ```

3. **The script should**:
   - Read state file for `next_carousel`
   - Look up topic from carousel plan
   - Generate 4 slides via KIE GPT Image 2 (sequential, not parallel)
   - Poll each until success (~3-5 min/slide)
   - Download and save immediately (KIE URLs expire fast)
   - Send to Make.com via multipart POST with requests library
   - Advance state file on HTTP 200
   - Exit 0 on success, 1 on failure

4. **The cron prompt should instruct the agent to**:
   - Run the Python script with a generous timeout (900s)
   - Read stdout/stderr for success/failure messages
   - Report to the user in Mongolian
   - Handle script timeouts gracefully (retry next day)

### ⚠️ Shell script inline Python bug (Architecture A only)

When using Architecture A (no_agent shell script), inline Python in a bash script can fail with `NameError: name 'NEXT' is not defined` because bash's `$NEXT` does not expand inside inline Python code's f-string curly braces. The expression `f'{NEXT}.'` in a Python heredoc inside double-quoted `python3 -c "..."` does NOT expand the bash variable because there's no `$` prefix on `NEXT`.

**Bug symptom:** `Traceback ... NameError: name 'NEXT' is not defined` when the script runs via cron.

**Wrong code (inline Python in bash):**
```bash
TOPIC=$(python3 -c "
lines = open('$PLAN_FILE').readlines()
for line in lines:
    if line.strip().startswith(f'{NEXT}.'):   # BUG: NEXT is NOT a bash/py variable
        print(line.strip().split('.', 1)[1].strip())
        break
")
```

**Fix:** Use a standalone .py file for cron logic rather than inline Python in shell scripts. Architecture B (pure Python script) or Architecture C (agent-driven script) avoid this entirely because they don't mix bash/Python variable namespaces.

### Recovery from stuck tasks

When generating images via KIE GPT Image 2 within a script:
- Set per-slide timeout: max 60 polls × 10s = 10 min
- If a slide task stays in `"generating"` state for >60 polls, do NOT abort the entire carousel
- Submit a fresh task for that slide with a slightly simplified prompt
- Let both tasks run in parallel — take whichever completes first
- If only 3/4 slides complete, still attempt to publish with the available slides
- Save all successfully generated slides before attempting the next

## Decision tree for brand fidelity issues

When generating carousel slides for a branded series:

1. User says "improve the prompt / add more detail" → Enrich BRAND_PROMPT with exact hex colors, layout, and logo description. The model renders colors well; logos will be invented.

2. User says "this is wrong" or complains about logo → Switch to two-stage: text-free background generation + local Pillow overlay with actual logo PNG.

3. User sends a logo image file → Save to assets/logos/. Explain: "I saved your logo. Prompt-only generation can't embed specific images. I'll switch to two-stage: generate clean backgrounds, then overlay the real logo and brand colors locally."

## Script tips for KIE GPT Image 2

- Write JSON payload to a temp file and use `curl -d @file` to avoid shell escaping issues with Cyrillic/Mongolian text. See the "JSON temp file technique" section above.
- Poll for at least 2-3 minutes per slide (generate time is ~3 min for GPT Image 2).
- KIE `recordInfo` returns `resultJson` as a **stringified JSON string** — always parse it explicitly with `json.loads()`.
- Download KIE URLs immediately after generation — temporary links expire quickly.
- Use `python3 -u` or `sys.stdout.reconfigure(line_buffering=True)` for unbuffered output in cron context.
- On cron job run, the script executes in `~/.hermes/scripts/` — use absolute paths for brand data files.

1. **Script path:** Must be relative filename in `~/.hermes/scripts/`. Absolute paths are rejected by the cronjob tool.
2. **Model/provider on LLM-driven jobs:** Set explicitly on the cron job — the user may change their default provider later.
3. **Error recovery:** Script exits non-zero on failure -> state not advanced -> next tick retries same carousel number.
4. **Missing script file:** The cron job errors silently with `last_status: error` if the script file doesn't exist. Check `~/.hermes/scripts/` before creating the job.
5. **Approval exception:** Pre-approved series bypass the approval-first rule for cron execution. The user approved the plan; the cron just executes.
6. **KIE script-only path:** For pure Python scripts, use `urllib.request` not `curl` in shell commands to avoid UTF-8 escaping issues with Mongolian/Cyrillic text in prompts.
7. **KIE download URL expiry:** Save generated images to disk immediately. KIE temporary URLs expire quickly.
