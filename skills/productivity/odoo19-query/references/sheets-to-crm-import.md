# Google Sheets → Odoo CRM Import

Import leads from Google Sheets into Odoo `crm.lead`. Used for Zangia.mn and similar Mongolian company lead imports.

## Prerequisites

- Google Workspace OAuth token at `/opt/data/google_token.json`
- Odoo 19 credentials in `/opt/data/.env` (ODOO19_URL, ODOO19_DB, ODOO19_USER, ODOO19_PASSWORD)
- Google Sheets API enabled in the GCP project

## Field Mapping (Sales Leads sheet)

| Google Sheet Column | crm.lead Field | Notes |
|---|---|---|
| Company Name | `partner_name` | |
| Phone / Contact | `phone` | |
| Job Title | `function` | |
| Address | `street` | |
| Email | `email_from` | |
| Company URL | `website` | |
| English Name, Salary, Job Level, Source, FB, etc. | `description` | Collected as text notes |

## Healthcare Leads Import (with Tagging)

The Healthcare Leads tab has **116 leads** with 24 columns. Import script at `/opt/data/scripts/import_healthcare_leads_to_crm.py`.

### Healthcare Headers (24 columns)

0: Date Collected, 1: Category, 2: Company Name, 3: Company ID, 4: Company Alias,
5: Over 50 Employees, 6: Employee Count Found, 7: Active Jobs Count, 8: Address Examples,
9: Job Titles, 10: Company URL, 11: Job Source URLs, 12: Employee Count Evidence,
13: Source, 14: Status / Notes, 15: HR Phone(s) from Job Posts, 16: Company Phone,
17: Email, 18: Email Source, 19: Facebook Page, 20: Website, 21: Staff Count,
22: Enrichment Status, 23: Last Enriched At

### Tagging Pattern

Create or reuse CRM tags via XML-RPC before importing:

```python
# Find or create tag
tag_ids = models.execute_kw(DB, uid, PASS, 'crm.tag', 'search', [[['name', '=', 'Эрүүл мэндийн байгууллага']]])
if not tag_ids:
    tag_id = models.execute_kw(DB, uid, PASS, 'crm.tag', 'create', [{'name': 'Эрүүл мэндийн байгууллага', 'color': 2}])

# Assign tag to lead via many2many tuple (4 = add)
vals = {
    'name': f'{company} - {job_title}',
    'partner_name': company_name,
    'tag_ids': [(4, tag_id)],
}
```

### CRM Tag Reference (as of May 2026)

| ID | Name | Leads |
|----|------|-------|
| 1 | Эрүүл мэндийн байгууллага | 116 healthcare |
| 2 | aithon2026 | 3 |
| 3 | smart-city | 3 |
| 4 | hackathon | 3 |

### Full Import Pattern

```python
from xmlrpc.client import ServerProxy
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 1. Read Google Sheet
creds = Credentials.from_authorized_user_file('/opt/data/google_token.json')
sheets = build('sheets', 'v4', credentials=creds)
rows = sheets.spreadsheets().values().get(
    spreadsheetId=SHEET_ID, range='TAB_NAME!A1:Z2000'
).execute().get('values', [])

# 2. Connect to Odoo
common = ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
models = ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# 3. Create leads in a loop
for lead in rows[1:]:  # skip header
    vals = {
        'name': f'{company_name} - {job_title}',
        'partner_name': company_name,
        'phone': phone,
        'email_from': email,
        'website': website or company_url,
        'function': job_titles,
        'street': address,
        'country_id': 152,
        'tag_ids': [(4, tag_id)],
        'description': '\n'.join(desc_parts) if desc_parts else '',
    }
    lead_id = models.execute_kw(DB, uid, PASS, 'crm.lead', 'create', [vals])
```

## Pitfalls

- `odoo_query.py` has NO create/update/delete — use direct XML-RPC instead
- `crm.lead.name` is **required** — Odoo returns `<Fault>` without it
- `crm.lead.name` should combine company + job title (e.g. "Monos Pharm - Эм зүйч"), not just company name alone
- Sheet names have spaces: "Sales Leads", "Healthcare Leads" — not "Sheet1"
- User workflow: Google Sheets first → Odoo CRM second
- Tag creation: `{'name': tag_name, 'color': 2}` — color 2 = green
- many2many tag tuple: `(4, id)` = ADD; `(6, 0, [ids])` = REPLACE ALL
- Run imports with `uv run` since system `pip` is unavailable:
  ```
  uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth-httplib2 python3 script.py
  ```
- All crm.lead defaults to Stage ID 1 ("New") — no need to set stage_id
- `country_id` for Mongolia = 152 (verify first with `search-read res.country --domain '[[\"code\", \"=\", \"MN\"]]'`)
- When combining multiple phone numbers, concatenate with ", " — Odoo handles char fields fine
