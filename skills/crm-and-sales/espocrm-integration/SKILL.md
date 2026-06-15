---
name: espocrm-integration
description: "EspoCRM REST API integration — read/write entities, manage calls, tasks, real estate requests. Used for Dream Team CRM instance."
version: 1.0.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
tags: [espocrm, crm, real-estate, api]
---

# EspoCRM Integration

EspoCRM REST API integration for reading and writing CRM entities. Targeted at the Dream Team CRM (real estate) instance but applicable to any EspoCRM 9.x instance.

## 🚫 HARD RULES (non-negotiable — user-corrected)

### Rule: ALWAYS log phone calls as Call records

**Never create a Meeting, Task, or update a Lead/Request for a phone interaction without FIRST creating the Call record.**

- The Call is the **primary record** — it comes before anything else
- Direction: `"Inbound"` if caller called you, `"Outbound"` if you called them
- Status: Always `"Held"` for completed calls
- Link to parent entity (RealEstateProperty, RealEstateRequest, or Lead)
- assignedUserId and dateEnd are REQUIRED

> Why: User explicitly said _"Утасны дуудлагыг бас давхар заавал тэмдэглэж байгаарай"_ — calls must ALWAYS be logged. Skipping the Call was a previous mistake.

## Authentication Methods

### Method 1: API Key (X-Api-Key header) — Preferred

Best for automated/read-only access. Roles managed via Administration > API Keys in the web UI.

```bash
API_KEY="your-api-key"
BASE="http://host:port/api/v1"
curl -H "X-Api-Key: <api_key>" "$BASE/Entity"
```

### Method 2: Session Token (AuthToken endpoint)

Full admin CRUD access if admin credentials are used. Token expires after session timeout.

```bash
# Login to get a token
TOKEN=$(curl -s -X POST "http://<host>:<port>/api/v1/AuthToken" \
  -H "Content-Type: application/json" \
  -d '{"userName":"admin","password":"<pass>"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Use the token
curl -H "Authorization: Bearer $TOKEN" "http://<host>:<port>/api/v1/Lead"
```

### HTTP Status Code Semantics

| Code | Meaning | X-Status-Reason |
|------|---------|-----------------|
| 200 | Success — data returned | — |
| 401 | Unauthorized — wrong auth method or credentials | — |
| 403 | Forbidden — auth recognized but no permission | `No read/create/delete access.` or `No access to 'Entity'.` |
| 404 | Not Found — entity doesn't exist on this instance | — |
| 500 | Server error — entity exists but internal error | — |

**Pitfalls:**
- **403 vs 401**: 403 means the API key IS recognized but lacks entity permission. Add roles via the web UI (Administration > API Keys).
- **Empty response ≠ no data**: Check `total` field in response. `{"total": 0, "list": []}` means genuinely empty; an empty body means 403/401 (check with `-sv`).
- **API key can't self-modify**: The API key blocks access to `/api/v1/ApiKey` or `/api/v1/AuthToken` unless explicitly granted. Use admin session token or web UI to change permissions.

### EspoCRM Version Discovery

```bash
curl -s "http://<host>:<port>/api/v1/Settings" -H "X-Api-Key: <key>" | python3 -c "
import json, sys
s = json.load(sys.stdin)
print(f'Version: {s.get(\"version\", \"unknown\")}')
print(f'App: {s.get(\"applicationName\", \"unknown\")}')
print(f'Currencies: {s.get(\"currencyList\", [])}')
print(f'Timezone: {s.get(\"timeZone\", \"unknown\")}')
"
```

### Entity Discovery Strategy

1. **Try common entities**: Account, Contact, Lead, Opportunity, Case, User, Note, Meeting, Call, Task, Document
2. **Read `/api/v1/Settings`** for the definitive configured entity list: `tabList` (all UI tabs), `globalSearchEntityList`, `quickCreateList`
3. **Common real-estate custom entities**: `RealEstateProperty` (listings), `RealEstateRequest` (buyer/tenant requests)

