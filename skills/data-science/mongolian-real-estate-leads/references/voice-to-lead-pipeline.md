# Voice-to-Lead Pipeline Implementation

Complete implementation for processing a voice recording through the full lead pipeline.

## One-Shot Implementation (Python)

This is the core function — pass a voice file path, get back a saved lead record:

```python
#!/usr/bin/env python3
"""Process a voice recording through the full lead pipeline."""

import json, sqlite3, os, subprocess, tempfile
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
DB_PATH = "/opt/data/leads/real_estate.db"
STT_PROVIDER = "openai"  # "local" or "openai"
OPENAI_KEY = os.environ.get("VOICE_TOOLS_OPENAI_KEY", "")
WHISPER_MODEL = "whisper-1"  # OpenAI's best model

# ── Step 1: STT ─────────────────────────────────────────────────────

def transcribe(audio_path: str) -> str:
    """Transcribe audio to Mongolian text."""
    if STT_PROVIDER == "openai":
        return _transcribe_openai(audio_path)
    else:
        return _transcribe_local(audio_path)

def _transcribe_openai(audio_path: str) -> str:
    """Use OpenAI Whisper API."""
    import openai
    client = openai.OpenAI(api_key=OPENAI_KEY)
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=f,
            language="mn",
            response_format="text"
        )
    return transcript

def _transcribe_local(audio_path: str) -> str:
    """Use local faster-whisper."""
    from faster_whisper import WhisperModel
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, language="mn", beam_size=5)
    return " ".join(seg.text for seg in segments)

# ── Step 2: Intent Parsing ──────────────────────────────────────────

LEAD_PARSE_PROMPT = """Та Монгол хэл дээрх үл хөдлөх хөрөнгийн үйлчлүүлэгчийн 
дуут бичлэгийн транскриптыг задлан шинжилж, дараах JSON форматаар хариулах AI туслах байна.

Транскрипт:
{transcript}

Дараах талбаруудыг гаргаж авна уу:
- client_name: Үйлчлүүлэгчийн нэр (байхгүй бол null)
- phone: Утасны дугаар (байхгүй бол null)  
- property_type: "apartment" | "house" | "land" | "commercial" | "office"
- bedrooms: Өрөөний тоо (тоо, байхгүй бол null)
- district: Дүүргийн нэрс (массив, Монгол Кирилл)
- budget_min: Хамгийн бага төсөв (төгрөгөөр)
- budget_max: Хамгийн их төсөв (төгрөгөөр)
- buy_or_rent: "buy" | "rent"
- urgency: "low" | "medium" | "high" | "immediate"
- lead_score: 0-100 хүртэлх тоо
- lead_score_reason: Онооны тайлбар (монголоор)
- notes: Бусад мэдээлэл

Зөвхөн JSON хариулна уу. Бусад тайлбар, текст оруулж болохгүй."""

def parse_intent(transcript: str) -> dict:
    """Extract structured lead data from transcript using LLM."""
    prompt = LEAD_PARSE_PROMPT.format(transcript=transcript)
    # Call LLM — replace with your preferred method
    # Example using subprocess with Hermes CLI:
    result = subprocess.run(
        ["hermes", "chat", "-q", prompt, "-Q"],
        capture_output=True, text=True, timeout=60
    )
    output = result.stdout.strip()
    # Extract JSON from output
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        # Try to find JSON block
        import re
        match = re.search(r'\{.*\}', output, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise

# ── Step 3: Database ────────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            phone TEXT,
            property_type TEXT,
            bedrooms INTEGER,
            districts TEXT,
            budget_min INTEGER,
            budget_max INTEGER,
            buy_or_rent TEXT,
            urgency TEXT,
            lead_score INTEGER,
            lead_score_reason TEXT,
            notes TEXT,
            transcript TEXT,
            agent TEXT,
            raw_audio_path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            contacted INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn

def save_lead(conn, lead: dict, transcript: str, audio_path: str, agent: str = ""):
    """Save parsed lead to database."""
    conn.execute("""
        INSERT INTO leads (
            client_name, phone, property_type, bedrooms, districts,
            budget_min, budget_max, buy_or_rent, urgency,
            lead_score, lead_score_reason, notes, transcript,
            agent, raw_audio_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead.get("client_name"),
        lead.get("phone"),
        lead.get("property_type"),
        lead.get("bedrooms"),
        json.dumps(lead.get("district", []), ensure_ascii=False),
        lead.get("budget_min"),
        lead.get("budget_max"),
        lead.get("buy_or_rent"),
        lead.get("urgency"),
        lead.get("lead_score"),
        lead.get("lead_score_reason"),
        lead.get("notes"),
        transcript,
        agent,
        audio_path
    ))
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

# ── Full Pipeline ───────────────────────────────────────────────────

def process_voice_file(audio_path: str, agent: str = ""):
    """Full pipeline: transcribe → parse → save."""
    print(f"[1/3] Transcribing...")
    transcript = transcribe(audio_path)
    print(f"     Transcript: {transcript[:100]}...")
    
    print(f"[2/3] Parsing intent...")
    lead = parse_intent(transcript)
    print(f"     Lead score: {lead.get('lead_score')}/100 ({lead.get('client_name', 'unknown')})")
    
    print(f"[3/3] Saving to database...")
    conn = init_db()
    lead_id = save_lead(conn, lead, transcript, audio_path, agent)
    conn.close()
    
    print(f"\n✓ Lead #{lead_id} saved!")
    return lead_id


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: process_voice.py <audio_file> [agent_name]")
        sys.exit(1)
    process_voice_file(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
```

