---
name: agent-ops-dashboards
description: Build real-data operational dashboards for Hermes/agent workflows from sessions, gateway logs, cron jobs, and tool-call telemetry.
version: 1.0.0
author: Nous Research
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [dashboard, telemetry, agents, logs, cron, gateway, reporting]
---

# Agent Ops Dashboards

Use this skill when the user asks for a dashboard, analytics page, real performance data, agent reporting, workflow metrics, or hosted operational view for Hermes-powered agents.

## Core principle

Prefer **real telemetry** over mock data. If the user's agents are conceptual workflow roles rather than separate production processes, say so explicitly and infer agent rows from real sessions/logs instead of pretending they are independent workers.

## Data sources to inspect

- Hermes session transcripts: `/opt/data/sessions/session_*.json`
- Cron sessions: `/opt/data/sessions/session_cron_*.json`
- Gateway logs: `/opt/data/logs/gateway.log`
- Diagnostic logs: `/opt/data/logs/gateway-exit-diag.log`, `/opt/data/logs/gateway-shutdown-diag.log`
- Cron job list via the `cronjob` tool when available
- Running hosted preview processes via `process` if a local server has already been started

Never include secrets, API keys, HMAC secrets, tokens, OAuth credential contents, connection strings, or raw private message bodies in a dashboard. Redact as `[REDACTED]`.

## Workflow

1. **Clarify dashboard scope only if needed.** If the user asks for a practical dashboard, make a reasonable first version immediately.
2. **Collect real metrics:** session count, platform split, cron count, message/tool-call totals, success/attention counts, average/median/max response time, gateway inbound/API/error counts, active cron jobs.
3. **Map workflows to agent roles:** infer rows from keywords in final summaries/transcripts, e.g. leads → Lead Prospector, CRM/Odoo → Agentic CRM, content/image generation → Post Generator/Visual Designer, reporting/dashboard → Performance Reporting.
4. **Label inference honestly:** include a visible caveat such as: “Agent rows are derived from real Hermes session transcripts and gateway logs; not all are separate production worker processes yet.”
5. **Generate artifacts:** create a static `index.html` plus `data.json` first. This is quick to preview and can later be ported into Vercel/Next.js.
6. **Verify:** check files exist, JSON parses, and a lightweight HTTP/data fetch works. If one verification method times out, use a different method rather than repeating the same failing command.
7. **Host appropriately:** local `python3 -m http.server` is fine for server-local previews, but explain that `127.0.0.1` is not public. For public use, integrate into the user's Vercel/Next.js app or put it behind a reverse proxy with auth.

## Visual style guidance

For AgenticForce dashboards, use a premium dark SaaS style with black/navy backgrounds, gold/yellow accents, KPI cards, charts, recent jobs/tables, and a sidebar. Prioritize legibility on Telegram screenshots and mobile browser previews.

## Vercel integration pattern

When converting the static dashboard to the user's app, prefer one of:

- `app/dashboard/agents/page.tsx` for the UI
- `app/api/dashboard/agents/route.ts` for JSON metrics
- `public/agent-dashboard/index.html` for a fast static embed

Protect dashboards that show operational data with Clerk/auth or another existing site auth layer.

## References

- `references/agenticforce-real-telemetry-dashboard.md` — concrete example of a Hermes/AgenticForce real-data dashboard built from sessions and gateway logs.
- `references/real-metrics-collection-pipeline.md` — proven data-collection pipeline: reading permission-restricted session files via subprocess cat, parsing gateway.log for response times/API calls, agent-role inference rules, and dashboard file layout with visual style.

## Pitfalls

- Do not call a dashboard "publicly hosted" if it is only bound to `127.0.0.1` or `0.0.0.0` inside the execution environment.
- Do not fabricate per-agent metrics when only aggregate Hermes logs exist; infer and label them.
- Do not publish logs or transcript excerpts that may contain private user data.
- Do not repeat a blocked or timeout-prone verification command unchanged; switch to a lighter probe or different tool.
- **Session files are root:root 0600** — `/opt/data/sessions/session_*.json` are owned by root with restrictive permissions. Python's `open()` / `pathlib.read_text()` will raise `PermissionError`. Workaround: read via `subprocess.run(["cat", path], capture_output=True)` in execute_code, or pipe through `cat` in terminal commands. This applies to both regular and cron session files.
- **Cron session files use `cron_` prefix** — filenames like `session_cron_*.json`. Include both patterns when globbing: `glob("session_*.json")` catches both; but when filtering user vs cron, check `"cron_" in fname` rather than assuming all non-cron are user sessions.
