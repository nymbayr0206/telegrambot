# Cron Job Capacity

There is **no hard-coded maximum** number of cron jobs in Hermes. Jobs are stored in SQLite, bounded only by disk space (~few KB per job).

## Defaults

- **`max_parallel_jobs: None`** in config — no limit on parallel execution
- Each job runs in a `ThreadPoolExecutor(max_workers=1)` thread
- Total jobs: theoretically unlimited

## Practical Limits

| Scenario | Feasible Count | Notes |
|----------|---------------|-------|
| Staggered schedules | 200+ | Jobs fire at different times, no contention |
| Same schedule, simple prompts | 50-100 | Fire in sequence, light CPU per job |
| Heavy jobs at same time (web+LLM+gen) | 10-20 | CPU/memory contention per tick |
| API-rate-limited (OpenRouter, etc.) | Depends on tier | Each job consumes API calls |

## Capacity Trap: Per-Client Jobs

**Do NOT create one cron job per client** (e.g., 1000 jobs for 1000 clients). Each job spins up a full Hermes agent session — wasteful and unnecessary.

**Instead:** One batch script job that loops through all clients:

```
✅ One job every 3h:
  1. Scrape data sources once
  2. Match against ALL client profiles in memory
  3. Send notifications to matched clients

❌ 1000 jobs every 3h:
  Each scrapes the same sites independently → 1000x redundant work
```

A single well-designed batch job handles 1000+ clients with ~30s CPU per run.

## Tuning

To limit concurrent job execution:

```yaml
# config.yaml
cron:
  max_parallel_jobs: 5   # only 5 jobs fire at once
```
