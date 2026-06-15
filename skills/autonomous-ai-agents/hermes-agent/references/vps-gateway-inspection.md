# VPS Gateway Inspection

When you SSH into a Hermes VPS and need to understand the running state — where the gateway lives, what port it's on, whether it's a service or foreground process, and what webhook config it has — use this reconnaissance recipe.

## 0. Prerequisite: Locate the Hermes Binary

`hermes` may NOT be on `$PATH` (common in Docker/VPS/source-checkout setups). Try these in order:

```bash
# Preferred: full path via repo venv
/path/to/hermes/.venv/bin/python /path/to/hermes/hermes gateway status

# Or add to PATH temporarily
export PATH="/opt/hermes/.venv/bin:$PATH"
hermes gateway status

# Fallback: check common install locations
which hermes 2>/dev/null
ls /opt/hermes/hermes 2>/dev/null
ls /opt/hermes/.venv/bin/hermes 2>/dev/null
find / -name "hermes" -type f 2>/dev/null | grep -v node_modules | head -5
```

Once found, alias or export PATH for the rest of the session.

## 1. Check if Gateway is Running

```bash
# Check gateway status via Hermes CLI (use full path if not on PATH)
hermes gateway status

# Alternative: find the actual process
ps aux | grep -v grep | grep "hermes gateway"
```

Look for either:
- `hermes gateway run` — foreground/manual mode
- `hermes gateway` — systemd service (check with `systemctl --user status hermes-gateway`)
- A startup daemon script may have spawned it — check `/opt/data/scripts/` for `start_gateway_daemon.py` or similar

### Dual .env file pitfall

This VPS may have **two `.env` files** with different content:

| File | Purpose |
|------|---------|
| `$HERMES_HOME/.env` | **Main** — contains `TELEGRAM_BOT_TOKEN`, `DEEPSEEK_API_KEY`, `KIE_API_KEY`, etc. |
| `~/.hermes/.env` or `$HOME/.hermes/.env` | Secondary/overlay — may have different or fewer vars |

If the gateway connects but behaves differently after a restart, compare both:

```bash
diff $HERMES_HOME/.env $HOME/.hermes/.env
```

The gateway loads `$HERMES_HOME/.env` — if a tool or cron job is writing to `$HOME/.hermes/.env` instead, critical vars (like `GATEWAY_ALLOW_ALL_USERS`, `TELEGRAM_BOT_TOKEN`) can go missing silently. Align them or add `export` directives to wire both.

## 2. Find Running PIDs and Process Type

```bash
# Full process list with parent info
ps aux | grep -E "hermes|python"

# Check if systemd service
systemctl --user list-units --type=service --all 2>/dev/null | grep -i hermes
systemctl list-units --type=service --all 2>/dev/null | grep -i hermes

# Check for docker
docker ps 2>/dev/null | grep -i hermes

# Check cron jobs
hermes cron list
```

Key distinction:
- `runuser -u hermes -- env ... hermes gateway run` → manually started
- `systemctl` shows systemd service
- Missing both → probably in Docker

## 3. Find the hermes Binary and Version

```bash
which hermes 2>/dev/null
hermes --version
```

Source installs: binary lives in `.venv/bin/hermes` under the project root.

## 4. Locate Config and Data

```bash
# Print config path
hermes config path 2>/dev/null

# Print env path
hermes config env-path 2>/dev/null

# Fallback: check common locations
echo "$HERMES_HOME"
ls ~/.hermes/config.yaml 2>/dev/null
ls /opt/data/config.yaml 2>/dev/null
```

Config.yaml contains all settings. `.env` (same directory) contains API keys.

## 5. Find What Port the Gateway Listens On

