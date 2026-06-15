---
name: odoo-api-query
description: "Use when connecting Hermes to an Odoo instance for safe natural-language querying, reporting, and controlled record operations through Odoo XML-RPC/JSON-RPC instead of direct PostgreSQL."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [odoo, erp, xml-rpc, database-query, reporting, productivity]
    related_skills: [google-workspace]
---

# Odoo API Query

## Overview

Use this skill when a user wants Hermes to answer questions from an Odoo database or create an Odoo-specific assistant. Prefer Odoo's external API (XML-RPC or JSON-RPC) over direct PostgreSQL access: Odoo enforces model permissions, computed fields, record rules, currencies, workflows, and business semantics that raw SQL bypasses.

The common user request shape is: “connect to my Odoo database so I can ask questions naturally.” Build a thin, reusable query helper that authenticates once, introspects models/fields, runs read-only queries by default, and summarizes results in plain language.

## When to Use

- User provides an Odoo URL, database name, username/password, or API key.
- User asks natural-language business questions about Odoo: sales, invoices, customers, inventory, purchases, CRM, accounting, employees, etc.
- User asks for a custom Hermes skill/tool for an Odoo instance.
- User says “PostgreSQL” but provides Odoo web port `8069`; treat that as Odoo API access, not direct DB access.

Do not use for unrelated PostgreSQL-only apps that do not run Odoo.

## Connection Pattern

Odoo web/API usually listens on port `8069`. Direct PostgreSQL usually listens on `5432`, but it is often not exposed and should not be the first choice.

Store credentials in environment variables or a secret store, never in SKILL.md:

```env
ODOO_URL=http://host:8069
ODOO_DB=database_name
ODOO_USER=user@example.com
ODOO_PASSWORD=api_key_or_password
```

Basic XML-RPC probe:

```python
import os, xmlrpc.client
url = os.environ['ODOO_URL'].rstrip('/')
db = os.environ['ODOO_DB']
user = os.environ['ODOO_USER']
password = os.environ['ODOO_PASSWORD']

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
version = common.version()
uid = common.authenticate(db, user, password, {})
assert uid, 'Odoo authentication failed'
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
```

Read example:

```python
partners = models.execute_kw(
    db, uid, password,
    'res.partner', 'search_read',
    [[['customer_rank', '>', 0]]],
    {'fields': ['name', 'email', 'phone'], 'limit': 10}
)
```

## Natural-Language Query Workflow

1. Clarify the business question only if required. If obvious, proceed read-only.
2. Map the question to likely Odoo models:
   - Customers/contacts: `res.partner`
   - Sales orders: `sale.order`, `sale.order.line`
   - Invoices/bills: `account.move`, `account.move.line`
   - Products/inventory: `product.product`, `product.template`, `stock.quant`, `stock.move`
   - CRM: `crm.lead`
   - Purchases: `purchase.order`, `purchase.order.line`
3. Introspect fields before guessing field names:

```python
fields = models.execute_kw(db, uid, password, 'sale.order', 'fields_get', [], {'attributes': ['string', 'type', 'relation']})
```

4. Use `search_count`, `search_read`, or `read_group` for reporting. Prefer `read_group` for aggregates.
5. Return both a concise answer and, when useful, the model/domain used.
6. For write/create/update/delete/workflow actions, show the exact proposed change and ask for confirmation first.

## Common Query Recipes

Count records:

```python
count = models.execute_kw(db, uid, password, 'res.partner', 'search_count', [[['customer_rank', '>', 0]]])
```

Recent records:

```python
orders = models.execute_kw(
    db, uid, password, 'sale.order', 'search_read',
    [[['date_order', '>=', '2026-01-01']]],
    {'fields': ['name', 'partner_id', 'amount_total', 'state', 'date_order'], 'order': 'date_order desc', 'limit': 20}
)
```

Aggregate totals:

```python
rows = models.execute_kw(
    db, uid, password, 'sale.order', 'read_group',
    [[['state', 'in', ['sale', 'done']]], ['amount_total:sum'], ['currency_id']]
)
```

## Safety Rules

- Prefer read-only access credentials. If the user gives admin credentials, recommend creating a dedicated read-only/API user.
- Never save passwords, API keys, or session tokens in memory or skill text.
- Never run destructive operations (`unlink`, cancellations, posting accounting entries, stock adjustments, mass updates) without explicit confirmation.
- Do not bypass Odoo permissions by using raw PostgreSQL unless the user specifically needs low-level diagnostics and understands the risk.
- Be careful with personal data in CRM/contacts. Return only the fields needed for the question.

## Verification Checklist

- [ ] Confirm the Odoo URL and port are reachable.
- [ ] Call `/xmlrpc/2/common` `version()` to verify it is Odoo and identify the server series.
- [ ] Authenticate and record only non-secret facts such as version and uid.
- [ ] For a new query helper, test a harmless `search_count` on a common model like `res.partner`.
- [ ] For natural-language answers, include enough context for the user to trust the result: date range, model, filters, and limits.

## References

- `references/odoo19-session-pattern.md` — concrete Odoo 19 session authentication patterns from a live instance
- `references/daily-morning-briefing.md` — structured daily briefing workflow using Odoo CRM queries + cron status + session history, compiled into a numbered action menu. Covers task assignment patterns (хүн бүрт даалгавар), team discovery, project.task creation, and cron automation setup.