Some EspoCRM 9.x instances return 403 for entity listing without a `maxSize` param. Always test with `?maxSize=1` as a first probe.

**Metadata API parity gap:** `/api/v1/metadata/entityDefs/EntityName` works for standard entities (Opportunity, Lead) but returns empty for custom entities (RealEstateProperty, RealEstateRequest). Use the Settings endpoint for entity discovery instead.

### Pagination, Filtering & Ordering

```bash
# Paginate
curl "...api/v1/Lead?offset=0&maxSize=20"

# Filter by date (today)
curl "...api/v1/Task?filter[0][type]=today&filter[0][attribute]=dateStart&maxSize=20"

# Filter by status
curl "...api/v1/Task?filter[0][type]=equals&filter[0][attribute]=status&filter[0][value]=Not+Started"
```

**Date Filter Types:**

| Type | Description |
|------|-------------|
| `today` | Matches records where `attribute` equals today's date |
| `past` | Matches records where date is in the past |
| `future` | Matches records where date is in the future |
| `between` | Matches records between two dates (requires `from` and `to`) |
| `equals` | Exact match on a field value |

## Connection

EspoCRM uses `X-Api-Key` header authentication. No session token needed unless modifying API keys.

```bash
API_KEY="your-api-key"
BASE="http://host:port/api/v1"
```

## Entity Reference

### RealEstateRequest — incoming client requests

| Field | Type | Example |
|---|---|---|
| `type` | string | `"Sale"`, `"Rent"` |
| `propertyType` | string | `"Apartment"`, `"Land Lot"` |
| `fromBedroomCount`, `toBedroomCount` | int | `3` |
| `fromPrice`, `toPrice` | int (currency) | `500000000` |
| `fromPriceCurrency`, `toPriceCurrency` | string | `"USD"` |
| `status` | string | `"New"` |
| `description` | text | Full notes |
| `parentType`, `parentId` | for linking | `"RealEstateProperty"`, ID |

### Call — phone call records

| Field | Type | Notes |
|---|---|---|
| `name` | string | Descriptive title |
| `dateStart`, `dateEnd` | datetime | `"2026-06-12 13:00:00"` |
| `durationMinutes` | int | |
| `status` | string | `"Held"`, `"Not Held"`, `"Planned"` |
| `direction` | string | `"Outbound"`, `"Inbound"` |
| `description` | text | Call notes |
| `parentType`, `parentId` | link | e.g. `RealEstateRequest`, its ID |
| `assignedUserId` | string | User UUID |

### Task — follow-up actions

| Field | Type | Notes |
|---|---|---|
| `name` | string | Task title |
| `dateStart`, `dateEnd` | datetime | |
| `status` | string | `"Not Started"`, `"Completed"` |
| `priority` | string | `"High"`, `"Normal"` |
| `parentType`, `parentId` | link | e.g. `RealEstateRequest` |
| `assignedUserId` | string | User UUID |

## Essential API Patterns

### Create a record
```bash
curl -s -X POST "$BASE/RealEstateRequest" \
  -H "X-Api-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"Rent","propertyType":"Apartment","fromBedroomCount":3,"toBedroomCount":3}'
```

### Update a record (PUT)
```bash
curl -s -X PUT "$BASE/RealEstateRequest/$ID" \
  -H "X-Api-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"description":"Updated info"}'
```

### Currency field workaround (⚠️ ESSENTIAL)
In EspoCRM 9.x, currency fields on custom entities fail validation unless **both** `price` AND `priceCurrency` are set in the **same** request:
```bash
# WRONG — fails with "validCurrency" error:
curl ... -d '{"fromPrice": 500000000}' 

# RIGHT — works:
curl ... -d '{"fromPrice": 500000000, "fromPriceCurrency": "USD"}'
```
The field order matters — set both fields atomically.

**🚨 Currency code must be in the system's configured list.** Even with both fields set, using an unconfigured currency code (e.g. `"MNT"` when only `"USD"` is in the system) produces the same `validCurrency` error:

Check available currencies first:
```bash
curl -s "$BASE/Settings" -H "X-Api-Key: $API_KEY" | python3 -c "
import json, sys
s = json.load(sys.stdin)
print('Available currencies:', s.get('currencyList', []))
print('Default currency:', s.get('defaultCurrency', ''))
"
```

If the desired currency (e.g. MNT) is NOT in `currencyList`, you **CANNOT** set price fields at all. Workaround: omit price from the request and store the budget in the `description` field instead.

> For generating a full Python CLI bot via Codex CLI, see `references/codex-bot-prompt.md` in this skill directory.

### List all records
```bash
curl -s "$BASE/RealEstateRequest" -H "X-Api-Key: $API_KEY"
```

### Get single record
```bash
curl -s "$BASE/RealEstateRequest/$ID" -H "X-Api-Key: $API_KEY"
```

## Call Follow-Up Workflow

When a client call results in a scheduled follow-up (e.g. "called back in 2 weeks"):

1. **Create Call record** — POST to `/Call` with status=Held, direction=Outbound, linked to parent RealEstateRequest
2. **Update RealEstateRequest** — PUT description with latest status
3. **Create Task** — POST to `/Task` with dateStart=follow-up date, status=Not Started, priority=High, linked to parent
4. **Set cron reminder** — create a 1-time cron job for the follow-up date (morning Mongolia time, UTC+8)

```bash
# Example: Create Call
curl -X POST "$BASE/Call" \
  -H "X-Api-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Client call - description",
    "dateStart": "2026-06-12 13:00:00",
    "dateEnd": "2026-06-12 13:10:00",
    "durationMinutes": 10,
    "status": "Held",
    "direction": "Outbound",
    "description": "Notes...",
    "parentType": "RealEstateRequest",
    "parentId": "$REQUEST_ID",
    "assignedUserId": "$USER_ID"
  }'
```

## Lead Entity

For new incoming calls, create a **Lead** alongside the RealEstateRequest.

| Field | Type | Convention |
|---|---|---|
| `firstName` | string | Phone number (e.g. `"80001059"`) |
| `lastName` | string | Location (e.g. `"Хан-Уул"`) |
| `phoneNumber` | string | `+976XXXXXXXX` — MUST include country code prefix |
| `status` | string | `"New"` |
| `source` | string | `"Call"` |
| `description` | text | Full notes about the client |

### Entity Choice Guide

| Entity | When to use |
|---|---|
| **Lead** 🟡 | New caller — first contact, not yet qualified |
| **Contact** 🟢 | Known person — multiple conversations, relationship established |
| **Account** 🏢 | Organization — developer, company, real estate firm |
| **RealEstateProperty** 🏠 | Property for sale/rent (the asset — owner/landlord side) |
| **RealEstateRequest** 📋 | What the client is looking for (the need — buyer/tenant side) |

### Property Scenario Guide

| Situation | Entity combo | Notes |
|---|---|---|
| Client wants to **BUY** | Lead + RealEstateRequest (type: Sale) | Person looking to purchase |
| Client wants to **RENT** (tenant) | Lead + RealEstateRequest (type: Rent) | Person looking to lease |
| Client has property to **SELL** (owner) | Lead + RealEstateProperty (requestType: Sale) | Owner listing property |
| Client has property to **RENT OUT** (landlord) | Lead + RealEstateProperty (requestType: Rent) | Owner listing property |
| Realtor/Agent from company | Contact + Account + (maybe RealEstateProperty) | Agent calling about a listing |
| Matching existing requests | Check all RealEstateRequest/RealEstateProperty for matches | Recommend or alert user |

### Workflow: New Call → CRM (HARD RULE: Call FIRST)

