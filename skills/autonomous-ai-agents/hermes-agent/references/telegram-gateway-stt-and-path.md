# Telegram gateway STT + PATH setup notes

Use this when configuring Hermes Gateway for Telegram voice messages or debugging gateway-side agent runs that cannot find `hermes`/`python`.

## Telegram credentials

Direct YAML config uses `platforms.telegram` for credentials:

```yaml
platforms:
  telegram:
    enabled: true
    token: "<numeric_bot_id>:<bot_secret>"
```

Top-level `telegram:` is for behavior settings such as reactions, allowlists, allowed chats, reply behavior, prompts, etc. A BotFather token missing the numeric prefix and colon will be rejected by Telegram as `telegram.error.InvalidToken: Not Found`.

Approve a DM pairing code with:

```bash
/opt/hermes/.venv/bin/python /opt/hermes/hermes pairing approve telegram <CODE>
```

## Local STT with faster-whisper

Some Hermes source-checkout venvs may not include `pip` or `ensurepip`. If `python -m pip install faster-whisper` fails with `No module named pip`, use `uv` against the venv interpreter:

```bash
uv pip install --python /opt/hermes/.venv/bin/python faster-whisper
```

Verify installation:

```bash
/opt/hermes/.venv/bin/python - <<'PY'
import faster_whisper
print('faster_whisper import ok', getattr(faster_whisper, '__version__', ''))
PY
```

Enable local STT in `config.yaml`:

```yaml
stt:
  enabled: true
  provider: local
  local:
    model: base
```

Restart the gateway after changing STT config.

## Starting gateway from a source checkout

If the global `hermes` command is not on PATH, use the checkout launcher explicitly:

```bash
/opt/hermes/.venv/bin/python /opt/hermes/hermes gateway status
/opt/hermes/.venv/bin/python /opt/hermes/hermes gateway run
```

Gateway-spawned tool calls may still invoke `hermes` or `python`. If the runtime environment lacks these command names, start the gateway with a PATH that includes the checkout and venv:

```bash
PATH=/opt/hermes:/opt/hermes/.venv/bin:/usr/local/bin:/usr/bin:/bin \
  /opt/hermes/.venv/bin/python /opt/hermes/hermes gateway run
```

Verify the running gateway process PATH:

```bash
tr '\0' '\n' < /proc/<PID>/environ | grep '^PATH='
```

## Verification

Check status and Telegram connection:

```bash
/opt/hermes/.venv/bin/python /opt/hermes/hermes gateway status
grep -i "telegram connected\|connected to telegram\|failed\|error" /opt/data/logs/gateway.log | tail -80
```

Expected success lines include:

```text
[Telegram] Connected to Telegram (polling mode)
✓ telegram connected
```
