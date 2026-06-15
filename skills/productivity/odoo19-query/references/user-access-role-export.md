# Odoo 19 user access / role export

Use this when the user asks for "all roles with access", "who has access", "position names", or an actual list of Odoo users and permissions.

## Goal

Produce an auditable read-only export that joins:
- `res.users` active internal users
- explicit Odoo groups (`group_ids`)
- inherited/implied groups (`all_group_ids`)
- linked employee record (`employee_id`)
- HR position/department/manager (`hr.employee` fields)

## Read-only query pattern

1. Verify Odoo XML-RPC connectivity with the helper `ping` command.
2. Query active internal users only unless the user asks for portal/public accounts:
   - model: `res.users`
   - domain: `[["active", "=", true], ["share", "=", false]]`
   - fields: `id,name,login,active,share,group_ids,all_group_ids,groups_count,employee_id`
3. Resolve group IDs from both `group_ids` and `all_group_ids` using `res.groups.read` fields:
   - `id,name,full_name,display_name`
   - Do **not** request `category_id` unless fields inspection confirms it exists on that instance.
4. Resolve employees from linked `employee_id` using `hr.employee.read` fields:
   - `id,name,job_title,job_id,department_id,parent_id,work_email,work_phone,mobile_phone`
5. Export rows with these columns:
   - `user_id`
   - `name`
   - `login`
   - `employee_id`
   - `position_job_title`
   - `department`
   - `manager`
   - `work_email`
   - `work_phone`
   - `explicit_access_roles`
   - `all_access_roles_count`
   - `all_access_roles`
   - optional `is_test_smoke_account`

## Reporting guidance

- Treat `group_ids` as explicitly assigned access roles.
- Treat `all_group_ids` as effective/inherited access roles, including implied roles and technical permissions.
- Flag obvious smoke/test accounts separately when names/logins include markers such as `SMOKE` or `@example.test`; do not silently mix them with real users.
- In the final response, attach the CSV and summarize counts by:
  - total active internal users
  - real vs test/smoke accounts
  - top explicit roles
  - top position names
  - top departments

## Pitfalls

- `res.groups.category_id` may not exist in this Odoo 19 installation; use `full_name`/`display_name` instead for human-readable group names.
- Many users can share generic roles like `Role / User`; include both raw role lists and a short top-role summary so the user can audit details without reading every row in chat.
- Position names are HR employee data, not access groups. Join via `res.users.employee_id` to `hr.employee.job_title` / `job_id`.