```
📞 New call arrives or goes out:
   1. 🥇 CREATE CALL RECORD (status=Held, direction=Inbound/Outbound, link to parent) ← ALWAYS FIRST
   2. Create Lead if new caller (phone as firstName, location as lastName, +976 prefix)
   3. Create associated entity:
      - Buyer/tenant → RealEstateRequest (type: Sale/Rent)
      - Owner/landlord → RealEstateProperty (requestType: Sale/Rent)
      - Realtor/Agent → Contact + Account

🤝 After talking / scheduling:
   1. Update parent entity description with latest status
   2. Create Meeting (if in-person scheduled)
   3. Create Task (if follow-up needed, dateStart=follow-up date, status=Not Started)
   4. Set 1-time cron job for morning-of reminder (see Cron Jobs section)

🔄 After multiple conversations / confirmed relationship:
   → Convert Lead to Contact (or create Contact and link to requests/properties)
```

### Account & Contact Creation for Companies

When adding a real estate office or agency:

```bash
# Create Account
curl -X POST "$BASE/Account" \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{
    "name": "RE/MAX 100%",
    "website": "https://www.remax.mn",
    "phoneNumber": "+97672700100",
    "billingAddressStreet": "Romana Residence - 1104, Хан-Уул, 15-р хороо",
    "billingAddressCity": "Улаанбаатар",
    "billingAddressCountry": "Монгол улс",
    "description": "RE/MAX 100% оффис"
  }'

# Create Contact (agent) linked to Account
curl -X POST "$BASE/Contact" \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{
    "firstName": "Lkhamsuren",
    "lastName": "Oyun",
    "phoneNumber": "+97688117615",
    "title": "Realtor",
    "accountId": "<account_id>",
    "source": "RE/MAX",
    "description": "RE/MAX 100% риэлтор. Хан-Уул дүүрэг."
  }'
```

### Phone Number Format

Phone numbers **must** use international format with `+976` (Mongolia) prefix:

```bash
# ✅ Works:
"phoneNumber": "+97680001059"

# ❌ Fails with "valid" validation error:
"phoneNumber": "80001059"
"phoneNumber": "99667788"
```

The API masks middle digits in responses (`+976****1059`) but stores the full number.

## Reporting & Aggregation

### Building a Cross-Entity Leaderboard

Aggregate data across entities to rank agents by performance. See `references/leaderboard-pattern.md` for a complete working script.

**Entity assignment chase order** (who created/owns what):
1. Check `assignedUserId` first — this is the person the record was assigned to
2. Fall back to `createdById` — this is who entered it (important for unassigned records created by API/system)
3. Note: `createdById` may point to an API user (type=`api`), not a real agent — filter these out

**Metric weighting (for this Dream Team CRM user):**
| Metric | Weight | Entity | Field to count |
|--------|--------|--------|----------------|
| Calls | 10 pts each | Call | assignedUserId |
| Leads | 15 pts each | Lead | createdById |
| Opportunities | 25 pts each | Opportunity | createdById |
| Requests | 5 pts each | RealEstateRequest | createdById |
| Properties | 5 pts each | RealEstateProperty | createdById |

**Common pitfalls:**
- The `Leaderboard` UI tab in EspoCRM may not be a real API entity — `GET /api/v1/Leaderboard` returns 404. Always probe with `?maxSize=1` and check the HTTP response body, not just status code.
- Tab list in Settings often includes custom tabs that link to external pages. Parse `tabList` from `/api/v1/Settings` to discover real entities vs UI-only tabs.
- Users of type `api` (from API key usage) show up in User list but are not real agents. Filter with `type != "api"` or `isActive == true`.

### On-Demand Cron Script Pattern ("Just Say The Word")

For commands the user wants to trigger by voice/keyword (e.g. "leaderboard" → auto-send report):