## Matching New Listings Against Leads

```python
def match_new_listings(conn):
    """Match new listings against all active leads."""
    new_listings = conn.execute("""
        SELECT * FROM listings 
        WHERE scraped_at > datetime('now', '-3 hours')
    """).fetchall()
    
    leads = conn.execute("SELECT * FROM leads WHERE contacted = 0").fetchall()
    
    for listing in new_listings:
        for lead in leads:
            score = compute_match_score(lead, listing)
            if score >= 70:  # threshold
                conn.execute("""
                    INSERT INTO matches (lead_id, listing_id, match_score)
                    VALUES (?, ?, ?)
                """, (lead[0], listing[0], score))
                notify_agent(lead, listing, score)

def compute_match_score(lead, listing):
    """Simple rule-based matching score 0-100."""
    score = 0
    
    # Property type match
    if lead[3] and lead[3] == listing[4]:
        score += 30
    elif not lead[3]:
        score += 15  # no preference
    
    # Bedrooms match
    if lead[4] and lead[4] == listing[5]:
        score += 25
    
    # Budget match
    if lead[6] and lead[7] and listing[2]:
        if lead[6] <= listing[2] <= lead[7]:
            score += 25
        elif listing[2] <= lead[6] * 1.1:  # within 10% over min
            score += 15
    
    # District match
    if lead[5]:
        districts = json.loads(lead[5])
        if listing[6] in districts:
            score += 20
    
    return score
```

## Verifying Setup

```bash
# Test STT works
python -c "
from faster_whisper import WhisperModel
model = WhisperModel('large-v3', device='cpu', compute_type='int8')
segments, info = model.transcribe('/tmp/test_audio.ogg', language='mn')
print('STT ready - detected language:', info.language)
"

# Test OpenAI Whisper
python -c "
import openai, os
client = openai.OpenAI(api_key=os.environ['VOICE_TOOLS_OPENAI_KEY'])
with open('/tmp/test_audio.ogg', 'rb') as f:
    text = client.audio.transcriptions.create(model='whisper-1', file=f, language='mn')
print('OpenAI STT ready:', text[:50])
"

# Test DB
python -c "
import sqlite3
conn = sqlite3.connect('/opt/data/leads/real_estate.db')
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print('Tables:', [t[0] for t in tables])
"
```
