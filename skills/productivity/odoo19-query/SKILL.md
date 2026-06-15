---
name: odoo19-query
description: "Use when querying the user's Odoo 19 instance for customers, invoices, sales orders, products, inventory, CRM, accounting, or operational reports via the Odoo XML-RPC API."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [odoo, odoo19, xmlrpc, erp, database, crm, accounting, inventory]
    related_skills: [google-workspace]
---

# Odoo 19 Query

## Overview

This skill connects to the user's Odoo 19 server through the Odoo XML-RPC API. Use it to answer natural-language business questions about records such as customers, companies, invoices, sales orders, products, stock, CRM leads, payments, and accounting entries.

The Odoo endpoint in this environment is an Odoo API/web server on port `8069`, not a direct PostgreSQL port. Direct PostgreSQL access on `5432` may be closed; prefer XML-RPC unless the user later provides a database host/port intended for PostgreSQL.

## Credentials

The helper script reads credentials from environment variables or from the Hermes `.env` file:

```env
ODOO19_URL=http://72.62.197.97:8069
ODOO19_DB=odoo19_admin
ODOO19_USER=...
ODOO19_PASSWORD=...
```

Security guidance:
- Prefer a dedicated read-only Odoo user or API key rather than an admin password.
- Do not print passwords or tokens in final responses.
- Do not store credentials inside this `SKILL.md` or any committed script.
- Treat writes/creates/updates/deletes as high-risk and ask for explicit confirmation first.

## Helper Script

Use the linked script:

```bash
python /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py ping
python /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py models --search invoice --limit 20
python /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py fields account.move --search amount --limit 50
python /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py count res.partner --domain '[]'
python /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read res.partner --domain '[["customer_rank", ">", 0]]' --fields name,email,phone --limit 10
```

All commands return JSON.

## Common Models

- Contacts/customers/vendors: `res.partner`
- Users: `res.users`
- Companies: `res.company`
- Sales orders: `sale.order`
- Sales order lines: `sale.order.line`
- Invoices/bills/journal entries: `account.move`
- Invoice lines: `account.move.line`
- Products: `product.product`, `product.template`
- Stock quants/on-hand inventory: `stock.quant`
- Stock moves: `stock.move`
- CRM leads/opportunities: `crm.lead`
- Payments: `account.payment`
- Installed modules: `ir.module.module`
- Module categories: `ir.module.category`

Odoo modules vary by installation. If a model is missing, use `models --search <keyword>` to discover installed model names.

## Query Workflow

1. Interpret the user's business question.
2. Identify the likely Odoo model(s).
3. Inspect fields when uncertain:
   ```bash
   python /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py fields MODEL --search keyword --limit 50
   ```
4. Run a read-only query with `count`, `search-read`, or `read`.
5. Summarize results in plain English and include key numbers.
6. If the user asks for a write operation, draft the intended change and ask for explicit confirmation before running it.

## Write Operations (Create / Update / Delete)

⚠️ **`odoo_query.py` is read-only** — it has no `create`/`write`/`update`/`delete` subcommands. Attempting `odoo_query.py create ...` fails with `argument cmd: invalid choice: 'create'`.

For write ops, use direct XML-RPC. Credentials are in `/opt/data/.env`:

```python
from xmlrpc.client import ServerProxy
import os
url = os.environ.get('ODOO19_URL')
db = os.environ.get('ODOO19_DB')
user = os.environ.get('ODOO19_USER')
password = os.environ.get('ODOO19_PASSWORD')
common = ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, user, password, {})
models = ServerProxy(f'{url}/xmlrpc/2/object')

# Create
record_id = models.execute_kw(db, uid, password, 'model.name', 'create', [{'field': 'value'}])

# Update
models.execute_kw(db, uid, password, 'model.name', 'write', [[record_id], {'field': 'new_value'}])

# Delete
models.execute_kw(db, uid, password, 'model.name', 'unlink', [[record_id]])
```

### CRM lead creation pitfalls

**Required field `name`:** `crm.lead` has a required field `name` (Opportunity title). `partner_name` (company) is separate. You **must** set `name` or Odoo rejects with `Missing required value for the field 'Opportunity' (name)`. Compose `name` as `"{contact_name} - {job_title}"` or `"{company} - {job_title}"`.

**Run XML-RPC write code via `terminal()`, NOT `execute_code`:** The `execute_code` sandbox does NOT load `.env` variables — `os.environ.get('ODOO19_URL')` returns `None`, causing `ServerProxy('None/xmlrpc/2/common')` to fail with `OSError: unsupported XML-RPC protocol`. Always use `terminal()` with a heredoc for raw XML-RPC operations — it inherits the shell environment including the `.env` file:

