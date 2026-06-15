# Image / Business Card → CRM Lead Import

## When to Use

When the user sends an image (screenshot, photo of a business card, contact detail) and asks to save it to Odoo CRM. The workflow: OCR the image, validate existing records, create a `crm.lead`.

## Workflow

### 1. OCR the Image

If the current model lacks vision (e.g. deepseek-v4-flash), fall back to OCR.space:

```python
import base64, json, urllib.request, urllib.parse

with open('image.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

data = urllib.parse.urlencode({
    'base64Image': f'data:image/jpeg;base64,{img_b64}',
    'language': 'eng',  # Add 'mongolian' if Cyrillic text expected
    'OCREngine': '1',
}).encode()

req = urllib.request.Request(
    'https://api.ocr.space/parse/image',
    data=data,
    headers={'apikey': 'helloworld', 'Content-Type': 'application/x-www-form-urlencoded'}
)
result = json.loads(urllib.request.urlopen(req, timeout=30).read())
text = result['ParsedResults'][0]['ParsedText']
```

Preprocess with PIL (enlarge, grayscale, contrast, sharpen) if results are poor. See `ocr-and-documents` skill → `references/pil-ocr-preprocessing.md`.

### 2. Parse Fields

Typical business card fields and their `crm.lead` mapping:

| OCR pattern | crm.lead field | Notes |
|---|---|---|
| Name (e.g. "SH. DARAMBAZAR") | `contact_name` | Person's name |
| Job title (e.g. "Executive director") | `function` | Job Position |
| Company name | `partner_name` | Company field |
| Phone (e.g. "+976 99081691") | `phone` | Raw string |
| Email (e.g. "name@domain.mn") | `email_from` | Email |
| Street address | `street` | |
| City (e.g. "Ulaanbaatar") | `city` | |
| Website | `website` | |
| Country (e.g. "Mongolia") | `country_id` | ⚠️ **Verify live** — see Pitfalls |
| Opportunity title | `name` | **Required**. Build from context: `"{Company} - {Name}"` or `"{Name} - {Job Title}"` |

### 3. Check for Duplicates

```bash
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read res.partner --domain '[[\"name\", \"ilike\", \"NAME_PART\"]]' --fields id,name,email,phone --limit 10
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read res.partner --domain '[[\"phone\", \"ilike\", \"PHONE_LAST_DIGITS\"]]' --fields id,name,email,phone --limit 10
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read res.partner --domain '[[\"email\", \"ilike\", \"EMAIL_PART\"]]' --fields id,name,email,phone --limit 10
```

Also check `crm.lead`:
```bash
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read crm.lead --domain '[[\"contact_name\", \"ilike\", \"NAME_PART\"]]' --fields id,contact_name,phone,email_from --limit 10
```

### 4. Create the Lead (XML-RPC)

Writes require explicit user confirmation. Once confirmed:

```python
from xmlrpc.client import ServerProxy
import os

url = os.environ['ODOO19_URL']
db = os.environ['ODOO19_DB']
user = os.environ['ODOO19_USER']
password = os.environ['ODOO19_PASSWORD']

common = ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, user, password, {})
models = ServerProxy(f'{url}/xmlrpc/2/object')

lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [{
    'name': 'Darambazar - Executive director',   # Required: opportunity title
    'contact_name': 'SH. DARAMBAZAR',
    'function': 'Executive director',
    'phone': '+976 99081691',
    'email_from': 'darambazar@managewall.mn',
    'street': 'unroad-62, 1st khoroo, Sukhbaatar district',
    'city': 'Ulaanbaatar',
    'country_id': mn_id,  # Mongolia — verify live with res.country query first
}])
```

### 5. Verify

```bash
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py read crm.lead --ids [LEAD_ID] --fields name,contact_name,phone,email_from
```

### 6. Create Calendar Follow-up Reminder (optional)

After saving the lead, the user often wants a reminder to contact the person. Use the `google-workspace` skill to create a Calendar event:

```bash
cd /tmp && HERMES_HOME=/opt/data uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth-httplib2 python3 /opt/data/skills/productivity/google-workspace/scripts/google_api.py calendar create --summary "📞 Холбогдох - {NAME} ({PHONE})" --start 2026-06-08T10:00:00+08:00 --end 2026-06-08T10:15:00+08:00 --description "Lead #{LEAD_ID} (Odoo CRM). {Context from event where met}"
```

Then add a popup reminder (0 min = at event time, or 15/30/60 min before):

```python
# Patch reminders onto the created event
from google_api import build_service
event = build_service('calendar','v3').events().patch(
    calendarId='primary', eventId='EVENT_ID',
    body={'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 0}]}}
).execute()
```

## Pitfalls

- `crm.lead.name` is **required** — Odoo rejects with "Missing required value for the field 'Opportunity' (name)" if omitted
- OCR.space may mangle email addresses (e.g. "darambazar@managewall.mn" → "darambazar@m" + "n age'.valLmn") — you must manually reconstruct from context
- OCR.space may merge or split phone numbers on business cards (multiple numbers on one card can get garbled) — check each extracted digit sequence against the card layout
- Always check both `res.partner` and `crm.lead` for duplicates before creating
- **`country_id` is dynamic** — Mongolia's ID was 152 in earlier sessions but returned 146 in June 2026. Always verify before creating a lead:
  ```bash
  python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read res.country --domain '[[\"code\", \"=\", \"MN\"]]' --fields id
  ```
  Store the result as `mn_id` and use it in the create call, never hardcode it.
- `OCREngine=2` can fail (status 99) on business card images — default to `OCREngine=1`
- When the user mentions meeting context (event name, location), include it in the lead `description` field as HTML so it's visible in Odoo UI
