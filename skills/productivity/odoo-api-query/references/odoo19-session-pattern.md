# Session Note: Odoo 19 Query Access Pattern

This note captures reusable details from a session where the user wanted natural-language query access to an Odoo 19 system.

## Durable Technical Findings

- The user described the system as an “Odoo 19 database.”
- The provided port was `8069`, which is the Odoo web/XML-RPC API port, not PostgreSQL.
- A direct PostgreSQL probe on `5432` was refused, while `8069` was reachable.
- XML-RPC authentication against `/xmlrpc/2/common` succeeded and returned Odoo server series `19.0`.

## Lesson

When a user gives Odoo host + database + credentials and a port like `8069`, proceed through Odoo XML-RPC rather than trying raw PostgreSQL. Explain the distinction clearly: Odoo API access is safer and respects Odoo permissions/business logic; direct PostgreSQL is usually unnecessary and may be closed.

## Security Reminder

Do not store the user's actual host, database, username, password, or admin credential in this reference. Ask them to place secrets in environment variables or a proper credential store.
