# Odoo HR Organizational Structure Queries

Use this when the user asks for company organizational structure — departments, job positions, headcount, department managers, or HR data needed for reports, handover documents, or org charts.

## Key Models

| Model | Purpose | Useful Fields |
|-------|---------|---------------|
| `hr.department` | Departments/divisions | `id`, `name`, `manager_id`, `parent_id` |
| `hr.job` | Job positions | `id`, `name`, `department_id`, `no_of_employee` |
| `hr.employee` | Employee records | `id`, `name`, `job_title`, `job_id`, `department_id`, `parent_id`, `work_email`, `work_phone` |

## Query Patterns

### All departments with managers
```python
models.execute_kw(db, uid, password, 'hr.department', 'search_read', [[]],
    {'fields': ['id', 'name', 'manager_id'], 'limit': 50})
```
`manager_id` returns a tuple `(id, name)` when set.

### All job positions with department + headcount
```python
models.execute_kw(db, uid, password, 'hr.job', 'search_read', [[]],
    {'fields': ['id', 'name', 'department_id', 'no_of_employee'], 'limit': 100, 'order': 'name asc'})
```
Use this to verify whether a claimed position actually exists in the org chart (e.g., confirm there's no "Худалдан авалтын менежер").

### All active employees with job, department, manager
```python
models.execute_kw(db, uid, password, 'hr.employee', 'search_read',
    [[['active', '=', True]]],
    {'fields': ['id', 'name', 'job_title', 'job_id', 'department_id', 'parent_id'],
     'limit': 100, 'order': 'name asc'})
```
`parent_id` is the employee's manager/team lead. `job_id` links to `hr.job`, `department_id` links to `hr.department`.

### User groups / system roles
```python
models.execute_kw(db, uid, password, 'res.groups', 'search_read', [[]],
    {'fields': ['id', 'name', 'full_name'], 'limit': 100, 'order': 'name asc'})
```
**Pitfall**: `res.groups` does NOT have `category_id` in this Odoo 19 instance. Use `full_name` instead.

## Report Reconciliation Pattern

When cross-referencing Odoo HR data against a document (e.g., a handover report's role table):

1. Query `hr.job` to get every registered position.
2. Compare against the document's role list — flag positions that don't exist.
3. Query `hr.department` for actual department names and managers.
4. Query `hr.employee` with `job_title` to get the actual person holding each role.
5. For procurement/purchasing roles, check `res.groups` with names containing "Procurement" or "Худалдан авалт" — in Mongolian municipal Odoo, purchasing is a multi-step workflow (Нярав → Санхүү → Хуулийн этгээд → Ерөнхий менежер → Захирал), not a single manager role.

## User Groups Related to Procurement (Mongolian municipal context)

| Group Name (Odoo) | Equivalent Role |
|-------------------|----------------|
| Хот тохижилтын засвар / Procurement / Purchase Manager | Procurement manager (процесс эзэмшигч) |
| Хот тохижилтын засвар / Procurement / Storekeeper | Нярав |
| Хот тохижилтын засвар / Procurement / Finance User | Санхүү |
| Хот тохижилтын засвар / Procurement / Legal User | Хуулийн этгээд |
| Хот тохижилтын засвар / Procurement / CEO | Захирал |
| Хот тохижилтын засвар / Procurement / General Manager | Ерөнхий менежер |
| Хот тохижилтын засвар / Procurement Administration User | Бичиг хэрэг |
