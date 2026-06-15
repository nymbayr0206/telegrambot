# Odoo user access / role audit recipe

Use this when the user asks for the actual list of Odoo users with access roles, positions, departments, or what permissions they have.

## Models and fields

Primary models:
- `res.users` — Odoo login accounts and access groups.
- `res.groups` — access-role/group names.
- `hr.employee` — employee profile, job title, department, manager, contact details.

Useful `res.users` fields:
- `id`, `name`, `login`, `active`, `share`
- `group_ids` — groups explicitly assigned to the user.
- `all_group_ids` — explicit + inherited/implied groups.
- `groups_count`
- `employee_id`

Useful `res.groups` fields:
- `id`, `name`, `full_name`, `display_name`

Useful `hr.employee` fields:
- `id`, `name`, `job_title`, `job_id`, `department_id`, `parent_id`
- `work_email`, `work_phone`, `mobile_phone`

## Query pattern

1. Connect with the helper and verify with `ping`.
2. Query active internal users only unless the user asks for portal/public users:
   ```json
   [["active", "=", true], ["share", "=", false]]
   ```
3. Read all `group_ids` and `all_group_ids`, then read `res.groups` by those IDs to map IDs to readable names.
4. Read linked `hr.employee` records to attach job title, department, and manager.
5. Export a CSV rather than pasting a huge list into chat.
6. Include a concise summary in the reply: total active internal users, smoke/test accounts if detectable, top roles, top positions, and top departments.

## Output columns to include

Recommended CSV columns:
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
- `is_test_smoke_account`

## Pitfalls

- `group_ids` alone only shows explicitly assigned groups. For the full effective access picture, include `all_group_ids` too.
- Some users may be test/smoke accounts. Flag obvious examples such as names containing `SMOKE ` or logins ending in `@example.test`, but do not silently delete them from the report unless the user asks.
- Some Odoo installations do not have `res.groups.category_id`; do not assume it exists. Use `name`, `full_name`, and `display_name` first.
- Some user accounts have no linked employee record, so position and department may be blank.
- Prefer read-only XML-RPC methods (`search_read`, `read`, `search_count`) for audits.
