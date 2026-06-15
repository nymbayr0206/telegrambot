# Gateway local STT with faster-whisper

Use this when enabling voice-message transcription for Hermes gateway platforms such as Telegram.

## Known-good sequence from a source checkout

1. Install faster-whisper into the Hermes runtime venv.

If the checkout venv has pip:

```bash
/opt/hermes/.venv/bin/python -m pip install faster-whisper
```

If the checkout venv is stripped and reports `No module named pip`, use uv against the venv Python instead:

```bash
uv pip install --python /opt/hermes/.venv/bin/python faster-whisper
```

2. Configure STT in `config.yaml`:

```yaml
stt:
  enabled: true
  provider: local
  local:
    model: base
```

3. Verify the package import in the same Python the gateway will use:

```bash
/opt/hermes/.venv/bin/python - <<'PY'
import faster_whisper
print('faster_whisper import ok', getattr(faster_whisper, '__version__', 'unknown'))
PY
```

4. Restart the gateway.

For a manually-run gateway in a source checkout, if `hermes gateway run` reports an already-running PID after a tracked background process was killed, use the CLI stop/status flow before starting again:

```bash
/opt/hermes/.venv/bin/python /opt/hermes/hermes gateway stop || true
/opt/hermes/.venv/bin/python /opt/hermes/hermes gateway status || true
/opt/hermes/.venv/bin/python /opt/hermes/hermes gateway run
```

5. Verify logs include the platform reconnecting, e.g. for Telegram:

```bash
grep -i "telegram connected\|connected to telegram\|failed\|error\|stt\|whisper" ~/.hermes/logs/gateway.log | tail -80
```

## Pitfalls

- Do not record `No module named pip` as a durable tool failure. The fix is to install with `uv pip install --python <venv-python> ...` or bootstrap a venv with pip.
- Config changes for gateway STT require a gateway restart.
- Verify imports using the exact venv Python used to run the gateway, not the system Python.
