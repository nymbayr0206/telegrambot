---
name: mongolian-real-estate-leads
description: "Full pipeline for Mongolian real estate lead management — voice intake, STT transcription, intent parsing, lead scoring, client preference storage, property listing scraping, and automated client-to-property matching with agent notification."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mongolia, real-estate, lead-scoring, stt, voice, scraping, matching]
    related_skills: [zangia-lead-generation, maps]
---

# Mongolian Real Estate Leads

End-to-end pipeline for capturing real estate client leads from voice recordings, parsing their requirements, scoring their likelihood to buy, and matching them against scraped property listings.

## Pipeline Overview

```
Voice File (.ogg/.mp3/.wav)
    │
    ▼
┌─────────────────────┐
│ 1. STT Transcription │  ← Local faster-whisper or OpenAI Whisper API
└─────────┬───────────┘
          │ "Би 3 өрөө байр хайж байна, Баянзүрх дүүрэгт, 200 сая хүртэл"
          ▼
┌─────────────────────┐
│ 2. Intent Parsing    │  ← LLM extract structured fields + lead score
└─────────┬───────────┘
          │ {name, phone, property_type, bedrooms, district, budget, lead_score}
          ▼
┌─────────────────────┐
│ 3. Database Save     │  ← SQLite or PostgreSQL lead table
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 4. Listing Scraping  │  ← Every 3h: crawl unegui.mn, remax.mn, zangia.mn
└─────────┬───────────┘
          │ New property listings
          ▼
┌─────────────────────┐
│ 5. Client Matching   │  ← Match new listings against saved client prefs
└─────────┬───────────┘
          │ "Match found: 3-өрөө байр, 180M₮, Баянзүрх"
          ▼
┌─────────────────────┐
│ 6. Agent Notification│  ← Telegram / SMS / Email alert
└─────────────────────┘
```

## 1. Speech-to-Text (STT)

| Option | Cost | Mongolian Quality | Setup |
|--------|------|-------------------|-------|
| **Local faster-whisper large-v3** | **$0** | ⭐⭐⭐⭐ | Already installed, set `language=mn` |
| OpenAI Whisper API | $0.006/min | ⭐⭐⭐⭐ | Set `VOICE_TOOLS_OPENAI_KEY` + `stt.provider: openai` |
| Groq Whisper | Free tier | ⭐⭐⭐ | Set `GROQ_API_KEY` + `stt.provider: groq` |

**Recommendation:** Local faster-whisper large-v3 for zero cost. Switch to OpenAI Whisper API only if you need higher accuracy on difficult audio (background noise, multiple speakers, phone call recordings).

### STT Config

```yaml
# Hermes config.yaml
stt:
  enabled: true
  provider: local     # local | openai | groq
  local:
    model: large-v3
    language: mn      # Force Mongolian (empty = auto-detect)
```

Gateway restart required after config changes: `/restart` in Telegram or `hermes gateway restart`.

## 2. Intent Parsing & Lead Scoring

After transcription, call an LLM to extract structured data and score the lead. Use a cheap model (DeepSeek, local LLM) — this is a simple extraction task.

### Extracted Fields

```json
{
  "client_name": "Баярмаа",
  "phone": "99112233",
  "property_type": "apartment",
  "bedrooms": 3,
  "district": ["Баянзүрх", "Сүхбаатар"],
  "budget_min": 150000000,
  "budget_max": 200000000,
  "buy_or_rent": "buy",
  "urgency": "high",
  "lead_score": 85,
  "lead_score_reason": "Clear requirements, ready to buy within month",
  "notes": "Зуслангийн газар байхгүй бол хамаагүй",
  "agent": "Бат-Эрдэнэ",
  "transcript": "Би 3 өрөө байр хайж байна..."
}
```

### Lead Scoring Criteria

| Factor | Weight |
|--------|--------|
| Has specific requirements (district, budget, rooms) | +20 |
| Short timeline ("энэ сард", "дараа долоо хоногт") | +25 |
| Has budget range | +15 |
| Is buyer not renter | +10 |
| Provided phone number | +15 |
| Referred by existing client | +15 |

Score 0-100. Thresholds: Hot (80+), Warm (50-79), Cold (<50).

### Prompt Template

Save as `templates/lead-parsing-prompt.txt` — the self-contained prompt for the subagent/script:

```
Та Монгол хэл дээрх үл хөдлөх хөрөнгийн үйлчлүүлэгчийн дуут бичлэгийн 
транскриптыг задлан шинжилж, дараах JSON форматаар хариулах AI туслах байна.

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
```

## 3. Database Schema