```python
# ❌ FAILS — execute_code sandbox has no .env
from xmlrpc.client import ServerProxy
url = os.environ.get('ODOO19_URL')  # None
```

```bash
# ✅ WORKS — terminal heredoc inherits the shell .env
python3 << 'PYEOF'
import os, xmlrpc.client
url = os.environ.get('ODOO19_URL')  # 'http://72.62.197.97:8069'
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, user, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [vals])
PYEOF
```

**Single-lead "quick add" pattern:** When the user provides one contact at a time (text, voice, image), create directly with `create()` — no need for Sheets import. The field map is the same as bulk import but with `contact_name` populated from the person's name and `function` for their job title. Example:

```python
vals = {
    'name': f"{contact_name} - {function}",
    'contact_name': contact_name,
    'partner_name': company,        # optional — infer from email domain or leave blank
    'function': job_title,
    'phone': phone,
    'email_from': email,
    'street': street, 'city': city, 'country_id': 146,  # Mongolia
}
lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [vals])
```

**Unknown contact name:** When the prospect's name isn't known (common with voice-intake leads), use a descriptive business-type identifier + phone number as `name` — e.g., `"Beauty Salon Owner - 99150560"`. Leave `contact_name` empty or omit it. Populate `description` with whatever IS known (business type, locations, how the contact was established, next steps) so the lead remains actionable despite the missing name.

For image-based extraction, see the `ocr-and-documents` skill's OCR.space reference — extract text from business card / contact screenshots before mapping to fields above.

**`country_id` is dynamic:** Mongolia's country_id was 152 in earlier sessions but is currently 146 (2026-06). Always verify live:
```bash
python3 odoo_query.py search-read res.country --domain '[["code", "=", "MN"]]' --fields id
```

Common `crm.lead` field mapping from external sources:
- `name` — Opportunity title (e.g. `"{Company} - {Job Title}"`)
- `partner_name` — Company name
- `contact_name` — Person name (optional)
- `phone` — Phone number
- `email_from` — Email
- `function` — Job position
- `street` / `city` / `country_id` — Address (Mongolia country_id = 146, but always verify live)
- `website` — Company URL
- `description` — HTML notes
- `tag_ids` — many2many tags; use `[(4, tag_id)]` to add, `[(6, 0, [id1, id2])]` to replace all

### Google Sheets → CRM import full example

See `scripts/import_sales_leads_to_crm.py` and `scripts/import_healthcare_to_crm.py` for complete working examples. The pattern:

1. Fetch Google Sheet data with Sheets API
2. Map columns to `crm.lead` fields
3. Create/reuse a `crm.tag` for categorization
4. Loop and `create()` each lead with `[(4, tag_id)]`
5. Run with `uv run --with google-api-python-client ... python3 script.py`

## Domain Syntax

Domains are JSON arrays using Odoo domain tuples/lists:

```json
[["field", "=", "value"]]
[["amount_total", ">", 100000], ["state", "=", "posted"]]
[["create_date", ">=", "2026-05-01 00:00:00"]]
```

### Shell JSON quoting pitfall

When passing `--domain` to the helper script via shell, the JSON **must** use double quotes for keys/values, and the outer shell string must use single quotes. This is required because JSON spec mandates `"double quotes"`:

```bash
# ✅ CORRECT — single quotes outside, double quotes inside
python odoo_query.py count res.partner --domain '[["customer_rank", ">", 0]]'

# ❌ WRONG — will fail with "Invalid JSON" error
python odoo_query.py count res.partner --domain "[["customer_rank", ">", 0]]"
python odoo_query.py count res.partner --domain [["customer_rank", ">", 0]]
```

**Watch out for triple nesting** — a common mistake is wrapping the domain in an extra layer of brackets inside the quotes. The script expects a JSON list of tuples `[["field", "op", value]]`, not `[[["field", "op", value]]]`:

```bash
# ✅ CORRECT
python odoo_query.py search-read ir.module.module --domain '[["state", "=", "installed"]]' --fields name,display_name --limit 10

# ❌ WRONG — triple-nested domain causes "Domain() invalid item in domain" error
python odoo_query.py search-read ir.module.module --domain '[[["state", "=", "installed"]]]' --fields name,display_name --limit 10
```

