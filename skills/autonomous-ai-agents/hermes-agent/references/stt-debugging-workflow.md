# STT Debugging Workflow

When voice/STT fails, do NOT start with code patches. Follow this diagnostic chain FIRST.

## 1. Which `.env` file does the gateway read?

**This is the #1 cause of "STT configured but not working."**

The gateway reads `$HERMES_HOME/.env`, NOT `~/.hermes/.env`.

On many container setups, `HERMES_HOME=/opt/data` so the gateway reads `/opt/data/.env`.
The CLI reads `~/.hermes/.env` which resolves to `/opt/data/home/.hermes/.env`.

**Diagnostic:**

```bash
# Find which .env the gateway reads
grep "^HERMES_HOME" /opt/data/.env
# Or check config.yaml location
hermes config path            # CLI config
# Gateway config location:
ls -la /opt/data/.env /opt/data/home/.hermes/.env
```

**Fix:** Ensure the STT API key (`VOICE_TOOLS_OPENAI_KEY`, `GROQ_API_KEY`, etc.) is in BOTH or in the gateway's `.env`.

## 2. Verify the key is actually loaded

```bash
# Read the gateway's actual env
cat $HERMES_HOME/.env | grep -E "VOICE_TOOLS|GROQ_API|OPENAI_API"
```

## 3. Check the STT config section

```
stt:
  enabled: true
  provider: openai       # one of: local, groq, openai, mistral, xai
  openai:
    model: whisper-1
```

## 4. Check gateway logs for the actual error

```bash
tail -20 /opt/data/logs/gateway.log | grep -iE "transcribe|stt|whisper|error|api key"
```

Look for:
- `"No STT provider available"` → provider not configured
- `"VOICE_TOOLS_OPENAI_KEY nor OPENAI_API_KEY is set"` → key missing from gateway env
- `"Invalid file format"` → usually a side effect of missing key (file passed but auth failed)
- `"API error: 401"` → bad key
- `"API error: 400"` → check file format or actual error message

## 5. Test the STT provider directly

```bash
# Test OpenAI Whisper
python3 -c "
import os
os.environ['VOICE_TOOLS_OPENAI_KEY'] = open('/opt/data/.env').read().split('VOICE_TOOLS_OPENAI_KEY=')[1].split('\n')[0]
from openai import OpenAI
client = OpenAI(api_key=os.environ['VOICE_TOOLS_OPENAI_KEY'], timeout=30)
with open('/path/to/test.wav', 'rb') as f:
    t = client.audio.transcriptions.create(model='whisper-1', file=f, response_format='text')
print('STT OK:', t[:100])
"

# Test Groq Whisper
python3 -c "
import os
os.environ['GROQ_API_KEY'] = open('/opt/data/.env').read().split('GROQ_API_KEY=')[1].split('\n')[0]
from groq import Groq
client = Groq(api_key=os.environ['GROQ_API_KEY'])
with open('/path/to/test.wav', 'rb') as f:
    t = client.audio.transcriptions.create(model='whisper-large-v3', file=f, response_format='text')
print('STT OK:', t[:100])
"
```

## 6. Common pitfalls summary

| Symptom | Real cause (NOT what to patch) |
|---------|-------------------------------|
| "Invalid file format" | Usually API key missing or wrong — not an actual format issue |
| "No STT provider available" | `stt.provider` not set or misspelled in config.yaml |
| Silence / no transcript | Gateway env != CLI env — key is in `~/.hermes/.env` but gateway reads `$HERMES_HOME/.env` |
| Works in CLI test but not in gateway | Gateway needs restart after config/env change |
