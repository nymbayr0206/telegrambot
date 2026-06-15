# Odoo Project/Task Reporting Notes

Use this when the user asks for active projects, project names, or tasks grouped by project.

## Active project count

Model: `project.project`

```bash
python /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py count project.project --domain '[["active", "=", true]]'
```

## Active project names

```bash
python /opt/data/skills/productivity/odoo19-query/scripts/odoo_query.py search-read project.project \
  --domain '[["active", "=", true]]' \
  --fields name,active \
  --limit 200 \
  --order 'name asc'
```

Avoid reading `stage_id` unless you have confirmed the current Odoo user has the `Use Stages on Project` group. In this environment, reading `project.project.stage_id` returned an access-rights fault for user id 2.

## Tasks grouped by active project

The helper CLI can run separate `search-read` calls, but grouping projects and tasks is easier with a short Python script using the helper's `_execute_kw` function:

```python
import sys, json
sys.path.insert(0, '/opt/data/skills/productivity/odoo19-query/scripts')
from odoo_query import _execute_kw

projects = _execute_kw(
    'project.project', 'search_read',
    [[['active', '=', True]]],
    {'fields': ['name', 'active'], 'limit': 200, 'order': 'name asc'},
)
project_ids = [p['id'] for p in projects]

tasks = []
if project_ids:
    tasks = _execute_kw(
        'project.task', 'search_read',
        [[['project_id', 'in', project_ids]]],
        {'fields': ['name', 'project_id'], 'limit': 1000, 'order': 'project_id asc, name asc'},
    )

by_project = {p['id']: [] for p in projects}
for task in tasks:
    pid = task.get('project_id')
    if isinstance(pid, list):
        pid = pid[0]
    if pid in by_project:
        by_project[pid].append({'id': task['id'], 'name': task['name']})

result = [
    {
        'project_id': p['id'],
        'project_name': p['name'],
        'task_count': len(by_project[p['id']]),
        'tasks': by_project[p['id']],
    }
    for p in projects
]
print(json.dumps({'project_count': len(projects), 'task_total': len(tasks), 'projects': result}, ensure_ascii=False, indent=2))
```

## Response format

For Telegram, avoid markdown tables. Use headings and bullets:

```text
There are N active projects. Total tasks: M.

## 1. Project name
- Task name
- Task name

## 2. Project with no tasks
- No tasks found
```
