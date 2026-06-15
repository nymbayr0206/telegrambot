# Odoo HR as Organizational Structure Validator

Use this when you need to validate position names, department names, or role titles from an **external document** (work completion report, contract, org chart, etc.) against the live Odoo 19 HR master data.

The user's Odoo 19 instance is the **source of truth** for organizational structure. When a lawyer or counterparty says a role name or department name is wrong, query Odoo HR to find the real name.

## Which models to query

| Model | Purpose | Key fields |
|-------|---------|------------|
| `hr.job` | All defined job positions (ажлын байр) | `id`, `name`, `department_id`, `no_of_employee` |
| `hr.department` | All departments (газар/хэлтэс) | `id`, `name`, `manager_id` (name only, not tuple) |
| `hr.employee` | Individual employees with their assigned job & dept | `id`, `name`, `job_title`, `job_id`, `department_id`, `parent_id` (manager) |
| `res.groups` | User groups / access roles (procurement, etc.) | `id`, `name`, `full_name` |

## Typical validation workflow

1. **User says "the lawyer says role X is wrong"** → query `hr.job` for all positions. If X is absent from the job list, the lawyer is correct.
2. **User says "there should be role Y instead"** → search `hr.job` with `[['name', 'ilike', 'Y части слова']]` to find the official title.
3. **Department head names needed** → query `hr.department` — each department has a `manager_id` that contains the department head's name.
4. **User's own position for document title** → query `hr.employee` filtered by user's Odoo `id` or name, get `job_title`.

## Practical example: procurement workflow roles in Odoo

When a report says "Худалдан авалтын менежер" (purchasing manager) but the lawyer says it doesn't exist:

Query `res.groups` filtering by `full_name` containing "Procurement". This Odoo instance's procurement groups are:

```
Хот тохижилтын засвар / Procurement / Purchase Manager
Хот тохижилтын засвар / Procurement / Storekeeper
Хот тохижилтын засвар / Procurement / Finance User
Хот тохижилтын засвар / Procurement / Legal User
Хот тохижилтын засвар / Procurement / CEO
Хот тохижилтын засвар / Procurement / General Manager
```

The real structure: procurement is a **workflow with multiple role-based checks** (storekeeper → finance → legal → CEO), not a single "purchasing manager" position.

## Example: department structure (this Odoo instance)

```
Удирдлага (Management)
├── Захирал (Director)
├── Менежер (Manager)
├── Хуулийн мэргэжилтэн (Legal Specialist)
├── Мэдээлэл технологийн ажилтан (IT)
└── Дотоод хяналтын ажилтан (Internal Audit)

Санхүүгийн алба (Finance)
├── Ерөнхий ня-бо (Chief Accountant)
├── Тооцооны ня-бо (Accounting)
└── Нярав (Storekeeper)

Хог тээвэрлэлтийн хэлтэс (Garbage Transport)
├── Хэлтсийн дарга (Dept Head)
├── Жолооч (Driver)
├── Ачигч (Loader)
└── Тээвэрлэлтийн хяналтын ажилтан (Transport Controller)

Ногоон байгууламж, цэвэрлэгээ үйлчилгээний хэлтэс (Green Facility & Cleaning)
├── Ахлах мастер (Senior Master)
├── Мастер (Master)
├── Зам талбайн үйлчлэгч (Road Worker)
└── Ногоон байгууламжийн инженер (Green Facility Engineer)

Тохижилтын хэлтэс (Landscaping)
├── Хэлтсийн дарга — М.Уртбаяр
├── Туслах ажилтан
├── Харуул (Guard)
└── Жолооч (Driver)
```

## Pitfalls

- `hr.job` has a `department_id` field but it may be `False` (not assigned to any department). Do not assume all jobs map to a department.
- `hr.employee` has both `job_title` (free-text, often abbreviated like "ЗТҮ") and `job_id` (formal position from `hr.job`, may be `False`). Use `job_id.name` when available, fall back to `job_title`.
- `res.groups` does **not** have `category_id` in Odoo 19 CE — use `full_name` or `display_name` instead. Querying `category_id` causes an XML-RPC fault.
- Some `hr.employee` records are test entries with fake names — recognize and exclude them from validation (names like "Bdbdj Hdhd", "test test").
- `hr.department.manager_id` is a many2one to `hr.employee` — it returns `[id, name]`. Use `name` from the tuple for display.