1. **Write a self-contained shell script** — Python inline via heredoc, with no external dependencies beyond curl + Python stdlib
2. **Place in `~/.hermes/scripts/`** (the only directory cron's no_agent scripts can read from)
3. **Create a cron job with `no_agent=true`** — this runs the script directly, skips the LLM, and delivers stdout verbatim to the chat:

```python
cronjob(
  action="create",
  name="leaderboard",
  schedule="0 0 * * *",  # daily at 00:00 UTC = 08:00 Mongolia
  no_agent=True,
  script="leaderboard.sh"  # relative to ~/.hermes/scripts/
)
```

4. **Trigger on demand** when user says the keyword:
```python
cronjob(action="run", job_id="<job_id>")
```
The `no_agent` mode delivers the script's stdout directly as the Telegram message — no agent loop, no LLM tokens consumed.

**Delivery semantics for no_agent=True:**
- Non-empty stdout → sent verbatim to the user
- Empty stdout → silent (nothing sent)
- Non-zero exit / timeout → error alert sent

**Pitfalls:**
- Script paths MUST be relative (just filename) to `~/.hermes/scripts/` — absolute paths are rejected
- The script inherits no Python venv — use `/usr/bin/python3` or inline `python3 << 'PYEOF'`
- Markdown in stdout renders correctly on Telegram: `*bold*`, `_italic_`, `` `code` ``, emoji
- The script runs in the cron scheduler's working directory, not the skill directory — use absolute paths or `dirname "$0"`

### Daily Morning Task Check (Cron Job)

Set up a daily cron job to check EspoCRM tasks due today and remind via Telegram:

```bash
# Create via cronjob tool:
cronjob(
  action="create",
  name="Өглөөний CRM Task сануулга",
  schedule="0 0 * * *",           # 00:00 UTC = 08:00 Mongolia
  enabled_toolsets=["terminal"],   # only needs curl
  prompt="Өнөөдөр EspoCRM-д хийх Task-уудыг шалгаж, Telegram-аар сануулах."
)
```

**Prompt behavior (self-contained, no chat context):**
1. `GET /api/v1/Task` — fetch all tasks via `curl`
2. Filter by `status: "Not Started"` and `dateStart` matching today's date in UTC+8
3. If tasks found → return formatted Telegram reminder text
4. If no tasks → return empty string (silent — cron delivers nothing)

For API-level date filtering, use:
```
GET /api/v1/Task?filter[0][type]=today&filter[0][attribute]=dateStart&maxSize=20
```

**Non-Mongolia timezone users:** Adjust schedule expression. The cron fires at 00:00 UTC; for UTC+8 this is 08:00 morning. For other timezones, compute the UTC offset: target_local_hour_in_UTC = local_hour - utc_offset.

**Idempotency rule:** If no tasks are due, the cron MUST return empty/silent. Do NOT send "no tasks today" messages — users find them noisy.

## Pitfalls

- **🚨 ALWAYS LOG CALLS FIRST**: Never create a Meeting, Task, or Lead update for a phone-based interaction without first creating the Call record. This was user-corrected — the user expects an unbroken log of every call. The Call is the parent interaction; everything else is a child of it.
- **Phone search unreliable**: Filtering by `?phoneNumber=` query param often returns empty. Reliable approach: pull full list with `?maxSize=50` and parse client-side with Python `json.loads()` then filter by phone field.
- **Currency fields** on custom entities require price + currency in the same PUT/POST. Standard entities (Opportunity) accept plain numbers.
- **Unconfigured currency code** — Setting a currency code not in the system's `currencyList` (check via `/api/v1/Settings`) produces `validCurrency` error even with both price+currency set. Workaround: omit price entirely and store the amount in `description`.
- **Auto-numbered names** — RealEstateRequest names are system-generated (R 000001...) and cannot be overridden via PUT.
- **403 on Query** — if you get 403, the API key may not have access to that entity. Try adding `?maxSize=1` to the URL first; some EspoCRM versions return 403 without a query parameter.
- **dateEnd required on Call** — EspoCRM requires both dateStart and dateEnd when creating Calls.
- **assignedUser required on Call** — Must include `assignedUserId` when creating Calls.
- **Phone validation** — phone numbers require `+976XXXXXXXX` format. Plain digits fail validation.
- **Lead name convention** — use phone number as `firstName`, district/location as `lastName` for quick identification.
- **No external web server** — this container cannot serve files externally. Only ports 32768/32769 are accessible. Files written to `/opt/data/www/` are not reachable from a browser. Use `MEDIA:` delivery (tar.gz archives) or EspoCRM Attachment entities to share files with the user.