If you get a shell JSON parse error, the safest fallback is to use an empty domain `--domain '[]'` and filter in the `--limit` / `--order` if you already know your target record. For complex filters, write a small Python script using the helper's `_execute_kw` function (see `references/project-task-reporting.md` for a worked example).

Useful operators:
- `=` / `!=`
- `>` / `>=` / `<` / `<=`
- `ilike` for case-insensitive text search
- `in` for membership

## Date/Timezone Notes

Odoo often stores datetimes in UTC strings. When the user says "today" or "tomorrow", use their working timezone if known. The user has previously indicated Ulaanbaatar time (`Asia/Ulaanbaatar`, UTC+8). Convert reporting windows carefully.

## Common Questions and Starting Points

Additional project/task reporting recipe: see `references/project-task-reporting.md` for active project counts, project names, and tasks grouped by project, including a known access-rights pitfall around `project.project.stage_id`.

User access/role audits: see `references/user-access-role-audit.md` for exporting active users with explicit and inherited access roles, employee position names, departments, managers, and smoke/test-account flags.

### Odoo HR as organizational structure validator

When the user needs to validate position names, department names, or role titles from an external document (work report, contract, org chart, lawyer feedback) against the live Odoo HR data, see `references/odoo-hr-org-validator.md`. This covers which models to query (`hr.job`, `hr.department`, `hr.employee`, `res.groups`), real department structure for this Odoo instance, procurement workflow roles, and pitfalls.

### User access roles and positions

When the user asks for "all roles that have access," "actual list of users/permissions," or "position names and what they can access," treat it as an Odoo user access audit. Use `res.users` joined conceptually to `res.groups` and `hr.employee`:

```bash
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read res.users --domain '[["active", "=", true], ["share", "=", false]]' --fields id,name,login,group_ids,all_group_ids,groups_count,employee_id --limit 10000 --order 'name asc'
```

Important: `group_ids` are explicit assignments; `all_group_ids` includes inherited/implied groups and is better for effective access. Read the referenced `res.groups` IDs using fields `id,name,full_name,display_name` and read linked `hr.employee` records for `job_title`, `job_id`, `department_id`, and `parent_id`. For large results, export CSV and send the file instead of pasting the full list into chat. Include a short summary with total active internal users, obvious smoke/test accounts, top roles, top positions, and top departments.

### Projects and tasks

```bash
python /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py count project.project --domain '[["active", "=", true]]'
python /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read project.task --domain '[["project_id", "!=", false]]' --fields name,project_id --limit 100
```

For grouped output by active project, use the reference file above.

### "Өнөөдөр шинэ ажил орсон уу?" / today's new work check

When the user asks in Mongolian whether a new "ажил" was entered in Odoo today, interpret broadly before answering. Use the user's Asia/Ulaanbaatar day window and convert to UTC for Odoo `create_date` filters. Check `project.task` first, but also inspect common/custom work models seen in this Odoo instance:

```bash
# Example for 2026-05-25 Asia/Ulaanbaatar => UTC 2026-05-24 16:00:00 to 2026-05-25 16:00:00
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read project.task --domain '[["create_date", ">=", "YYYY-MM-DD-1 16:00:00"], ["create_date", "<", "YYYY-MM-DD 16:00:00"]]' --fields id,name,project_id,stage_id,user_ids,create_date,date_deadline,priority --limit 50 --order 'create_date desc'
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read shared.work.department.task --domain '[["create_date", ">=", "START_UTC"], ["create_date", "<", "END_UTC"]]' --fields id,display_name,shared_work_id,department_id,assigned_employee_ids,create_date,write_date --limit 50 --order 'create_date desc'
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read ops.task.report --domain '[["create_date", ">=", "START_UTC"], ["create_date", "<", "END_UTC"]]' --fields id,display_name,task_id,state,reporter_employee_id,report_datetime,create_date,write_date --limit 50 --order 'create_date desc'
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read project.project --domain '[["create_date", ">=", "START_UTC"], ["create_date", "<", "END_UTC"]]' --fields id,name,user_id,create_date --limit 50 --order 'create_date desc'
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read hr.job --domain '[["create_date", ">=", "START_UTC"], ["create_date", "<", "END_UTC"]]' --fields id,name,department_id,no_of_employee,no_of_recruitment,create_date,write_date --limit 50 --order 'create_date desc'
```

