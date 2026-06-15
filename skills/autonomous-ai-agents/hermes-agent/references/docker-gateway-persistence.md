# Docker container gateway persistence (ttyd as PID 1)

Use when Hermes Gateway runs inside a Docker container where PID 1 is `ttyd` (the web terminal server), not systemd. In this environment:

- `systemctl` is unavailable
- `hermes gateway install` refuses (detects container context)
- The gateway process dies when its parent shell exits (background tool processes end when the agent session ends)
- PID 1 (ttyd) sends SIGTERM on certain events (new terminal session, container lifecycle)

## The pattern: double-fork daemon

The canonical approach is `/opt/data/scripts/start_gateway_daemon.py` — a double-fork daemon that:

1. Fork 1: detaches from the parent (currently-running agent)
2. `setsid()`: creates a new session (no controlling terminal)
3. Fork 2: fully orphans the child (reparented to PID 1)
4. Closes all inherited file descriptors
5. Redirects stdin → `/dev/null`, stdout+stderr → log file
6. `os.execve()` — replaces the daemon child with the gateway process

Result: the gateway runs with PPID=1 (ttyd), independent of any agent session or terminal.

## Critical fixes applied to the daemon script

### 1. Stale lock cleanup (before starting)

The gateway writes platform credential locks under:
```
/opt/data/home/.local/state/hermes/gateway-locks/*.lock
```

A zombie or killed gateway leaves these behind. A fresh start with a stale lock fails with:
```
Telegram bot token already in use (PID 9999). Stop the other gateway first.
```

**Fix:** delete all `*.lock` files before starting:
```python
import glob
for lock in glob.glob("/opt/data/home/.local/state/hermes/gateway-locks/*.lock"):
    os.remove(lock)
```

### 2. Zombie process cleanup

Kill both zombies and live gateways aggressively before restart:
```python
subprocess.run(["pkill", "-9", "-f", "hermes gateway run"], capture_output=True)
subprocess.run(["pkill", "-9", "-f", "hermes gateway"], capture_output=True)
time.sleep(2)
```

### 3. PID tracking

The double-fork means `start_gateway()` returns the first child's PID, which exits immediately. The actual gateway has a different PID. **Fix:** write `os.getpid()` (the second child's PID) to a file just before `os.execve()`:

```python
with open("/opt/data/gateway.pid", "w") as f:
    f.write(str(os.getpid()))
```

On restart, read the PID file and verify or fall back to `pgrep -f "hermes gateway run"`.

## .env loading from two paths

The daemon script now loads environment variables from **both** `~/.hermes/.env` and `$HERMES_HOME/.env` (e.g. `/opt/data/.env`). This is critical because:

- The CLI typically reads `~/.hermes/.env` (which resolves to `/opt/data/home/.hermes/.env`)
- The gateway reads `$HERMES_HOME/.env` (which resolves to `/opt/data/.env`)
- API keys (`VOICE_TOOLS_OPENAI_KEY`, `GROQ_API_KEY`, `TELEGRAM_BOT_TOKEN`, etc.) may live in either file

The daemon script merges both into the environment passed to `os.execve()`, so the gateway sees all keys regardless of which `.env` file they're in.