```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT,
    phone TEXT,
    property_type TEXT,
    bedrooms INTEGER,
    districts TEXT,           -- JSON array
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
    contacted INTEGER DEFAULT 0,
    matched_listing_id INTEGER
);

CREATE TABLE listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,               -- unegui.mn, remax.mn, zangia.mn
    listing_id TEXT UNIQUE,    -- source's original ID
    title TEXT,
    price INTEGER,
    property_type TEXT,
    bedrooms INTEGER,
    district TEXT,
    address TEXT,
    url TEXT,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER REFERENCES leads(id),
    listing_id INTEGER REFERENCES listings(id),
    match_score INTEGER,
    notified INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 4. Property Listing Scraping

Use the `references/mongolian-web-scraping.md` reference file for detailed scraping patterns. Key sites:

| Site | Type | Coverage |
|------|------|----------|
| unegui.mn | SSR HTML | Apartments, houses, land, commercial |
| remax.mn | Azure Search API | RE/MAX listings, structured OData query |
| zangia.mn | SSR/SPA | Classifieds, agent listings |

**Recommended schedule:** Every 3 hours, run a batch script that:
1. Scrapes ALL new listings (not per-client — one pass)
2. Stores in `listings` table with dedup by `listing_id`
3. Runs matching query against all active leads

**Load:** ~30 seconds CPU, ~50-200 HTTP requests per run. Negligible on any VPS.

## 5. Client-Property Matching

After scraping new listings, run a matching query:

```sql
SELECT l.*, lst.* 
FROM leads l
CROSS JOIN listings lst
WHERE lst.scraped_at > (SELECT MAX(scraped_at) FROM listings) - INTERVAL '3 hours'
  AND (l.property_type IS NULL OR lst.property_type = l.property_type)
  AND (l.bedrooms IS NULL OR lst.bedrooms = l.bedrooms)
  AND (l.budget_min IS NULL OR lst.price >= l.budget_min)
  AND (l.budget_max IS NULL OR lst.price <= l.budget_max)
  AND (l.districts IS NULL OR lst.district IN JSON_EXTRACT(l.districts, '$'))
```

For more advanced matching, use vector embeddings on property descriptions vs. client notes.

## 6. Agent Notification

Delivery methods in priority order:
- **Telegram DM** — fastest, most reliable (use Hermes send_message)
- **SMS** — if agent is not on Telegram
- **Email** — fallback

Notification template:
```
🔔 ШИНЭ ТААРЧ БОЛОМЖ
Үйлчлүүлэгч: {client_name}
Утас: {phone}
Хайсан: {bedrooms}-өрөө {property_type}, {district}
Төсөв: {budget_min:,}₮ - {budget_max:,}₮
Оноо: {lead_score}/100
---
Тохирох зар: {listing_title}
Үнэ: {price:,}₮
Холбоос: {url}
```

## Server Load Estimates

| Component | Per-Run Cost | Notes |
|-----------|-------------|-------|
| STT (local whisper) | $0 | ~5-10s per minute of audio |
| STT (OpenAI Whisper) | $0.006/min | ~$0.01 per typical 2-min voice |
| LLM parsing | $0.001-0.003 per file | DeepSeek or local model |
| Scraping (1000 listings) | $0 | ~30s CPU, VPS handles easily |
| Matching 1000 clients | $0 | SQL query, <1s |
| **Total per day (50 leads)** | **~$0.15** | With OpenAI Whisper |

**Scaling:** 1000 client profiles × 8 scrapes/day is trivial for any modern VPS. The bottleneck is the scraping sites' rate limits, not server resources. Spread scrapes 5-10 minutes apart per site.

## Alternative Storage: EspoCRM

The SQLite schema is the reference implementation. If using **EspoCRM 9.x** as your backend (Dream Team crm or similar), use the `espocrm-integration` skill which covers:

- Auth via X-Api-Key header vs. web admin login
- Custom entity CRUD — RealEstateProperty, RealEstateRequest
- Currency field gotchas (MUST set value+currency in same request)
- Call logging with parent linking
- Field validation requirements
- HTTP status code semantics, entity discovery, pagination/filtering

The `RealEstateRequest` entity maps 1:1 to the `leads` table. The `RealEstateProperty` entity maps to the `listings` table. Create both via REST API — no SQL needed.

## Related Skills

- `zangia-lead-generation` — Zangia.mn company/person lead scraping
- `maps` — geocoding Mongolian addresses for location-based matching

## References

- `references/voice-to-lead-pipeline.md` — detailed implementation guide with code
- `references/lead-parsing-prompt.md` — LLM prompt templates for Mongolian intent parsing
- `references/espocrm-api.md` — EspoCRM 9.x REST API reference for real estate entities (Dream Team crm)
- `references/mongolian-web-scraping.md` — scraping patterns for unegui.mn (SSR) and remax.mn (React SPA + Azure Search API); general Mongolian site scraping methodology
- `references/unegui-parsing.md` — detailed unegui.mn data extraction patterns (HTML structure, author analysis, price distribution)
- `references/remax-api.md` — complete remax.mn API reference (ConfigRegion, Azure Search OData query, listing URL construction, pagination)