Pitfalls:
- Use `python3` if `python` is unavailable; do not record this as a durable environment limitation.
- `crm.lead` and `sale.order` may not be installed in this Odoo database; if queried and missing, report that they are not available rather than treating it as a failed Odoo connection.
- `project.project.stage_id` can trigger access-right errors; omit `stage_id` from quick project checks unless explicitly needed.
- Final answer should be short in Mongolian: state the local date window, counts by checked model, and whether any new work was found.

### "What's new" monitoring (Mongolian: шинэ юу орсон бэ?)

When the user asks what's new across the system in the last N days (e.g., "өнгөрсөн 7 хоногт шинэ хэдэн сежм орж ирсэн бэ?", "утас нэрийг нь гарга"), check multiple models in parallel for a consolidated answer:

```bash
# Modules recently added/updated
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read ir.module.module --domain '[["state", "=", "installed"], ["write_date", ">=", "START_UTC"]]' --fields name,display_name,write_date --limit 20 --order 'write_date desc'

# CRM leads in the last N days (most common source of "new customers")
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read crm.lead --domain '[["create_date", ">=", "START_UTC"]]' --fields name,contact_name,partner_name,phone,email_from,create_date --limit 50 --order 'create_date desc'

# New contacts/partners
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read res.partner --domain '[["create_date", ">=", "START_UTC"]]' --fields name,phone,email,create_date --limit 50 --order 'create_date desc'
```

Workflow:
1. Convert user's time window to UTC for Odoo's `create_date`/`write_date` filters.
2. Always check `ir.module.module` (new/updated modules), `crm.lead` (new leads), and `res.partner` (new contacts).
3. For Mongolian users: if asked "утас нэрийг гарга", they want CRM leads with phone numbers — check `crm.lead` with `partner_name, contact_name, phone` fields.
4. Present results grouped: modules first (if any), then leads/contacts with name + phone.
5. Answer in Mongolian: state the time window, count per model, and if nothing new — say so directly.

### User access / roles / positions

For audit-style exports of Odoo users, explicit/effective access roles, and HR position data, use `references/user-access-role-export.md`.

### Customers

```bash
python scripts/odoo_query.py count res.partner --domain '[["customer_rank", ">", 0]]'
python scripts/odoo_query.py search-read res.partner --domain '[["name", "ilike", "BAT"]]' --fields name,email,phone,customer_rank --limit 20
```

### Unpaid customer invoices

```bash
python scripts/odoo_query.py search-read account.move --domain '[["move_type", "=", "out_invoice"], ["payment_state", "!=", "paid"], ["state", "=", "posted"]]' --fields name,partner_id,invoice_date,amount_total,amount_residual,payment_state --limit 20
```

### Sales orders

```bash
python scripts/odoo_query.py search-read sale.order --domain '[]' --fields name,partner_id,date_order,amount_total,state --limit 20 --order 'date_order desc'
```

### Installed modules (ir.module.module)

Query which modules are installed and when they were added. Pre-installed (stock Odoo) modules have `create_date = false`; custom/added-later modules have a real timestamp:

```bash
# Total installed modules count
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py count ir.module.module --domain '[["state", "=", "installed"]]'

# Most recently added custom modules (has create_date)
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read ir.module.module --domain '[["state", "=", "installed"], ["create_date", "!=", false]]' --fields name,display_name,create_date,write_date --limit 20 --order 'create_date desc'

# Modules updated recently (write_date)
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read ir.module.module --domain '[["state", "=", "installed"], ["write_date", "!=", false]]' --fields name,display_name,create_date,write_date --limit 20 --order 'write_date desc'
```

Pitfalls:
- `create_date` is `false` (JSON null) for modules installed during initial DB creation — only custom modules added later have a timestamp.
- `write_date` is set when module data is updated (upgrades, config changes), not just on initial install.

### Municipal garbage truck fuel reports

When the user asks about "түлшний мэдээлэл", "шатахуун", or when fuel data was last updated, use the custom model `municipal.garbage.fuel.report`.

Discover/check fields if needed:
```bash
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py fields municipal.garbage.fuel.report --search fuel --limit 50
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py fields municipal.garbage.fuel.report --search date --limit 50
```

Known useful fields:
- `report_date` — report date
- `vehicle_id`, `vehicle_license_plate`, `vehicle_type_id` — vehicle identifiers
- `fuel_liters` — consumed fuel amount
- `fuel_type` — fuel type, often blank in current records
- `state` — e.g. `success` / `failed`
- `create_date`, `create_uid`, `write_date`, `write_uid` — audit timestamps/users

