# OAuth PKCE Manual Exchange

When the standard `setup.py --auth-url` → `setup.py --auth-code` flow fails with errors like:

```
InvalidGrantError: (invalid_grant) Missing code verifier
```

or the code_verifier from the generated OAuth flow state is not persisted/exposed — use this manual PKCE exchange technique.

## Problem

The `google_auth_oauthlib` Flow class generates a PKCE code_verifier internally when calling `authorization_url()`, but this verifier is **not always accessible** via `flow.oauth2session._client.code_verifier` (returns `None` on some versions). The Flow state also cannot always be pickled for later reuse (`AttributeError: Can't get local object`).

As a result, when you generate an auth URL but the user provides the code in a separate turn/session, the Flow can't complete the exchange.

## Solution: Manual PKCE + Direct HTTP Exchange

### Step 1: Generate auth URL with manual PKCE

```python
import secrets, hashlib, base64, json, requests

# Step 1a: Load client config
client_path = "/opt/data/google_client_secret.json"
with open(client_path) as f:
    cfg = json.load(f)['installed']

# Step 1b: Generate PKCE values
code_verifier = base64.urlsafe_b64encode(
    secrets.token_bytes(32)
).rstrip(b'=').decode()

code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).rstrip(b'=').decode()

# Step 1c: Save verifier for later exchange
import os
os.makedirs('/opt/data/email-campaign', exist_ok=True)
with open('/opt/data/email-campaign/oauth_data.json', 'w') as f:
    json.dump({
        'code_verifier': code_verifier,
        'client_id': cfg['client_id'],
        'client_secret': cfg['client_secret']
    }, f)

# Step 1d: Build authorization URL
params = {
    'response_type': 'code',
    'client_id': cfg['client_id'],
    'redirect_uri': 'http://localhost',
    'scope': 'https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/calendar ...',
    'access_type': 'offline',
    'include_granted_scopes': 'true',
    'code_challenge_method': 'S256',
    'code_challenge': code_challenge,
    'prompt': 'consent',
    'state': secrets.token_urlsafe(16)
}
url = f"{cfg['auth_uri']}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
print(f"🔗 {url}")
```

### Step 2: Exchange the code

When the user returns the redirect URL (containing `?code=...`):

```python
import json, requests

# Load saved verifier
with open('/opt/data/email-campaign/oauth_data.json') as f:
    oauth_data = json.load(f)

# Extract code from URL or use raw code string
code = "4/0AeoWuM8..."  # from the redirect URL

# Exchange
resp = requests.post("https://oauth2.googleapis.com/token", data={
    'code': code,
    'client_id': oauth_data['client_id'],
    'client_secret': oauth_data['client_secret'],
    'redirect_uri': 'http://localhost',
    'grant_type': 'authorization_code',
    'code_verifier': oauth_data['code_verifier']
})
resp.raise_for_status()
token_data = resp.json()
```

### Step 3: Save as google_token.json

```python
import datetime
from datetime import timezone

token_file = {
    'token': token_data['access_token'],
    'refresh_token': token_data.get('refresh_token', ''),
    'token_uri': 'https://oauth2.googleapis.com/token',
    'client_id': oauth_data['client_id'],
    'client_secret': oauth_data['client_secret'],
    'scopes': token_data['scope'].split(),
    'universe_domain': 'googleapis.com',
    'account': '',
    'expiry': (datetime.datetime.now(timezone.utc) + 
               datetime.timedelta(seconds=token_data.get('expires_in', 3600))).isoformat()
}

with open('/opt/data/google_token.json', 'w') as f:
    json.dump(token_file, f, indent=2)
```

## Key Details

- **PKCE code_verifier**: Must be a cryptographically random string of 43-128 URL-safe base64 characters (no padding `=`). Generate with `secrets.token_bytes(32)` → base64.
- **PKCE code_challenge**: SHA-256 hash of verifier, then URL-safe base64 (no padding).
- The **same** code_verifier must be used for both URL generation and token exchange.
- The `redirect_uri` in the auth URL and the token exchange POST **must match exactly**.
- Always use `prompt=consent` to force a refresh_token to be issued.
- Use `include_granted_scopes=true` to preserve previously-granted scopes.

## When to Use This

- The user provided an OAuth code but the standard setup.py flow can't exchange it (stale/failed flow state).
- The OAuth code came from a URL generated in a different turn/session.
- You need to add new scopes to an existing token (just change the scope in the auth URL params — Google will ask for consent for new scopes only).
- The token needs to be fully refreshed with updated scopes.
