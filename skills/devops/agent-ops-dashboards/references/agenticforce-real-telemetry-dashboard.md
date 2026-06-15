# AgenticForce real telemetry dashboard example

This reference captures a reusable pattern from a session where the user asked for a real-data dashboard for AgenticForce/Hermes agents.

## Situation

The user had a list of named business agents, but most were conceptual workflow roles rather than independently instrumented production workers. The correct approach was to build a dashboard from real Hermes operational sources and clearly label inferred agent rows.

## Real data sources used

- `/opt/data/sessions/session_*.json`
- `/opt/data/logs/gateway.log`
- Hermes cron/status output where available

## Metrics that proved useful

- Total sessions
- Platform split: Telegram, CLI, cron
- Total messages
- Total tool calls
- Session success rate
- Gateway inbound messages
- Gateway API calls observed in logs
- Gateway errors
- Average/median/max response seconds
- Active cron jobs
- Inferred agent runs/success/attention/tool calls/messages/duration/last active

## Output shape

Generate:

- `index.html` — standalone dark SaaS dashboard UI
- `data.json` — machine-readable telemetry payload

Example local directory:

```txt
/opt/data/agenticforce-agent-dashboard/index.html
/opt/data/agenticforce-agent-dashboard/data.json
```

Example local preview command:

```bash
cd /opt/data/agenticforce-agent-dashboard
python3 -m http.server 8797 --bind 0.0.0.0
```

## Verification pattern

- Confirm files exist and are non-empty.
- Parse `data.json` with Python JSON tools.
- If `curl`/HTTP verification times out, do not repeat the same command unchanged. Use a smaller Python `urllib` fetch, browser navigation, or process polling.

## User-facing caveat

Use wording like:

> This dashboard uses real Hermes operational data. The named business agents are currently inferred from session topics and workflows, not all separate production worker processes yet.

## Public hosting guidance

A local server on `127.0.0.1` or `0.0.0.0` is not automatically public. For durable/public use, integrate into the Vercel/Next.js app, for example:

```txt
app/dashboard/agents/page.tsx
app/api/dashboard/agents/route.ts
```

or serve as a static asset under:

```txt
public/agent-dashboard/index.html
```

Operational dashboards should be protected by site auth when they include internal metrics.
