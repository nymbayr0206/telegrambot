---
name: hubspot-crm
description: HubSpot CRM integration via @hubspot/cli and direct REST API — install CLI, authenticate with Personal Access Key, manage contacts/companies/deals, and read/write CRM data.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
required_commands:
  - npm
metadata:
  hermes:
    tags: [HubSpot, CRM, Contacts, Companies, Deals, API, CLI]
    related_skills: [odoo19-query, zangia-lead-generation]
---

# HubSpot CRM

Set up and use HubSpot CRM through the official CLI or direct REST API. Uses Personal Access Key (PAK) authentication.

## Quick Setup

### 1. Install CLI

The `@hubspot/cli` npm package needs to be installed globally. If you hit EACCES, use `--prefix`:

```bash
npm install -g @hubspot/cli@latest --prefix ~/.local
export PATH="$HOME/.local/bin:$PATH"
```

### 2. Create Personal Access Key (PAK)

The user must create a PAK in their HubSpot account:
1. Open https://app.hubspot.com → ⚙️ Settings → Integrations → Private Apps
2. Create Private App → name it (e.g. "Hermes AI Integration")
3. Grant required scopes (e.g. `crm.objects.contacts.read/write`, `crm.objects.companies.read/write`)
4. Copy the generated Access Token

### 3. Configure CLI Authentication

**Problem:** `hs init` and `hs auth` use interactive prompts (Enquirer) that read from `/dev/tty`, not stdin. Piping input or using `printf` doesn't work.

**Solution:** Write the config file directly at `~/.hscli/config.yml`:

```yaml
defaultPortal: <environment>
portals:
  - name: <environment>
    accountId: <environment>
    personalAccessKey: "<PAK_TOKEN>"
    authType: personalaccesskey
```

The PAK format is `$<env>-<uuid>-<random>`. The environment prefix (e.g. `na2`, `na1`, `eu1`) becomes the portal name and accountId (since accountId wants a string and numeric IDs aren't easily extractable from the PAK alone).

### 4. Verify

```bash
hs doctor
```

The PAK is checked at runtime by the API, not during config validation.

## Direct API Usage (No CLI Needed)

The CLI is optional — you can use the REST API directly with the PAK as a Bearer token:

```bash
# List contacts
curl -s -H "Authorization: Bearer <PAK_TOKEN>" \
  "https://api.hubapi.com/crm/v3/objects/contacts?limit=10"

# Create a contact
curl -s -X POST \
  -H "Authorization: Bearer <PAK_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"properties":{"email":"test@example.com","firstname":"John","lastname":"Doe"}}' \
  "https://api.hubapi.com/crm/v3/objects/contacts"

# List companies
curl -s -H "Authorization: Bearer <PAK_TOKEN>" \
  "https://api.hubapi.com/crm/v3/objects/companies?limit=10"

# List deals
curl -s -H "Authorization: Bearer <PAK_TOKEN>" \
  "https://api.hubapi.com/crm/v3/objects/deals?limit=10"

# Get account info
curl -s -H "Authorization: Bearer <PAK_TOKEN>" \
  "https://api.hubapi.com/account-info/v3/account"
```

## API Endpoints Reference

| Object | List | Create | Update | Delete |
|--------|------|--------|--------|--------|
| Contacts | `/crm/v3/objects/contacts` | POST same URL | PATCH `/crm/v3/objects/contacts/{id}` | DELETE same |
| Companies | `/crm/v3/objects/companies` | POST same URL | PATCH `/crm/v3/objects/companies/{id}` | DELETE same |
| Deals | `/crm/v3/objects/deals` | POST same URL | PATCH `/crm/v3/objects/deals/{id}` | DELETE same |
| Products | `/crm/v3/objects/products` | POST same URL | PATCH `/crm/v3/objects/products/{id}` | DELETE same |
| Search | `/crm/v3/objects/{object}/search` | POST with filter body | — | — |

All endpoints at: `https://api.hubapi.com/{path}`

## Using `hs api` Command

Once the config file is set up at `~/.hscli/config.yml`, the CLI wrapper works:

```bash
# List contacts
hs api /crm/v3/objects/contacts

# Search contacts with filter
hs api /crm/v3/objects/contacts/search -X POST \
  --data '{"filterGroups":[{"filters":[{"propertyName":"email","operator":"EQ","value":"test@example.com"}]}]}'

# Create a contact
hs api /crm/v3/objects/contacts -X POST \
  --data '{"properties":{"email":"test@example.com","firstname":"John"}}'

# Output as JSON
hs api /crm/v3/objects/contacts --json
```

## Using Environment Variables

Set these env vars and use the `--use-env` flag to bypass config file entirely:

- `HUBSPOT_PERSONAL_ACCESS_KEY` — the PAK token
- `HUBSPOT_ACCOUNT_ID` — numeric account/portal ID (required; "na2" doesn't work, must be a number)

```bash
HUBSPOT_PERSONAL_ACCESS_KEY="<PAK>" HUBSPOT_ACCOUNT_ID="123456789" hs api /crm/v3/objects/contacts --use-env
```

## Pitfalls

### ⚠️ PAK Expiration
- PAKs can expire silently — the API returns `"Access token requires new signature"` or `"expired 20600 day(s) ago"` even when the config file looks valid
- **No CLI-side validation** — `hs doctor` fails with generic errors like `Cannot read properties of undefined (reading 'tokenInfo')` when the PAK is bad
- **Fix:** The user must create a **new** Private App in HubSpot settings and generate a fresh PAK. Old tokens cannot be refreshed.

### ⚠️ CLI is Interactive-Only for Auth
- `hs init` and `hs auth` use Enquirer (TTY-only) — cannot automate with pipes/heredocs
- `expect`, `script`, or similar pseudo-TTY wrappers are the only automation path
- **Workaround:** Write `~/.hscli/config.yml` manually (format above)

### ⚠️ Account ID Troubleshooting
- The `--account` flag requires a **numeric** ID, not the env prefix from the PAK
- If you only have the PAK (no numeric portal ID), the config file approach with string `accountId` works, but some CLI commands fail
- Direct API calls with `curl` and Bearer token always work regardless of config format

### ⚠️ CLI Dependencies
- Node.js required (tested with Node 18+)
- Global install via `npm -g` needs `--prefix ~/.local` if `/usr/local` is not writable
- `npm ERR! EACCES` means either use `--prefix` or install with `sudo`

## Hermes Integration Script

For a reusable Hermes skill, write a Python script that calls the HubSpot REST API directly:

```python
import json, subprocess, os

PAK = os.environ.get("HUBSPOT_PAK", "<your-pak>")
BASE = "https://api.hubapi.com"

def hubspot_get(path):
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {PAK}", f"{BASE}{path}"],
        capture_output=True, text=True, timeout=15
    )
    return json.loads(result.stdout)

def hubspot_post(path, data):
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", "-H", f"Authorization: Bearer {PAK}",
         "-H", "Content-Type: application/json", "-d", json.dumps(data),
         f"{BASE}{path}"],
        capture_output=True, text=True, timeout=15
    )
    return json.loads(result.stdout)

# Usage
contacts = hubspot_get("/crm/v3/objects/contacts?limit=5")
```
