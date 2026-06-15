# Stale gateway platform locks

Use this when a Hermes Gateway platform reports that a credential/token is already in use, but process inspection shows the referenced PID is gone or zombie.

## Symptom

Gateway status or logs show a platform-specific lock error, for example:

```text
telegram: Telegram bot token already in use (PID 1314). Stop the other gateway first.
[Telegram] Telegram bot token already in use (PID 1314). Stop the other gateway first.
```

The global gateway may still run with other platforms, e.g. webhook only, while Telegram fails to connect.

## Verify before touching locks

1. Check gateway status:

```bash
/opt/hermes/.venv/bin/python /opt/hermes/hermes gateway status || hermes gateway status
```

2. Inspect the claimed PID and current gateway processes:

```bash
ps -o pid,ppid,stat,etime,cmd -p <PID>
ps aux | grep -E '[h]ermes.*gateway|[p]ython.*gateway'
```

Only treat the lock as stale if the PID is absent or has zombie status (`STAT` starts with `Z`). If a real non-zombie gateway process is running, stop that gateway instead of deleting the lock.

## Lock locations

Platform credential locks live under:

```text
$HERMES_HOME/.local/state/hermes/gateway-locks/
```

Examples:

```text
/opt/data/.local/state/hermes/gateway-locks/telegram-bot-token-<hash>.lock
```

The profile gateway PID/lock files are separate:

```text
$HERMES_HOME/gateway.pid
$HERMES_HOME/gateway.lock
```

Do not confuse the profile-wide gateway lock with a platform credential lock.

## Auto-resolving Telegram polling conflicts

Not every "token already in use" error indicates a stale lock. The gateway has a built-in retry mechanism for Telegram polling conflicts (3 retries with 10s backoff). These occur when:

- Two gateway instances overlap during a restart or --replace takeover
- A previous gateway instance's long-poll still has a lingering connection to Telegram's API

The log shows:

```text
[Telegram] Telegram polling conflict (1/3), will retry in 10s.
Error: Conflict: terminated by other getUpdates request
...
[Telegram] Telegram polling resumed after conflict retry 1
```

**Wait before treating this as a stale lock.** If the gateway retries successfully and the log shows "polling resumed", the gateway is healthy. Only quarantine platform locks if the polling conflict persists across all 3 retries AND process inspection confirms the referenced PID is zombie or dead.

## Safe cleanup pattern

Quarantine stale platform locks rather than deleting them outright:

```bash
/opt/hermes/.venv/bin/python - <<'PY'
import json, pathlib, subprocess, datetime
base = pathlib.Path('/opt/data/.local/state/hermes/gateway-locks')
for p in base.glob('telegram-bot-token-*.lock'):
    data = json.loads(p.read_text())
    pid = str(data.get('pid'))
    stat = subprocess.run(['ps', '-o', 'stat=', '-p', pid], text=True, capture_output=True).stdout.strip()
    stale = (not stat) or stat.startswith('Z')
    if stale:
        new = p.with_name(p.name + '.stale.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        p.rename(new)
        print(f'quarantined stale lock {p.name} pid={pid} stat={stat!r}')
    else:
        print(f'active lock remains {p.name} pid={pid} stat={stat!r}')
PY
```

Adjust the glob for other platform credential locks if needed.

## Restart and verify

Start the gateway in a way that will not be killed by the tool timeout. For live debugging from the agent, use `terminal(background=true)` rather than a foreground restart command that can be terminated when the tool times out.

Then verify logs contain:

```text
[Telegram] Connected to Telegram (polling mode)
gateway.run: ✓ telegram connected
gateway.run: ✓ webhook connected
gateway.run: Gateway running with 2 platform(s)
```

If a foreground restart was accidentally timed out, it may leave another stale platform lock for the short-lived PID. Re-run the stale-lock verification before starting again.

## Double-fork zombie propagation

When using the double-fork daemon pattern (`start_gateway_daemon.py`), the first call to `os.fork()` returns the first child's PID to the parent — but that first child exits immediately after the second fork. If `start_gateway()` returns that PID and the caller tries to `os.kill()` or track it, the PID is already a zombie. This creates two problems:

1. **The lock file may contain a zombie PID**, causing "Telegram bot token already in use" on restart.
2. **`pkill -f 'hermes gateway'` may not match** if the zombie process's command line differs from the exec'd gateway.

**Fix in the daemon script:** Before `os.execve()`, write the actual PID (`os.getpid()`) to a known file. On startup, the script should:
- `pkill -9 -f 'hermes gateway run'` to kill both zombies and live gateways
- Remove all lock files under `gateway-locks/`
- Wait 2 seconds for cleanup before starting anew

The hardened reference implementation in `references/docker-gateway-persistence.md` documents all of this with the corrected daemon script.
