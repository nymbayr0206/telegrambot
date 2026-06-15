# PDF → Mongolian Audiobook (Multi-Voice Dialogue)

Extract English text from a PDF, translate to Mongolian, format as alternating male+female dialogue, and generate chapter-by-chapter MP3 files via KIE ElevenLabs.

## Workflow

### 1. Extract text from PDF (per chapter)

```bash
uv venv /tmp/pdfvenv --clear
uv pip install --python /tmp/pdfvenv/bin/python pymupdf
/tmp/pdfvenv/bin/python -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for i in range(doc.page_count):
    page = doc[i]
    print(f'=== PAGE {i+1} ===')
    print(page.get_text())
"
```

### 2. Translate English → Mongolian & Format as Dialogue

Split into alternating dialogue turns. Use two distinct voices:
- **Female**: `Lily` (host/narrator — introduces topics, asks questions, transitions)
- **Male**: `Callum` (guest/expert — provides insights, explanations, main content)

Other supported male voices on KIE: `Daniel`, `Liam`.

Keep each turn reasonable (50-400 chars). For longer PDF sections, split across multiple dialogue turns to keep the audio natural.

### 3. Create Dialogue JSON Payload

Submit to KIE ElevenLabs via the multi-voice script:

```bash
python3 /opt/data/scripts/kie_multi_voice_tts.py /tmp/dialogue.json /tmp/chapter1.mp3
```

#### JSON format:
```json
{
  "model": "elevenlabs/text-to-dialogue-v3",
  "input": {
    "dialogue": [
      {"text": "Тавтай морилно уу. ...", "voice": "Lily"},
      {"text": "Тийм ээ, энэхүү ...", "voice": "Callum"}
    ],
    "stability": 0.5
  }
}
```

### 4. Multi-Voice Script

Located at `/opt/data/scripts/kie_multi_voice_tts.py`.

Usage: `python3 kie_multi_voice_tts.py <json_input_path> <output_audio_path>`

The script:
- Reads the JSON payload with `dialogue` array (each entry has `text` + `voice`)
- Submits to KIE API at `https://api.kie.ai/api/v1/jobs/createTask`
- Requires `KIE_API_KEY` env var
- Polls for completion (up to 4.5 minutes)
- Downloads the resulting MP3

### 5. Chapter-by-Chapter Output

For full PDFs (multiple chapters), repeat steps 1-4 per chapter and name outputs as:
- `/tmp/homebook_ch1.mp3`
- `/tmp/homebook_ch2.mp3`
- etc.

Deliver each via `MEDIA:/path/to/file.mp3`.

## Pricing

| Provider | Rate | Our 2,284-char test |
|----------|------|-------------------|
| KIE ElevenLabs | **$0.07 / 1K chars** | ~$0.16 (~₮570) |
| fal.ai (ElevenLabs) | $0.10 / 1K chars | ~$0.23 (~₮820) |
| ElevenLabs direct | ~$0.10-0.20 / 1K chars | ~$0.23-0.46 |

KIE exchange rate: 1 credit = $0.005 USD. KIE pricing is ~30% cheaper than fal.ai / ElevenLabs direct.

Conversion (June 2026): 1 USD ≈ ₮3,569 MNT.

## Supported Voices on KIE

- **Female**: `Lily` ✓
- **Male**: `Callum` ✓, `Daniel` ✓, `Liam` ✓

Unsupported on KIE (tested): Antoni, Sam, Adam, Patrick, Thomas, Michael, Oliver, Ethan, Henry, Jack, Noah, James, Benjamin, Lucas, William, Mason, Elijah, Alexander — all return 422/500.

## Pitfalls

- **Dialogue model**: Use `elevenlabs/text-to-dialogue-v3` (NOT the standard TTS model) for multi-voice output
- **Voice validation**: KIE has a restricted voice list — always test with a short 1-turn request first
- **Turns limit**: Keep dialogue array entries manageable (5-10 turns per request). Very long arrays may time out
- **Text length**: Max 40,000 chars per submission per the Hermes TTS config. Split long chapters
- **Mongolian TTS quality**: `elevenlabs/text-to-dialogue-v3` handles Mongolian well as it's a multilingual model
- **Timeouts**: Default polling is 90 attempts × 3s = 4.5 min. Increase for very long audio
- **Stability**: `0.5` is a good default for dialogue. Lower = more expressive, higher = more consistent
