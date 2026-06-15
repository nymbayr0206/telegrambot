# Daily Morning Briefing

A concrete workflow that uses Odoo CRM queries (via `odoo-api-query` skill) plus cron status and session history to compile a structured daily work briefing for the user.

## When to Use

User asks: "what's my day looking like?", "today's tasks", "ажлын даалгавар гарга", "өнөөдрийн төлөвлөгөө", "what's on today?"

Works for both Mongolian and English. Designed for users with Odoo CRM, automated cron workflows, content pipelines, and sales coaching routines.

## Workflow

### Step 1: Understand date/time context

Note the current UTC time and convert to the user's timezone (typically Asia/Ulaanbaatar, UTC+8). Lead with this in your response so the user knows you have the right day.

### Step 2: Gather recent context (parallel)

Run these in parallel:
```
session_search()  # no query → recent sessions
cronjob(action='list')
memory -> read user profile
```

### Step 3: Query Odoo for recent activity (7-day window)

Use the `odoo-api-query` skill. The 7-day UTC window for ULAT (UTC+8) users:
- **Start:** `YYYY-MM-DDT16:00:00` (7 days ago at midnight ULAT)
- **End:** `YYYY-MM-DDT16:00:00` (today at midnight ULAT)

Query recent CRM leads, partners/contacts, and installed modules.

### Step 4: Compile structured briefing

**Format (proven for Mongolian users):**

1. **Header** — Date + Day + Time in ULAT
2. **Odoo results section** — ✅ emoji header, bullet-list format (Telegram has no tables):
   - Modules: count or "Шинээр суулгасан модуль байхгүй"
   - CRM Leads: count + `• **Company** — Name | Phone: 99XXXXXX`
   - Partners: note test vs real entries
3. **Cron job status** — Flag any jobs with `last_status = "error"`
4. **Ongoing projects table** — Brief status per project/brand
5. **Goal reminders** — OOS / 1M M&T, sales coaching schedule
6. **Numbered action menu** — Offer 5-8 specific choices

### Step 5: End with open call to action

"Юу хийхээ хэлээд өгөөч 👇" (Mongolian) or "What would you like to tackle?" (English).

## Formatting Rules

- Use emoji section headers (🔥, ✅, 📋) for visual scanning on Telegram
- Convert tables to bullet lists (Telegram has no table syntax)
- Number action items (1️⃣ 2️⃣ 3️⃣) for easy reference
- Lead with the freshest/most important data
- Flag cron errors prominently

## Extended Flow: Task Assignment to Team

When user asks "хүн тус бүр дээр даалгавар үүсгэх" (create tasks for each person):

### Resolve Ambiguity

Default to Odoo `project.task` if context is Odoo/My Office. Confirm in 1 sentence.

Mongolian phrasing hints:
- "үүсгэж болгох" → automation/process setup, not one-time
- "үүсгэж өгөх" or "өгөх" → one-time assignment

### Discover People

Query Odoo `res.users` or `hr.employee` for active team members.

### Create Tasks via Odoo XML-RPC

Use `terminal()` with `python3 << 'PYEOF'` (not `execute_code` — sandbox lacks Odoo env vars):

```python
import os, xmlrpc.client
url = os.environ.get('ODOO19_URL')
db = os.environ.get('ODOO19_DB')
user = os.environ.get('ODOO19_USER')
password = os.environ.get('ODOO19_PASSWORD')
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, user, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

for p in persons:
    task_id = models.execute_kw(db, uid, password, 'project.task', 'create', [{
        'name': p['task'],
        'user_ids': [(4, p['user_id'])],
        'project_id': PROJECT_ID,  # required
        'description': f"Assigned to {p['name']}",
    }])
```

**Required fields:** `name` (title), `project_id` (project). Discover available projects first by querying `project.project`.

### Set Up Automation

For recurring task creation, set up a Hermes cron job that runs daily and creates tasks via Odoo XML-RPC.

### Report Back

- **One-time:** Confirm task IDs, assignee names, and titles
- **Process:** "Өдөр бүр 09:00 цагт Odoo дээр ажилтан бүрт даалгавар автоматаар үүсгэгдэхээр тохирууллаа."

## Pitfalls

- **Odoo installs vs updates:** Modules installed during initial DB creation have `create_date: false`. Filter with `["create_date", "!=", false]`.
- **res.partner vs crm.lead:** `res.partner` is often test/system-generated; `crm.lead` is real prospect data.
- **No tables in Telegram:** Use bullet lists instead.
- **UTC conversion:** Odoo stores `create_date` in UTC. ULAT (UTC+8): today's data starts at `YYYY-MM-DD-1T16:00:00Z`.
- **CRM phone spaces:** Some values include spaces like "8888 0312" — don't strip them.
- **User is direct-execution oriented:** Don't over-explain. Present data and let them pick.
- **`execute_code` vs `terminal` for Odoo writes:** `execute_code` sandbox lacks Odoo env vars. Always use `terminal()`.
- **`project.task` requires `project_id`:** Unlike `crm.lead`, you can't create a task without specifying the project.
- **Recurring vs one-shot phrasing:** "үүсгэж болгох" ≈ automation setup; "үүсгэж өгөх" = one-time batch.
