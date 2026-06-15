# Quick Lead Intake: Voice/Chat → CRM + Calendar

Pattern for rapidly capturing prospect info from voice messages or chat into Odoo CRM leads with associated Google Calendar follow-up events, and end-of-session tally to the Pinnacle Playbook II coaching scoreboard.

## Workflow

1. **Extract fields** from user input (voice transcript, text):
   - Phone number (primary key when name unknown)
   - Contact name (if mentioned; leave empty if unknown)
   - Company / organization name (e.g., "Трейд ХХК", "Ханбүргэдэй")
   - Position / role (e.g., "Ахлах", "Finance person", "эзэн")
   - Business type / description (e.g., "beauty aesthetics salon")
   - Locations (e.g., "MPM Plaza and Aison" — multiple branches)
   - Meeting intent (e.g., "talk about Postly", "meet Monday afternoon")
   - Confirmation status: confirmed, tentative ("need to confirm on Monday"), or TBD

2. **Create Odoo CRM lead** via XML-RPC `terminal()` heredoc:

   ```python
   vals = {
       'name': f"{company_or_person} - {role}",        # e.g. "Трейд ХХК - Ахлах"
       'contact_name': person_name,                     # individual name if known
       'partner_name': company,                         # company name
       'phone': phone,
       'function': job_position,                        # e.g. "Finance person / Финанс"
       'street': primary_location,
       'city': 'Улаанбаатар',
       'country_id': 146,                               # verify live
       'description': (
           f'<p>{business_type}. {extra_details}</p>'
           f'<p>Холбогдсон: {how_connected}</p>'
           f'<p>Хариу: {response_summary}</p>'
           f'<p>Дараагийн алхам: {next_steps}</p>'
       ),
   }
   ```

### Lead naming conventions

| Input available | `name` value | `contact_name` | `partner_name` |
|---|---|---|---|
| Company + role only | `"Ханбүргэдэй - Finance"` | `''` (omit) | `"Ханбүргэдэй"` |
| Person + company + role | `"Мөнх-Эрдэнэ - Трейд ХХК Ахлах"` | `"Мөнх-Эрдэнэ"` | `"Трейд ХХК"` |
| Business type + phone only | `"Beauty Salon Owner - 99150560"` | `''` (omit) | `''` (omit) |

3. **Create Calendar events** for follow-up:

### Pattern A: Confirmed meeting
- One event at the agreed time
- Popup reminder 10-15 min before

### Pattern B: Tentative meeting ("need to confirm on Monday")
Create **two** events:

   1. **Confirmation call** — the morning of the confirmation day (09:00-09:15, popup 10 min before)
      - Summary: `📞 {Name} ({Company}) руу залгах — баталгаажуулах {phone} [Lead #{ID}]`
   2. **Tentative meeting** — the proposed meeting slot, explicitly marked unconfirmed
      - Summary: `🤝 Уулзалт — {Name} ({Company}) {phone} [Lead #{ID}] ⏳ Баталгаажаагүй`
      - Description includes note: `⚠️ БАТАЛГААЖААГҮЙ — {confirmation_day} өглөө залгаж баталгаажуулах шаардлагатай`

### Pattern C: Needs scheduling ("contacted, he was busy")
- One **call-back event** on the agreed follow-up day
- Summary: `📞 {Name} руу залгах — уулзалт товлох {phone} [Lead #{ID}]`
- Popup reminder 10 min before

4. **Cross-reference**: Use `[Lead #{ID}]` in every Calendar event summary and description so either system ties back to the other. The lead ID comes from the `create()` return value.

## End-of-Day Summary → Coaching Scoreboard

After a multi-lead session (or when the user asks "how many leads did I get today? record to my coach"), tally and record to the **Pinnacle Playbook II Daily Scoreboard** Google Sheet.

### Data sources for the tally

1. **Odoo CRM** — count leads created in today's ULAT window:
   ```python
   # ULAT 00:00 = UTC 16:00 previous day
   today_start = '2026-06-05 16:00:00'
   today_end   = '2026-06-06 16:00:00'
   count = models.execute_kw(db, uid, password, 'crm.lead', 'search_count',
       [[['create_date', '>=', today_start], ['create_date', '<', today_end]]])
   leads = models.execute_kw(db, uid, password, 'crm.lead', 'search_read',
       [[['create_date', '>=', today_start], ['create_date', '<', today_end]]],
       {'fields': ['id', 'name', 'partner_name', 'phone', 'create_date'], 'order': 'create_date desc'})
   ```

