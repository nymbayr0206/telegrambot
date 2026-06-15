# Gateway env-var loss after config changes

When you modify Hermes configuration (STT provider, model, terminal settings, or any `hermes config set` / manual edit), the `.env` file at `/opt/data/.env` can get rewritten and drop platform credentials — most commonly `TELEGRAM_BOT_TOKEN`.

## Symptoms

- Gateway logs show: `No messaging platforms enabled`  (even though Telegram was working before)
- `hermes gateway status` says ✓ running, but nothing connects
- Telegram voice messages pile up unanswered

## Root cause

The config change triggered a gateway restart. On restart, the gateway re-reads `.env` from scratch. If `TELEGRAM_BOT_TOKEN` (or `DISCORD_BOT_TOKEN`, etc.) was lost during the write — due to a config tool overwriting it, manual `.env` edit that removed it, or a partial write — the new process starts with no platform credentials.

## Diagnosis

```bash
# 1. Check if Telegram is missing from the logs
grep -i "no messaging platforms\|telegram connected" /opt/data/logs/gateway.log | tail -5

# 2. Verify TELEGRAM_BOT_TOKEN is in .env
grep TELEGRAM_BOT_TOKEN /opt/data/.env

# 3. If empty, check alternative locations too
grep TELEGRAM_BOT_TOKEN /opt/data/home/.hermes/.env 2>/dev/null

# 4. Also check for token in platforms section of config.yaml
grep -A2 "platforms:" /opt/data/config.yaml | grep telegram -A3
```

## Stale PID death-spiral

After the env loss, when you `hermes gateway restart`, the command sends SIGTERM to the old gateway PID, the old process exits, but the restart command itself can **time out** (common when running from an agent/tool session). This produces a SIGKILL (exit code -9) on the restart command, which may also kill the new gateway process that was already starting. The result:

1. All gateway processes dead
2. Stale PID file remains at `/opt/data/gateway.pid` pointing to a dead PID
3. Next `hermes gateway run` fails with `Gateway already running (PID XXXX)`
4. `hermes gateway status` shows `✗ Gateway is not running` with `Gateway draining` message

**Breaking out of the spiral:**

```bash
# Remove the stale PID file
rm -f /opt/data/gateway.pid

# Start with --replace to force-clear any remaining lock
hermes gateway run --replace
```

The `--replace` flag is the cleanest fix — it clears any stale PID/lock and starts fresh. Prefer it over manual PID-file removal.

## Gateway gets killed as a background process

When you start the gateway via `terminal(background=true)` (even without `notify_on_complete`), the process dies with SIGKILL (exit code -9) after 25-60 seconds. This is because the Hermes CLI process manages background process lifecycles — it sends SIGTERM/SIGKILL to its children.

This is distinct from the timeout problem above. The background process is managed (tracked) by its parent Hermes session, and cleanup happens on session transitions.

### Workaround: direct Python module import

Instead of `hermes gateway run`, start the gateway by importing the module directly from the repo directory. This bypasses the gateway CLI's PID file and process management, but it will still be killed by the parent session:

```bash
cd /opt/hermes && python3 -c "
import sys
sys.path.insert(0, '.')
from gateway.run import main
import asyncio
asyncio.run(main())
"
```

Run this via `terminal(background=true)`. The gateway will stay up as long as the parent session permits — typically a few minutes.

### Cron jobs cannot bootstrap the gateway

The cron job scheduler runs **inside** the gateway process itself. If the gateway is down, no cron jobs fire — including any "start gateway" cron job. This means cron jobs are not a viable bootstrap mechanism for gateway recovery. Fix the env loss directly, then restart the gateway.

### Docker/no-systemd environments

In environments without systemd (Docker containers, ttyd shells), the `hermes gateway install` command cannot create a systemd service. In these environments:

- No reliable long-lived gateway persistence mechanism exists via the Hermes tooling
- Gateway background processes survive only as long as the parent Hermes session
- The only way to keep the gateway running permanently is to start it as a direct child of PID 1 (the container entrypoint), which requires modifying the Dockerfile or entrypoint script to run `hermes gateway run` as a main process alongside the existing service

## Fix

```bash
# Add the token back to .env
echo 'TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklmNOpqrsTUVwxyz' >> /opt/data/.env

# Restart gateway — use --replace to handle any stale PID
/opt/hermes/hermes gateway restart
# or if times out:
#   rm -f /opt/data/gateway.pid && hermes gateway run --replace

# Alternative: run in background (won't time out)
/opt/hermes/hermes gateway run --replace > /opt/data/logs/gateway.log 2>&1 &
```

## Prevention

- Keep a backup of `.env` after initial setup: `cp /opt/data/.env /opt/data/.env.backup`
- Before making config changes, check `.env` has all platform tokens
- After config changes, verify `.env` still has `TELEGRAM_BOT_TOKEN` before restarting the gateway
- Consider moving the token to `platforms.telegram.token` in `config.yaml` instead of `.env` — config.yaml is not overwritten by config-set commands the same way `.env` can be