**Diagnostic:** If the gateway connects to Telegram but STT fails with "No STT provider available" or "API key not set", the API key is almost certainly in one `.env` file but not the other. The fix is to ensure the key is in at least one of:
- `/opt/data/.env` (gateway's primary env)
- `/opt/data/home/.hermes/.env` (CLI's primary env)

## Signal hardening

ttyd (PID 1) may propagate SIGTERM/SIGINT to child processes. The daemonized child should ignore these signals before exec:

```python
signal.signal(signal.SIGHUP, signal.SIG_IGN)
signal.signal(signal.SIGTERM, signal.SIG_IGN)
signal.signal(signal.SIGINT, signal.SIG_IGN)
```

The gateway binary re-registers its own handlers on startup, so ignoring in the wrapper is safe — the exec'd gateway resets signal dispositions to SIG_DFL.

## Usage

```bash
python3 /opt/data/scripts/start_gateway_daemon.py
```

Output: `Gateway running with PID(s): 131872`

Then verify:
```bash
export PATH="/opt/hermes/.venv/bin:$PATH"
hermes gateway status
tail -20 /opt/data/logs/gateway.log | grep "telegram connected"
```

## Automatically starting on container boot

The container's entrypoint is `/hermes.sh` (root-owned, not writable by the `hermes` user). It contains:
```bash
setsid -f hermes gateway run >>"$HERMES_HOME/logs/gateway.log" 2>&1 </dev/null
```

This doesn't work because `hermes` is not on the default PATH. On this system:
- Hermes is at `/opt/hermes/.venv/bin/hermes`
- The correct PATH is `export PATH="/opt/hermes/.venv/bin:$PATH"`
- But `/hermes.sh` is root-owned and cannot be modified

**Workaround:** manually run the daemon script when needed. If the container image can be rebuilt, fix `/hermes.sh` to:
```bash
export PATH="/opt/hermes/.venv/bin:$PATH"
python3 /opt/data/scripts/start_gateway_daemon.py >/dev/null 2>&1
```

## Per-user PATH setup

Added to user's `.zshenv` (sourced by zsh on every shell start, including ttyd):
```
export PATH="/opt/hermes/.venv/bin:$PATH"
```

This file lives at `/opt/data/home/.zshenv` (the user's `$HOME` as set by `/hermes.sh`).

## Verifying the gateway is processing messages

After starting, the only reliable check is the log file — `hermes gateway status` only shows if the process is alive, not if Telegram is connected:

```bash
tail -20 /opt/data/logs/gateway.log

# Look for these markers:
#   ✓ telegram connected              → API connection OK
#   inbound message: ... msg='...'    → messages arriving
#   response ready: ... api_calls=N   → responses being sent
```

If you see `✓ telegram connected` but no `inbound message` after the user says they messaged, check:
- Is the user's chat ID in `TELEGRAM_HOME_CHANNEL` or `telegram.allowed_chats`?
- Is `GATEWAY_ALLOW_ALL_USERS` set? If not even the home channel user may be rate-limited on first contact.

## The `--replace` flag: why it matters

Every gateway start should use `hermes gateway run --replace` (not plain `run`). Without it:

1. **First ttyd connection** → `/hermes.sh` starts gateway A on port/chat
2. **Daemon script runs** → tries to start gateway B → fails with `Gateway already running (PID A)`
3. **Something kills gateway A** → gateway B still hasn't started → **no gateway at all**

With `--replace`, step 2 sends a SIGTERM to gateway A and immediately takes over. The `start_gateway_daemon.py` uses `--replace` for exactly this reason.

## Symptom checklist for "gateway not working" in Docker

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `hermes: command not found` | PATH not set | Source `/opt/data/home/.zshenv` or run via full path |
| `Gateway not running` — no process | Gateway died when parent session ended | Use the daemon script, not background tool |
| `token already in use (PID X)` | Stale lock file from zombie/killed gateway | Delete locks, run daemon script |
| `signal-initiated shutdown` in log | ttyd sent SIGTERM | Signal hardening (step 4 above) |
| Zombie processes everywhere | Parent didn't `wait()` on forked children | `pkill -9 -f "hermes gateway"` before restart |
| Gateway runs but Telegram doesn't respond | `GATEWAY_ALLOW_ALL_USERS` not set or home channel mismatch | Set env var or configure `telegram.allowed_chats` |
| Gateway repeatedly dies and restarts | Two gateways fighting over Telegram token — `/hermes.sh` starts one without `--replace`, daemon script starts another | Use only one launch method (prefer daemon script), ensure both use `--replace` |
| Gateway dies on new ttyd web terminal connection | `/hermes.sh` runs on every connection, sometimes signaling the old gateway. ttyd as PID 1 propagates signals | Use the daemon script (signal-hardened, ignores SIGTERM) as the sole launch mechanism |