```bash
# Modern systems (ss is preferred but may be missing in minimal containers)
cat /proc/net/tcp 2>/dev/null | awk '{print $2}' | grep -v "local_address"

# Decode hex port to decimal: echo $((0x21C4)) = 8644
# Or just send the hex to python
python3 -c "
import re
with open('/proc/net/tcp') as f:
    for line in f:
        local = line.split()[1]
        ip, port_hex = local.split(':')
        port = int(port_hex, 16)
        state = line.split()[3]
        if state == '0A':  # LISTEN
            print(f'Port {port} LISTEN')
"
```

Common Hermes ports:
- 8644 — webhook platform (gateway)
- 4860 — ttyd web terminal
- 8890 — image cache HTTP server
- 8899 — dashboard HTTP server

## 6. Check Webhook Platform Config

From `config.yaml`, look for:

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: 0.0.0.0
      port: 8644
      secret: <sha256-secret>
```

Health check:
```bash
curl -s http://localhost:8644/health
# Expected: {"status":"ok","platform":"webhook"}
```

## 7. Check Telegram Status

Telegram runs inside the gateway (long-polling, not webhook). Verify from config:

```yaml
platforms:
  telegram:
    enabled: true
    token: 1234567890:...
```

The gateway connects to Telegram API directly — no Telegram webhook setup needed.

## 8. Check for Zombie Processes

Hermes spawns many browser/tool subprocesses. Zombies are common and mostly harmless:

```bash
ps aux | grep -w Z
# Z = defunct (zombie), ZN = defunct + nice
```

If there are too many, the parent process (PID 1 or gateway PID) needs to `wait()` for them. A gateway restart cleans them up.

## 9. Find the Telegram Bot Token (Redacted)

```bash
grep -A2 "telegram:" /opt/data/config.yaml 2>/dev/null | grep token
# Output will be redacted in most shells as ****
```

## Quick Summary Command

```bash
# First, find the hermes binary
HERMES_BIN=$(which hermes 2>/dev/null)
if [ -z "$HERMES_BIN" ]; then
    [ -f "/opt/hermes/.venv/bin/hermes" ] && HERMES_BIN="/opt/hermes/.venv/bin/python /opt/hermes/hermes"
fi
echo "=== HERMES VPS DIAGNOSTIC ==="
echo "Binary: ${HERMES_BIN:-not found}"
$HERMES_BIN --version 2>/dev/null || echo "Version: unknown"
echo "Config: $($HERMES_BIN config path 2>/dev/null || echo 'unknown')"
echo "Gateway status: $($HERMES_BIN gateway status 2>/dev/null | head -1)"
echo "Gateway PIDs: $(ps aux | grep -v grep | grep 'hermes gateway' | awk '{print $2}' | tr '\n' ' ')"
echo ""
echo "=== .ENV FILES ==="
wc -l $HERMES_HOME/.env 2>/dev/null || echo "  (no HERMES_HOME/.env)"
wc -l ~/.hermes/.env 2>/dev/null || echo "  (no ~/.hermes/.env)"
echo "Diff: $(diff $HERMES_HOME/.env ~/.hermes/.env 2>&1 | head -3 || echo 'identical or not comparable')"
echo ""
echo "=== LISTENING PORTS ==="
python3 -c "
import re
with open('/proc/net/tcp') as f:
    for line in f:
        local = line.split()[1]
        ip, port_hex = local.split(':')
        port = int(port_hex, 16)
        state = line.split()[3]
        if state == '0A':
            print(f'  Port {port} LISTEN')
" 2>/dev/null || echo "  (cannot read /proc/net/tcp)"
echo ""
echo "=== WEBHOOK HEALTH ==="
curl -s http://localhost:8644/health 2>/dev/null || echo "  (gateway not responding on port 8644)"
echo ""
echo "=== STARTUP DAEMON ==="
ls /opt/data/scripts/start_gateway_daemon.py 2>/dev/null && echo "  (daemon script exists)" || echo "  (no daemon script)"
echo ""
echo "=== RECENT GATEWAY LOG (last 3 lines) ==="
tail -3 /opt/data/logs/gateway.log 2>/dev/null || echo "  (log not found at /opt/data/logs/gateway.log)"
```