2. **Calendar events** — count confirmation calls + meetings created (from today's session, even if dated in the future)

### Scoreboard sheet structure

Sheet ID: `1vjrtCmkoQlCV7CdL44ucuh0MbT_UFU2MxBel4km9RnQ`, tab `Daily Scoreboard`:

| Col | Header | Typical value |
|:---|:---|---:|
| A | Date | `2026-06-06` |
| B | Day | `Saturday` |
| C | Week | `Week 23` |
| D | Q1-New Leads | # leads added to CRM |
| E | Q2-Calls/Messages | # calls made today |
| F | Q3-Conversations | # conversations had |
| G | Q4-Appointments Booked | # meetings booked (tentative + confirmed) |
| H | Q5-Follow-ups Done | # follow-up actions (CRM saves, calendar events) |
| I | Q6-Proposals/Demos | 0 |
| J | Q7-New Clients | 0 |
| K | Q8-Referrals Requested | 0 |
| L | Q9-Revenue (₮) | 0 |
| M | Daily Score | (auto-calc or blank) |
| N | Response Status | `Logged 📝` |
| O | Coach Notes | Free-text summary like `6/6: 5 leads CRM, 3 bookings, follow-ups set` |

Append a row:
```python
service.spreadsheets().values().append(
    spreadsheetId=SHEET_ID,
    range='Daily Scoreboard!A:O',
    valueInputOption='USER_ENTERED',
    insertDataOption='INSERT_ROWS',
    body={'values': [new_row]}
).execute()
```

### Multi-lead batch session pattern

When the user provides 3+ leads back-to-back (same session):
1. Process each lead independently — CRM create first (capture `lead_id` from return value), then Calendar events per lead
2. Use the real `lead_id` in Calendar summaries via `[Lead #{ID}]` — never guess
3. At the end, tally all leads from Odoo `search_count` using today's UTC window, and offer to record to the coaching scoreboard
4. Check if today's row already exists in the sheet (search column A for today's date) before appending

## Example 1: Unknown name, business type only (2026-06-06)

```python
vals = {
    'name': 'Beauty Salon Owner - 99150560',
    'phone': '99150560',
    'street': 'MPM Plaza',
    'city': 'Улаанбаатар',
    'country_id': 146,
    'description': (
        '<p>Beauty aesthetics салоны эзэн. 2 салбартай:</p>'
        '<ul><li>MPM Plaza</li><li>Aison</li></ul>'
        '<p>Postly prospect. Даваа гарагт уулзалт товлохоор ярилцсан.</p>'
        '<p>Өглөө залгаж цаг/газар баталгаажуулах.</p>'
    ),
}
```

Calendar:
- 09:00 📞 Баталгаажуулалт — Beauty salon owner руу залгах (99150560) [Lead #139]
- 14:00 🤝 Уулзалт — Beauty salon owner (99150560) ⏳ Цаг TBD [Lead #139]

## Example 2: Company + position, needs Monday confirmation (2026-06-06)

```python
vals = {
    'name': 'Мөнх-Эрдэнэ - Трейд ХХК Ахлах',
    'contact_name': 'Мөнх-Эрдэнэ',
    'partner_name': 'Трейд ХХК',
    'phone': '94497502',
    'function': 'Ахлах / Senior',
    'city': 'Улаанбаатар',
    'country_id': 146,
    'description': (
        '<p>2026-06-06 (Бямба): Холбогдож, Gentek AI agent-ийн талаар танилцуулсан.</p>'
        '<p>Хариу: Даваа гарагт баталгаажуулна. Маргааш (мягмар) өглөө 09:00 цагт уулзахаар магадгүй.</p>'
        '<p>Дараагийн алхам: Даваа гарагийн өглөө залгаж баталгаажуулах.</p>'
        '<p>Уулзалт: Мягмар 09:00 (баталгаажаагүй)</p>'
    ),
}
```

Calendar (dual-event for tentative meeting):
1. Mon 09:00 📞 Мөнх-Эрдэнэ (Трейд ХХК) руу залгах — баталгаажуулах 94497502 [Lead #142] 🔔 10min
2. Tue 09:00 🤝 Уулзалт — Мөнх-Эрдэнэ (Трейд ХХК) 94497502 [Lead #142] ⏳ Баталгаажаагүй

## Calendar event creation (one-shot with reminders)

Use the Hermes venv Python for Google API calls:

```python
import sys
sys.path.insert(0, '/opt/data/skills/productivity/google-workspace/scripts')
from google_api import build_service

service = build_service('calendar', 'v3')

# Create event
created = service.events().insert(calendarId='primary', body={
    'summary': '📞 ... руу залгах [Lead #{lead_id}]',
    'description': '...',
    'start': {'dateTime': '2026-06-08T09:00:00', 'timeZone': 'Asia/Ulaanbaatar'},
    'end':   {'dateTime': '2026-06-08T09:15:00', 'timeZone': 'Asia/Ulaanbaatar'},
}).execute()

# Patch popup reminder
service.events().patch(
    calendarId='primary', eventId=created['id'],
    body={
        'reminders': {
            'useDefault': False,
            'overrides': [{'method': 'popup', 'minutes': 10}]
        }
    }
).execute()
```

## When to use

- User sends voice/chat with prospect info and says "save to CRM"
- User mentions a phone number and some details (name, company, role, or business type)
- Meeting is tentative — schedule a morning confirmation call before the actual meeting
- User provides company + position names — use them to build a richer lead name: `"{Person} - {Company} {Role}"` or `"{Company} - {Role}"` if person name unknown
- User asks "how many leads did I get today? record to my coach" — tally CRM leads and Calendar events, then log to the Pinnacle Playbook II Daily Scoreboard
