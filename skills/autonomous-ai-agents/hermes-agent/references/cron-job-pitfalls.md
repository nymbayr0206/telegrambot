# Cron Job Pitfalls and Patterns

This reference covers common cron job issues discovered in production use. See the Cron section in the main SKILL.md for the overview.

## Silent `last_status: error` with no retry

When a cron job has `last_status: error`, the scheduler enters a backoff period — it does NOT retry on the next tick. You must actively `cronjob(action='run')` to test a fix, or wait for the normal schedule to come around again (and even then it only fires at the next scheduled time, not immediately).

If multiple jobs share the same schedule slot and are all in error, fix one, run it, check the result, then fix the next. Do not change every job's schedule to force immediate retries — fix the root cause instead.

## Model/provider override is required for reliability

Cron jobs inherit the session's current model/provider at creation time only if neither `model` nor `provider` is explicitly set. If the default provider later changes (user switches models, credentials expire, a custom provider is unconfigured), cron jobs without an explicit override fail silently with `last_status: error`.

Always pin cron jobs to a specific model+provider when the user has a custom or non-default setup. For jobs created before this rule was known, list them and update each with `cronjob(action='update', job_id='...', model=...)`.

## Script path must be relative under ~/.hermes/scripts/

When using the `script` parameter, the path must be a bare filename relative to `~/.hermes/scripts/`. Absolute paths like `/opt/data/.../foo.sh` are rejected at create/update time with a clear error. Always copy the script in first:

```bash
cp /some/absolute/path/script.sh ~/.hermes/scripts/foo.sh
chmod +x ~/.hermes/scripts/foo.sh
```

Then use `script='foo.sh'`.

## Using `no_agent` correctly

Two modes:

1. **`no_agent: true` (default when script is set)** — the script IS the job. The scheduler runs the script on schedule and delivers its stdout verbatim. No LLM tokens consumed. Use for watchdogs, polls, heartbeats, or any task where the output is predictable and the script produces its own message text.

2. **`no_agent: false` (LLM-driven, requires prompt)** — the agent runs the prompt each tick, then optionally runs the `script` as a post-step. Use when generation/reasoning is needed before the script runs (e.g. generate 4 AI images, then a shell script sends them to a webhook).

Converting from `no_agent: true` to `no_agent: false`:

```python
cronjob(
    action='update',
    job_id='...',
    no_agent=False,
    prompt='Full self-contained prompt...',
    skills=['social-media-automation'],
    script='helper.sh',      # optional post-generation script
    enabled_toolsets=['terminal','file','skills'],
)
```

When `no_agent: false` with a `script`, the agent's prompt runs first, then the script executes after the agent finishes. This is ideal for "generate then deliver" patterns.

## Capacity: no hard limit, but batching beats per-client jobs

There is **no hard-coded maximum** on cron jobs. Jobs are SQLite-backed (bounded by disk space, ~few KB per job) and `max_parallel_jobs: None` (unlimited) is the default. Practical ceilings depend on schedule distribution and job weight:

| Scenario | Rough ceiling |
|----------|--------------|
| Staggered schedules, simple prompts | Hundreds (200+) |
| Same-slot, simple `no_agent: true` scripts | 50-100+ |
| Heavy jobs (web scraping + LLM calls) at the same minute | 10-20 (CPU/memory contention) |
| API-rate-limited providers | Depends on tier |

### 🚩 Anti-pattern: one cron job per client

Do NOT create N identical cron jobs for N clients/users (e.g. 1000 cron jobs for 1000 real estate clients). Each job spins up a full agent session — wasteful and scales poorly.

### ✅ Pattern: one batch script for all

Create a **single cron job** that:
1. Scrapes/gathers data **once** (sites, APIs, feeds)
2. Processes all client profiles against that data in-memory (simple loop, SQL query, or dict lookup)
3. Sends notifications only to matched clients

```
 1. Collect data (1x)                           ← 50-200 HTTP requests max
 2. Match against all N client profiles         ← O(N) in-memory, fast
 3. Send notifications to matched only
```

**Load for 1000 clients with this pattern:** ~30 seconds CPU per run, 200-500 MB RAM, ~4 minutes of actual compute per day on a $5/month VPS.

For the matching step, a simple SQLite DB with client criteria works fine — no need for per-client cron jobs.

## State-file pattern for multi-step cron workflows

Cron jobs that maintain progress across runs (e.g. a daily carousel series) need a durable state file. Do NOT use the `context_from` chaining pattern for counting — use a JSON state file on disk:

```json
{
  "series_total": 18,
  "next_carousel": 1,
  "completed": [],
  "last_run_at": null,
  "last_status": null,
  "timezone": "Asia/Ulaanbaatar",
  "schedule": "daily 09:00"
}
```

Rules:
- Keep state alongside the project data (e.g. `brand/automation/state.json`)
- The first action in every cron run is: read state, determine what to do
- The last action is: on success, advance the counter
- Do NOT increment `next_carousel` if generation or delivery fails
- State owner: only the cron job should write it. If both LLM-driven and script mode touch state, the script handles the final write.
