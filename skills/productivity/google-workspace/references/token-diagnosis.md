# Token Diagnosis & Recovery

When `setup.py --check` fails, not all failures are equal. This reference helps
an agent programmatically diagnose the root cause and choose the right fix.

## Step 1: Is the token file present?

```bash
python3 -c "
import os, json
path = os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))
token_path = os.path.join(path, 'google_token.json')
if os.path.exists(token_path):
    data = json.load(open(token_path))
    print(f'FILE_EXISTS: expiry={data.get(\"expiry\",\"?\")} refresh_token={\"present\" if data.get(\"refresh_token\") else \"MISSING\"} scopes={len(data.get(\"scopes\",[]))}')
else:
    print(f'FILE_MISSING (looked at {token_path})')
"
```

**No file** → Full setup needed (Steps 2-5 in SKILL.md). The token was never
created or was deleted.

**File exists** → Move to Step 2.

## Step 2: Try auto-refresh via `--check`

```bash
# Use the right Python — Hermes venv if system pip is unavailable
PYTHON=$(which python3 || which python)
$PYTHON /path/to/setup.py --check
```

If this prints `AUTHENTICATED`, it auto-refreshed the token — no action needed.

If it prints `TOKEN_REVOKED`, proceed to Step 3.

## Step 3: Manual refresh attempt (diagnose root cause)

Use the Google OAuth Python client directly to attempt a refresh. This tells
you whether the `refresh_token` is still valid:

```python
import json, os
from google.oauth2.credentials import Credentials
import google.auth.transport.requests

token_path = os.path.join(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes')), 'google_token.json')
token = json.load(open(token_path))
client = json.load(open(token_path.replace('google_token.json', 'google_client_secret.json')))

creds = Credentials(
    token=token.get('token', ''),
    refresh_token=token.get('refresh_token'),
    token_uri=token.get('token_uri', 'https://oauth2.googleapis.com/token'),
    client_id=token.get('client_id', client.get('installed', {}).get('client_id')),
    client_secret=token.get('client_secret', client.get('installed', {}).get('client_secret')),
    scopes=token.get('scopes', [])
)

try:
    creds.refresh(google.auth.transport.requests.Request())
    print(f'REFRESH_SUCCEEDED new_expiry={creds.expiry}')
    # Save the refreshed token back
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
        'universe_domain': creds.universe_domain,
        'account': '',
        'expiry': creds.expiry.isoformat() if creds.expiry else '',
        'type': 'authorized_user'
    }
    json.dump(token_data, open(token_path, 'w'), indent=2)
    print('TOKEN_SAVED')
except Exception as e:
    error_str = str(e)
    if 'invalid_grant' in error_str:
        print(f'REFRESH_FAILED: refresh_token REVOKED or EXPIRED. User must re-auth.')
        print('Reason: The user likely revoked the app in their Google Account settings,')
        print('or the refresh token itself expired (e.g. unused for >6 months).')
        print('Action: Run setup.py --revoke, then redo Steps 3-5 from the skill docs.')
    else:
        print(f'REFRESH_FAILED (other): {error_str}')
```

## Diagnosis table

| `--check` output | What it means | Action |
|---|---|---|
| `AUTHENTICATED` | Token good | Nothing |
| `TOKEN_REVOKED` + refresh works manually | Token file was stale, `--check` hit a transient error | Try `--check` again, or save the manually-refreshed token |
| `TOKEN_REVOKED` + manual refresh fails with `invalid_grant` | Refresh token itself is dead | `--revoke` then re-auth (Steps 3-5) |
| File missing at expected path, but exists elsewhere | `HERMES_HOME` may be set differently | Check `HERMES_HOME` env var vs actual file location |
| `NOT_AUTHENTICATED` | No token at all | Full setup from scratch |

## Common pitfalls

- **Token exists at `/opt/data/google_token.json` but `setup.py` can't find it:**
  `setup.py` uses `get_hermes_home()` which respects the `$HERMES_HOME` env var.
  If `HERMES_HOME` is set, the token must be at `$HERMES_HOME/google_token.json`.
  Check with: `echo "HERMES_HOME=$HERMES_HOME"` and verify the file is there.

- **Hermes venv has Google packages pre-installed:**
  On Hermes installations, `/opt/hermes/.venv/bin/python3` has all the Google
  API dependencies. Use this Python instead of the system one when `pip` or
  `uv` are unavailable:
  ```bash
  /opt/hermes/.venv/bin/python3 /path/to/setup.py --check
  ```
  This also works for `google_api.py` commands — no need to install deps.

- **Token exists but `--check` says NOT_AUTHENTICATED:**
  The file may be an old `gws` token in a different format, or the `type` field
  is missing/wrong. The script expects `"type": "authorized_user"`.

- **Access token expired but refresh is fine:**
  `setup.py --check` handles this silently — it auto-refreshes. Only jump to
  re-auth if `--check` explicitly says `TOKEN_REVOKED`.
