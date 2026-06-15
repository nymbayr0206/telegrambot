# What's New Monitoring — Session Reference

This file captures Odoo instance state discovered during the June 2026 monitoring sessions.

## Active modules summary

- **Total installed modules**: 110 (as of 2026-06-09)
- **Custom modules added after initial install** (have `create_date`): 10

### Recently added custom modules (by install date, descending)

| Module | Display Name | Created | Last Updated |
|--------|-------------|---------|-------------|
| municipal_environment_services | Хот тохижилтын ногоон байгууламж, тохижилтын үйлчилгээ | 2026-05-02 | 2026-05-24 |
| municipal_public_services | Хот тохижилтын гомдол, dashboard, audit | 2026-05-01 | 2026-06-05 |
| municipal_repair_workflow | Хот тохижилтын засвар, агуулахын холбоос | 2026-05-01 | 2026-06-05 |
| municipal_core | Хот тохижилтын үндсэн модуль | 2026-05-01 | 2026-05-24 |
| tengertech_push_notifications | Tengertech Push Notifications | 2026-04-26 | 2026-05-24 |
| hr_custom_mn | Mongolian HR Management | 2026-04-25 | 2026-06-05 |
| municipal_procurement_workflow | Municipal Procurement Workflow | 2026-04-22 | 2026-05-15 |
| ops_people_registry | Хотын ажиллагаа: Ажилтан ба эрхийн бүртгэл | 2026-04-22 | 2026-05-04 |
| ops_work_unit | Ажлын хэмжих нэгжийн legacy compatibility | 2026-04-22 | 2026-05-29 |
| hr_discipline_transfer_mn | Сахилга ба шилжилт хөдөлгөөн | 2026-04-21 | 2026-05-04 |

## CRM leads created in last 7 days (June 2-9, 2026)

5 leads entered on June 6:

| # | Name | Company | Phone | Email |
|---|------|---------|-------|-------|
| 1 | Munkhgerel G. - Sales Manager | METRO EXPRESS | 99013215 | sales3@metro-express.mn |
| 2 | Beauty Salon Owner - 99150560 | — | 99150560 | — |
| 3 | Ханбүргэдэй - Finance | Ханбүргэдэй | 8888 0312 | — |
| 4 | Мөнх-Эрдэнэ - Трейд ХХК Ахлах | Трейд ХХК | 94497502 | — |
| 5 | Bolor Hot Springs Hotel - Manager/SMM | Bolor Hot Springs Hotel | 99985887 | — |

## Contacts created in last 7 days

3 partners created (all test records):
- CODEx HR TRANSFER SMOKE 1780897949462 (2026-06-08, no phone)
- test1 test1 (2026-06-03, no phone)
- test test (2026-06-03, phone: 99889988)

## Monitoring query patterns

All use UTC timestamps. Convert user's local time (Asia/Ulaanbaatar = UTC+8) to UTC for Odoo filters.

```bash
# Modules updated in a window
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read ir.module.module \
  --domain '[["state", "=", "installed"], ["write_date", ">=", "2026-06-02 04:11:00"]]' \
  --fields name,display_name,write_date,create_date --limit 20 --order 'write_date desc'

# CRM leads in a window
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read crm.lead \
  --domain '[["create_date", ">=", "2026-06-02 04:11:00"]]' \
  --fields name,contact_name,partner_name,phone,email_from,create_date --limit 50 --order 'create_date desc'

# New contacts in a window
python3 /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read res.partner \
  --domain '[["create_date", ">=", "2026-06-02 04:11:00"]]' \
  --fields name,phone,email,create_date --limit 50 --order 'create_date desc'
```
