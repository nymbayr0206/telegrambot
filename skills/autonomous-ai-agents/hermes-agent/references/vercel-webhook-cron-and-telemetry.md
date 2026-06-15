# Vercel app webhook + scheduled Hermes agent + telemetry dashboard pattern

Use this when the user wants a Hermes-powered agent that feeds a Vercel/Next.js app on a schedule, or wants a dashboard backed by real Hermes operational logs rather than mock data.

## Scheduled content agent → Vercel webhook

Typical use case: daily industry news/articles where Hermes researches current news, creates bilingual English/Mongolian article data, selects or generates one image per article for a slider, and POSTs the payload to a Vercel-hosted API route.

1. **Ask only for the irreducible runtime inputs** before creating the cron job:
   - Real Vercel webhook URL, e.g. `https://<domain>/api/hermes/daily-industry-news`.
   - Shared HMAC secret or the environment variable/location where it is stored. Never print or persist the secret value.
   - Final industry list, count per industry, timezone/schedule, and whether the app should receive `draft` or `publish` status.
2. **Payload contract** should be explicit and stable:
   ```json
   {
     "job": "daily_industry_news",
     "generated_at": "ISO-8601",
     "timezone": "Asia/Ulaanbaatar",
     "language_versions": ["en", "mn"],
     "articles": [
       {
         "industry": "Mining",
         "rank": 1,
         "title_en": "...",
         "title_mn": "...",
         "summary_en": "...",
         "summary_mn": "...",
         "body_en": "...",
         "body_mn": "...",
         "image_url": "https://...",
         "sources": [{"title": "...", "url": "...", "published_at": "..."}],
         "status": "draft"
       }
     ]
   }
   ```
3. **Security headers** for Vercel route:
   - `x-hermes-timestamp: <unix-seconds>`
   - `x-hermes-signature: sha256=<hex hmac>` where HMAC is computed over `timestamp + "." + raw_json_body`.
   - Vercel route should reject stale timestamps, missing signature, and non-matching HMAC.
4. **Cron creation**:
   - Use `cronjob(action="create", schedule="0 7 * * *", name="Daily Industry News", prompt=<self-contained prompt>, enabled_toolsets=["web", "terminal" or minimal required])`.
   - The prompt must be fully self-contained because future cron sessions do not inherit the current chat.
   - For Asia/Ulaanbaatar morning delivery, state the timezone explicitly in the prompt and schedule/design.
5. **Do not create a live cron with placeholders.** If the URL or secret is still a placeholder (`your-domain.com`, `HERMES_NEWS_WEBHOOK_SECRET` with no value/location), give the user the exact missing inputs and keep the task at architecture/test-payload stage.

## Real Hermes telemetry dashboard pattern

When asked for “real data from your logs/performance data,” avoid fake sample metrics. Build from available Hermes data sources and label limitations clearly.

### Data sources

Common local sources:
- `~/.hermes/sessions/session_*.json` or environment-specific session dir such as `/opt/data/sessions/session_*.json`.
- `~/.hermes/logs/gateway.log` or environment-specific log dir such as `/opt/data/logs/gateway.log`.
- `hermes cron list/status` or the cronjob tool for scheduled job state.

### Metrics to compute

Useful dashboard metrics:
- Total sessions, Telegram/CLI/cron split.
- Total messages and tool calls.
- Session success/attention rate from transcript/final status heuristics.
- Gateway inbound messages, API/model call count, errors.
- Response time distribution: avg, median, max when timestamps are available.
- Active cron job count.
- Agent/workflow rows inferred from session keywords only when native per-agent telemetry does not exist.

### Important labeling

If the system does not have separate production worker processes per named agent, say so in the dashboard and final response:

> Agent rows are derived from real Hermes session transcripts and gateway logs. They are not yet separate production worker processes except scheduled cron jobs.

Do not claim every named business agent has real native telemetry unless there is direct emitted telemetry for each agent.

### Simple hosting pattern

For a local static dashboard:
1. Generate `index.html` and `data.json` in a durable directory, e.g. `/opt/data/agenticforce-agent-dashboard/`.
2. Serve it with a tracked background process:
   ```bash
   python3 -m http.server 8797 --bind 0.0.0.0
   ```
3. Verify with a lightweight Python `urllib.request.urlopen()` check rather than repeating a curl command that previously timed out or was blocked.
4. Report both file paths and local URL; do not overclaim external public access unless confirmed.

### Production upgrade path

For true per-agent analytics, add an emitted telemetry schema to each production agent/job:

```json
{
  "agent_name": "Lead Prospector Agent",
  "run_id": "uuid",
  "started_at": "ISO-8601",
  "finished_at": "ISO-8601",
  "status": "success|failed|attention_required",
  "task_type": "lead_generation|news_article|crm_sync",
  "input_count": 0,
  "output_count": 0,
  "tool_calls": 0,
  "errors": [],
  "cost_estimate": null,
  "business_outcome": "records_created / emails_sent / articles_published"
}
```

Store these records in the app database or a dedicated telemetry JSONL/table, then have the dashboard read direct telemetry instead of inferring workflows from transcripts.