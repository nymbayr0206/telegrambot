# Full Prompt Pattern — AI Global Industry Update (aiglobal_industry_update_v1)

## Working Example (May 31, 2026)

This is the exact full prompt sent to GPT Image 2 for the "Internet being rebuilt for AI agents" industry update slide.

### Trigger
User says "pass everything to KIE" / "use full prompt" for a branded slide with no dedicated template endpoint.

### Model
`gpt-image-2-text-to-image` on KIE's marketplace endpoint.

### Prompt Template

```
Create a ONE single 1:1 square social media carousel slide poster for [BRAND NAME] ([BRAND], Mongolia).

FORMAT: 1:1 square, 1080x1080, social media carousel slide.

THEME: [HEADLINE_TOPIC]

BRAND STYLE:\n- Background: See live style authority at `/opt/data/social-content/brands/ai-global/carousel-prompt-instructions.md` for current colors. As of June 2026: light blue gradient (#E8F4FD → #D6EAF8), fresh modern feel. **Do NOT default to cream/off-white without checking the live doc.**\n- Typography: Clean modern sans-serif, charcoal (#1A1A1A) for headlines, gold (#D7AB46) for accent elements\n- Style: [STYLE_DESCRIPTION]

LAYOUT (top to bottom):
- TOP-LEFT corner: A small gold pill/badge that says "[BADGE_TEXT]" in white text on gold background (#D7AB46)
- TOP-RIGHT corner: [BRAND] brand logo (simple minimal text logo)
- MAIN HEADLINE: Large bold text in charcoal (#1A1A1A) saying "[HEADLINE]"
- SUBHEADLINE: Smaller text "[SUBHEADLINE]" in medium gray
- HERO VISUAL on right side: [VISUAL_DESCRIPTION]
- TREND 1: With [ICON] icon "[TREND_1]"
- TREND 2: With [ICON] icon "[TREND_2]"
- TREND 3: With [ICON] icon "[TREND_3]"
- BOTTOM: Thin gold divider line (#D7AB46)
- BOTTOM-LEFT: Contact info in small gray text "[PHONE] [WEBSITE]"
- CTA text near bottom: "[CTA_TEXT]"

IMPORTANT:
- [LANGUAGE] text
- Clean sans-serif font
- Airy design with generous whitespace
- Gold (#D7AB46) accent color
- Premium, modern, educational feel
- No watermarks, no extra logos
- Professional social media carousel slide
```

### Latin Transliteration Rule
When the prompt is sent as JSON, use **latin transliteration** for Mongolian Cyrillic text instead of raw Cyrillic characters. Reason: JSON encoding + shell handling of UTF-8 Cyrillic can produce garbled text. The model still understands the intended Mongolian words when written in latinized form.

Example mapping:
| Cyrillic | Latin transliteration |
|----------|----------------------|
| Интернетийг | Internetiig |
| Агентуудад | Agentuudad |
| Зориулж | Zoriulj |
| Дахин | Dakhin |
| Бүтээж | Butteej |
| Дараагийн | Daraagiin |
| давалгаанд | dalgaland |
| бэлэн | belen |
| боломж | bolomj |

### Real Production Example (May 31, 2026)

Complete prompt file at `/opt/data/ai-global-industry-update-prompt.json`:

```json
{
  "model": "gpt-image-2-text-to-image",
  "input": {
    "prompt": "Create a ONE single 1:1 square social media carousel slide poster for AI Global (AI GLOBAL brand, Mongolia)..."
  }
}
```

### Submission Pattern
```bash
# Write prompt to JSON file (never inline shell - UTF-8 mangling)
python3 -c "import json; json.dump({'model':'gpt-image-2-text-to-image','input':{'prompt':'...'}}, open('/tmp/prompt.json','w'), ensure_ascii=False)"

# Submit
TASK_ID=$(curl -s --location 'https://api.kie.ai/api/v1/jobs/createTask' \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d @/tmp/prompt.json | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['taskId'])")

# Poll
for i in $(seq 1 30); do
  state=$(curl -s "https://api.kie.ai/api/v1/jobs/recordInfo?taskId=$TASK_ID" \
    -H "Authorization: Bearer $KIE_API_KEY" | \
    python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('state','unknown'))")
  echo "[$i] State: $state"
  [ "$state" = "success" ] && break
  sleep 10
done
```

### Observed timing
- First poll: `"generating"` (some polls report this immediately)
- May stay in generating for 20-25 polls
- State transitions: generating → success (around poll 29 in one observed run)
- Total time: ~290 seconds for one slide
- Always set 30+ polls / 5+ minute timeout

### Download
```python
import urllib.request, json, ssl
ctx = ssl._create_unverified_context()
# Convert KIE URL to signed download URL
req = urllib.request.Request(
    "https://api.kie.ai/api/v1/common/download-url",
    data=json.dumps({"url": kie_url}).encode(),
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req, context=ctx, timeout=60)
signed = json.loads(resp.read())["data"]  # "data" is a string URL
# Download
urllib.request.urlretrieve(signed, "output.png")
```