Latest update query:
```bash
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read municipal.garbage.fuel.report \
  --domain '[]' \
  --fields id,display_name,report_date,vehicle_id,vehicle_license_plate,vehicle_type_id,fuel_type,fuel_liters,state,create_date,create_uid,write_date,write_uid \
  --limit 10 \
  --order 'write_date desc'
```

For summaries, report both Odoo UTC `write_date` and Asia/Ulaanbaatar local time, plus counts by latest `report_date` and `state` when useful:
```bash
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py count municipal.garbage.fuel.report --domain '[["report_date", "=", "YYYY-MM-DD"]]'
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py count municipal.garbage.fuel.report --domain '[["report_date", "=", "YYYY-MM-DD"], ["state", "=", "success"]]'
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py count municipal.garbage.fuel.report --domain '[["report_date", "=", "YYYY-MM-DD"], ["state", "=", "failed"]]'
```

Pitfall: this model has no `driver_id`; do not include it in `--fields` unless field discovery shows it exists.

### Products / inventory

```bash
python scripts/odoo_query.py search-read product.product --domain '[]' --fields display_name,default_code,list_price,qty_available --limit 20
```

If `qty_available` is unavailable or unreliable, inspect `stock.quant`:

```bash
python scripts/odoo_query.py search-read stock.quant --domain '[["quantity", ">", 0]]' --fields product_id,location_id,quantity,reserved_quantity --limit 20
```

## Email Marketing (Mass Mailing) via XML-RPC

This Odoo instance has the `mailing.mailing` (Mass Mailing) module installed. It uses `mailing.contact` (model ID 970) as the recipients model.

### Checking if Email Marketing is available

```bash
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py models --search mailing --limit 20
```

Key models: `mailing.mailing` (campaign), `mailing.list` (recipient lists), `mailing.contact` (individual contacts).

### Mailing list discovery

```bash
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read mailing.list --domain '[]' --fields id,name,contact_count --limit 20
```

### Creating a mailing (email campaign) via XML-RPC

```python
from xmlrpc.client import ServerProxy

models.execute_kw(DB, uid, PASS, 'mailing.mailing', 'create', [{
    'name': 'Campaign Name (internal)',
    'subject': 'Email Subject Line',
    'body_html': '<div>Full HTML email body</div>',
    'email_from': 'Your Name <email@domain.mn>',
    'contact_list_ids': [(4, list_id)],  # many2many add
    'mailing_model_id': 970,            # mailing.contact
    'mailing_type': 'mail',
    'reply_to_mode': 'new',
    'state': 'draft',
}])
```

### Pitfalls

- `mailing_model_id` is **required** — set to 970 (mailing.contact). The `odoo_query.py` `fields` command shows `required: true`.
- `email_from` is **required** — Odoo admin user has no email set (`email: false`), so must be explicitly provided.
- `subject` is **required** — Odoo rejects with `Missing required value`.
- State: `'draft'` is the only valid initial state.
- After creation, user must go to Odoo UI → Marketing → Email Marketing to test/schedule/send.
- The `body_html` field accepts inline styles and full HTML — Odoo renders it as-is.

### Known mailing lists (as of May 2026)

| ID | Name | Contacts |
|----|------|----------|
| 1 | Newsletter | 1 |
| 2 | healthcare | 0 (needs importing) |

## Verification Checklist

- [ ] `ping` succeeds before using the skill.
- [ ] Use read-only operations by default.
- [ ] Inspect fields/models when uncertain.
- [ ] Do not expose credentials.
- [ ] Ask for confirmation before any write/create/update/delete action.
- [ ] Summaries include model, filters, time window, and notable assumptions.

## Related Reference Files

- `references/whats-new-monitoring.md` — Consolidated monitoring of new modules, leads, and contacts with time-window queries (as of June 2026)
- `references/sheets-to-crm-import.md` — Import leads from Google Sheets into Odoo CRM (XML-RPC create pattern, field mapping, pitfall notes)
- `scripts/import_sales_leads_to_crm.py` — Full import script for the Sales Leads tab (7 leads)
- `scripts/import_healthcare_to_crm.py` — Full import script for Healthcare Leads tab with tagging (116 leads)
- `references/project-task-reporting.md` — Active project counts and grouped task reports
- `references/user-access-role-export.md` — Full user access/roles/positions export
- `references/user-access-role-audit.md` — Odoo user access audit with res.users, groups, and HR data
- `references/voice-chat-lead-to-crm-calendar.md` — Quick lead intake from voice/chat to CRM lead + Calendar events with cross-references
