---
name: google-workspace
description: "Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python."
version: 1.2.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials (downloaded from Google Cloud Console)
metadata:
  hermes:
    tags: [Google, Gmail, Calendar, Drive, Sheets, Docs, Contacts, Email, OAuth]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [himalaya]
---

# Google Workspace

Gmail, Calendar, Drive, Contacts, Sheets, and Docs — through Hermes-managed OAuth and a thin CLI wrapper. When `gws` is installed, the skill uses it as the execution backend for broader Google Workspace coverage; otherwise it falls back to the bundled Python client implementation.

## References

- `references/gmail-search-syntax.md` — Gmail search operators (is:unread, from:, newer_than:, etc.)
- `references/drive-import-as-doc.md` — Creating Google Docs via Drive import when Docs API is unavailable
- `references/create-google-slides-from-pptx.md` — Creating Google Slides by uploading .pptx via Drive; no slides subcommand exists in google_api.py
- `templates/presentation-builder.py` — Reusable python-pptx helpers (add_bg, add_textbox, add_multi_text, add_card, add_rect) for building brand-consistent presentations programmatically
- `references/header-lookup-technique.md` — Finding Sheets column indices by header name instead of hardcoding positions
- `references/oauth-pkce-manual-exchange.md` — Manual PKCE code exchange when the standard setup.py `--auth-code` flow fails with "Missing code verifier" or stale flow state
- `references/calendar-create-with-reminders.md` — One-shot and two-step patterns for creating a Calendar event with popup reminders (the `calendar create` subcommand does not support inline reminders)
- `references/goal-deadline-accountability.md` — Combining Calendar events + daily cron jobs for personal savings/earnings goal accountability with countdown reminders
- `references/cold-email-prospecting.md` — Mongolian cold email outreach workflow: find company email, draft professional sales pitch, send via Gmail
- `references/token-diagnosis.md` — Step-by-step OAuth token diagnosis: file missing vs expired access_token vs revoked refresh_token, with diagnostic Python snippets

## Scripts

- `scripts/setup.py` — OAuth2 setup (run once to authorize)
- `scripts/google_api.py` — compatibility wrapper CLI. It prefers `gws` for operations when available, while preserving Hermes' existing JSON output contract.

## First-Time Setup

The setup is fully non-interactive — you drive it step by step so it works
on CLI, Telegram, Discord, or any platform.

Define a shorthand first:

```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
```

### Step 0: Check if already set up

```bash
$GSETUP --check
```

If it prints `AUTHENTICATED`, skip to Usage — setup is already done.

### Step 1: Triage — ask the user what they need

Before starting OAuth setup, ask the user TWO questions:

**Question 1: "What Google services do you need? Just email, or also
Calendar/Drive/Sheets/Docs?"**

- **Email only** → They don't need this skill at all. Use the `himalaya` skill
  instead — it works with a Gmail App Password (Settings → Security → App
  Passwords) and takes 2 minutes to set up. No Google Cloud project needed.
  Load the himalaya skill and follow its setup instructions.

- **Email + Calendar** → Continue with this skill, but use
  `--services email,calendar` during auth so the consent screen only asks for
  the scopes they actually need.

- **Calendar/Drive/Sheets/Docs only** → Continue with this skill and use a
  narrower `--services` set like `calendar,drive,sheets,docs`.

- **Full Workspace access** → Continue with this skill and use the default
  `all` service set.

**Question 2: "Does your Google account use Advanced Protection (hardware
security keys required to sign in)? If you're not sure, you probably don't
— it's something you would have explicitly enrolled in."**

- **No / Not sure** → Normal setup. Continue below.
- **Yes** → Their Workspace admin must add the OAuth client ID to the org's
  allowed apps list before Step 4 will work. Let them know upfront.

### Step 2: Create OAuth credentials (one-time, ~5 minutes)

Tell the user:

> You need a Google Cloud OAuth client. This is a one-time setup:
>
> 1. Create or select a project:
>    https://console.cloud.google.com/projectselector2/home/dashboard
> 2. Enable the required APIs from the API Library:
>    https://console.cloud.google.com/apis/library
>    Enable: Gmail API, Google Calendar API, Google Drive API,
>    Google Sheets API, Google Docs API, People API
> 3. Create the OAuth client here:
>    https://console.cloud.google.com/apis/credentials
>    Credentials → Create Credentials → OAuth 2.0 Client ID
> 4. Application type: "Desktop app" → Create
> 5. If the app is still in Testing, add the user's Google account as a test user here:
>    https://console.cloud.google.com/auth/audience
>    Audience → Test users → Add users
> 6. Download the JSON file and tell me the file path
>
> Important Hermes CLI note: if the file path starts with `/`, do NOT send only the bare path as its own message in the CLI, because it can be mistaken for a slash command. Send it in a sentence instead, like:
> `The JSON file path is: /home/user/Downloads/client_secret_....json`

Once they provide the path (including a document-upload path supplied by the gateway, such as `/opt/data/cache/documents/...client_secret...json`), immediately store it:

```bash
$GSETUP --client-secret /path/to/client_secret.json
```

If the user uploads an OAuth JSON while already in this setup flow, do **not** ask what they want done with it — treat it as the requested client-secret file and continue to the auth URL step.

If they paste the raw client ID / client secret values instead of a file path,
write a valid Desktop OAuth JSON file for them yourself, save it somewhere
explicit (for example `~/Downloads/hermes-google-client-secret.json`), then run
`--client-secret` against that file.

### Step 3: Get authorization URL

Use the service set chosen in Step 1 if the installed `setup.py --help` supports service/format flags. Newer skill docs may show:

```bash
$GSETUP --auth-url --services email,calendar --format json
$GSETUP --auth-url --services calendar,drive,sheets,docs --format json
$GSETUP --auth-url --services all --format json
```

However, some installed versions of `scripts/setup.py` only support `--auth-url` with no `--services` or `--format` arguments and always emits a full Workspace consent URL as plain text. Check `$GSETUP --help` first; if those flags are unavailable, run:

```bash
$GSETUP --auth-url
```

This prints the exact auth URL as plain text (or, in newer versions, returns JSON with an `auth_url` field) and may also save it to `~/.hermes/google_oauth_last_url.txt`.

Agent rules for this step:
- Extract the auth URL (plain text output or JSON `auth_url`) and send that exact URL to the user as a single line.
- Tell the user that the browser will likely fail on `http://localhost:1` after approval, and that this is expected.
- Tell them to copy the ENTIRE redirected URL from the browser address bar.
- If the user gets `Error 403: access_denied`, send them directly to `https://console.cloud.google.com/auth/audience` to add themselves as a test user.

### Step 4: Exchange the code

The user will paste back either a URL like `http://localhost:1/?code=4/0A...&scope=...`, a browser error page text containing that full URL (for example Chrome `ERR_UNSAFE_PORT` / "This site can't be reached" output), or just the code string. All are usable: extract the full `http://localhost:1/?...code=...` URL when present and pass it quoted to `--auth-code`. The `--auth-url` step stores a temporary
pending OAuth session locally so `--auth-code` can complete the PKCE exchange
later, even on headless systems:

```bash
$GSETUP --auth-code "THE_URL_OR_CODE_THE_USER_PASTED" --format json
```

If the installed setup script does not support `--format json`, retry without the unsupported flag:

```bash
$GSETUP --auth-code "THE_URL_OR_CODE_THE_USER_PASTED"
```

If `--auth-code` fails because the code expired, was already used, or came from
an older browser tab, it now returns a fresh `fresh_auth_url`. In that case,
immediately send the new URL to the user and have them retry with the newest
browser redirect only.

If `--auth-code` fails with `InvalidGrantError: (invalid_grant) code_verifier or verifier is not needed`, the `setup.py` internal Flow didn't persist the PKCE code_verifier across turns. Do NOT retry `--auth-url` → `--auth-code`. **Use the manual PKCE exchange instead** (see `references/oauth-pkce-manual-exchange.md`):

1. Load the client_secret JSON, generate a code_verifier + code_challenge yourself
2. Save the code_verifier to a known path (e.g. `/opt/data/email-campaign/oauth_data.json`)
3. Construct the auth URL with `redirect_uri=http://localhost` (no port 1)
4. Send it to the user. When they return the redirect URL, extract `?code=` manually
5. Exchange via direct HTTP POST to `https://oauth2.googleapis.com/token` including the saved `code_verifier`
6. Write the resulting `token_data` as `google_token.json` matching the expected credential format

### Step 5: Verify

```bash
$GSETUP --check
```

Should print `AUTHENTICATED`. Setup is complete — token refreshes automatically from now on.

### Notes

- Token is stored at `~/.hermes/google_token.json` and auto-refreshes via `$GSETUP --check` (handles expired access_tokens silently as long as a `refresh_token` is present).
- Pending OAuth session state/verifier are stored temporarily at `~/.hermes/google_oauth_pending.json` until exchange completes.
- If `gws` is installed, `google_api.py` points it at the same `~/.hermes/google_token.json` credentials file. Users do not need to run a separate `gws auth login` flow.
- To revoke: `$GSETUP --revoke`
- **Hermes venv Python shortcut**: On Hermes installations, `/opt/hermes/.venv/bin/python3` has all Google API packages pre-installed. Use it instead of system `python` whenever pip/uv are unavailable or you get `ModuleNotFoundError`. Replace every `python` in the GSETUP and GAPI shorthands with this path.

## Usage

All commands go through the API script. Set `GAPI` as a shorthand. In environments with `pip` available (standard Python installs):

```bash
GAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
```

In pip-less environments (Nix, uv-managed Python, containers), install deps permanently first and prefix everything with `uv run`:

```bash
uv pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
GAPI="uv run python3 /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
```

The `uv run` prefix is also required for `setup.py` commands in such environments — see the Troubleshooting section for the `uv pip install` alternative to `--install-deps`.

### Gmail

```bash
# Search (returns JSON array with id, from, subject, date, snippet)
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"

# Read full message (returns JSON with body text)
$GAPI gmail get MESSAGE_ID

# Send
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"
$GAPI gmail send --to user@example.com --subject "Report" --body "<h1>Q4</h1><p>Details...</p>" --html
$GAPI gmail send --to user@example.com --subject "Hello" --from '"Research Agent" <user@example.com>' --body "Message text"

# Drafts
# If google_api.py has no first-class draft command, use the direct Gmail API recipe in references/gmail-drafts.md.
# Draft creation is useful when the user wants an email saved for later; never send it without explicit confirmation.

# Drafts (if google_api.py has no draft subcommand, use the Python API directly)
python - <<'PY'
import base64, json, sys
from email.message import EmailMessage
sys.path.insert(0, '${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts')
from google_api import build_service
msg = EmailMessage()
msg['To'] = 'user@example.com'      # omit only if user wants to fill it later
msg['Subject'] = 'Subject line'
msg.set_content('Draft body text')
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
service = build_service('gmail', 'v1')
draft = service.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()
print(json.dumps({'status': 'draft_created', 'draft_id': draft.get('id'), 'message_id': draft.get('message', {}).get('id')}, indent=2))
PY

# Reply (automatically threads and sets In-Reply-To)
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."
$GAPI gmail reply MESSAGE_ID --from '"Support Bot" <user@example.com>' --body "Thanks"

# Labels
$GAPI gmail labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD

### Calendar

```bash
# List events (defaults to next 7 days)
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# Create event (ISO 8601 with timezone required)
$GAPI calendar create --summary "Team Standup" --start 2026-03-01T10:00:00-06:00 --end 2026-03-01T10:30:00-06:00
$GAPI calendar create --summary "Lunch" --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z --location "Cafe"
$GAPI calendar create --summary "Review" --start 2026-03-01T14:00:00Z --end 2026-03-01T15:00:00Z --attendees "alice@co.com,bob@co.com"
```

#### Daily calendar-summary or goal-accountability cron

When the user asks for a recurring morning calendar summary, create a Hermes cron job rather than a calendar event. The prompt must be self-contained because cron runs in a fresh session. For this user, default to `Asia/Ulaanbaatar` local time unless specified otherwise.

For **personal goal deadline accountability** (savings targets, pre-event earnings goals), see `references/goal-deadline-accountability.md` — this combines an all-day Calendar event with a daily cron that counts down and asks "Did you earn/save today?"

Example: 09:00 Asia/Ulaanbaatar is `01:00 UTC`, so the cron expression is `0 1 * * *`. Attach this skill and enable at least the `terminal` and `skills` toolsets so the job can query Google Calendar.

Cron prompt shape:
- interpret `today` in the user's timezone
- read Google Calendar only
- include date, event count, local start/end times, titles, locations if present
- say the calendar is clear if no events
- do not create/update/delete events or invite anyone
- do not call `send_message` from inside the cron run; cron final responses are auto-delivered by the scheduler. Put the summary directly in the final answer, and if the cron prompt explicitly asks for silence when there is nothing new, return exactly the configured sentinel (for example `[SILENT]`).

Cron runtime notes:
- Some scheduler environments have `python3` but not `python`. If `python .../setup.py --check` fails with `python: command not found`, retry with `python3` before treating auth as broken.
- If Google API dependencies are missing and `python3 -m pip` is unavailable, run the API scripts through `uv` with temporary dependencies rather than modifying global Python, for example:
  `uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth-httplib2 python /path/to/google-workspace/scripts/setup.py --check`
  and similarly for `google_api.py` calendar/Gmail commands.
- When using `uv run` from inside a Python project checkout, avoid accidentally building the current project as part of the temporary environment. Run from a neutral directory (for example `workdir=/tmp`) and set the correct Hermes home if needed, e.g. `HERMES_HOME=/opt/data uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth-httplib2 python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check`. This preserves the useful `uv` fallback without turning local editable-package build issues into a false Google auth failure.
- When running the `uv run --with ...` fallback from inside a Python project checkout (for example `/opt/hermes`), use a neutral working directory such as `/tmp` and set the correct `HERMES_HOME` if needed. Otherwise `uv` may try to build the current project instead of just running the Google script. Example:
  `cd /tmp && HERMES_HOME=/opt/data uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth-httplib2 python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check`

```bash
# Update an existing event when google_api.py has no update subcommand.
# Prefer IANA timezone IDs for local-time edits (e.g. Asia/Ulaanbaatar) instead of converting to UTC.
python - <<'PY'
import json, sys
sys.path.insert(0, '${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts')
from google_api import build_service
service = build_service('calendar','v3')
event = service.events().patch(calendarId='primary', eventId='EVENT_ID', body={
    'start': {'dateTime': '2026-03-01T12:00:00', 'timeZone': 'Asia/Ulaanbaatar'},
    'end': {'dateTime': '2026-03-01T13:00:00', 'timeZone': 'Asia/Ulaanbaatar'},
}).execute()
print(json.dumps({'status':'updated','id':event.get('id'),'start':event.get('start'),'end':event.get('end')}))
PY

# Add/replace reminders (example: popup 15 minutes before)
python - <<'PY'
import json, sys
sys.path.insert(0, '${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts')
from google_api import build_service
event = build_service('calendar','v3').events().patch(
    calendarId='primary', eventId='EVENT_ID',
    body={'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 15}]}}
).execute()
print(json.dumps({'status':'updated','id':event.get('id'),'reminders':event.get('reminders')}))
PY

# Delete event
$GAPI calendar delete EVENT_ID
```

### Drive

```bash
# Search existing files
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5

# Get metadata for a single file
$GAPI drive get FILE_ID

# Upload a local file (auto-detects MIME type)
$GAPI drive upload /path/to/report.pdf
$GAPI drive upload /path/to/image.png --name "Logo.png" --parent FOLDER_ID

# Download (binary files download as-is; Google-native files export to a
# sensible default — Docs→pdf, Sheets→csv, Slides→pdf, Drawings→png)
$GAPI drive download FILE_ID
$GAPI drive download DOC_ID --output ~/doc.pdf
$GAPI drive download DOC_ID --export-mime text/plain --output ~/doc.txt

# Create a folder
$GAPI drive create-folder "Reports"
$GAPI drive create-folder "Q4" --parent FOLDER_ID

# Share
$GAPI drive share FILE_ID --email alice@example.com --role reader
$GAPI drive share FILE_ID --email alice@example.com --role writer --notify
$GAPI drive share FILE_ID --type anyone --role reader        # anyone with link
$GAPI drive share FILE_ID --type domain --domain example.com --role reader

# Delete — defaults to trash (reversible). Use --permanent to skip the trash.
$GAPI drive delete FILE_ID
$GAPI drive delete FILE_ID --permanent
```

### Contacts

```bash
$GAPI contacts list --max 20
```

### Sheets

```bash
# Create a new spreadsheet
$GAPI sheets create --title "Q4 Budget"
$GAPI sheets create --title "Inventory" --sheet-name "Stock"

# Read
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# Write
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'

# Append rows
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'
```

**Batch writing large datasets (100+ rows):** The Sheets API accepts rows in a single write, but very large payloads (200+ rows x 6+ columns) can hit request limits. Split into batches of ~100 rows each when writing 300+ entries. Use the Python API directly (`build_service('sheets', 'v4')`) to write batches sequentially, computing range strings per batch (e.g., `Sheet1!A2:F101`, `Sheet1!A102:F201`).

### Docs

```bash
# Read
$GAPI docs get DOC_ID

# Create a new Doc (optionally seeded with body text)
$GAPI docs create --title "Meeting Notes"
$GAPI docs create --title "Draft" --body "First paragraph..."

# Append text to the end of an existing Doc
$GAPI docs append DOC_ID --text "Additional content to append"
```

## Output Format

All commands return JSON. Parse with `jq` or read directly. Key fields:

- **Gmail search**: `[{id, threadId, from, to, subject, date, snippet, labels}]`
- **Gmail get**: `{id, threadId, from, to, subject, date, labels, body}`
- **Gmail send/reply**: `{status: "sent", id, threadId}`
- **Calendar list**: `[{id, summary, start, end, location, description, htmlLink}]`
- **Calendar create**: `{status: "created", id, summary, htmlLink}`
- **Drive search**: `[{id, name, mimeType, modifiedTime, webViewLink}]`
- **Drive get**: `{id, name, mimeType, modifiedTime, size, webViewLink, parents, owners}`
- **Drive upload**: `{status: "uploaded", id, name, mimeType, webViewLink}`
- **Drive download**: `{status: "downloaded", id, name, path, mimeType}`
- **Drive create-folder**: `{status: "created", id, name, webViewLink}`
- **Drive share**: `{status: "shared", permissionId, fileId, role, type}`
- **Drive delete**: `{status: "trashed" | "deleted", fileId, permanent}`
- **Contacts list**: `[{name, emails: [...], phones: [...]}]`
- **Sheets get**: `[[cell, cell, ...], ...]`
- **Sheets create**: `{status: "created", spreadsheetId, title, spreadsheetUrl}`
- **Docs create**: `{status: "created", documentId, title, url}`
- **Docs append**: `{status: "appended", documentId, inserted_at, characters}`

## Rules

1. **Never send email, create/delete calendar events, delete Drive files, share files, or modify Docs/Sheets without confirming with the user first.** Show what will be done (recipients, file IDs, content, share role) and ask for approval. For `drive delete`, prefer the default trash (reversible) over `--permanent`.
2. **Check auth before first use** — run `setup.py --check`. If it fails, guide the user through setup.
3. **Use the Gmail search syntax reference** for complex queries — load it with `skill_view("google-workspace", file_path="references/gmail-search-syntax.md")`.
4. **Calendar times must include timezone** — always use ISO 8601 with offset (e.g., `2026-03-01T10:00:00-06:00`) or UTC (`Z`). For user-facing "tomorrow at noon" requests, first resolve the user's local timezone; do not default to the server timezone/UTC unless the user explicitly wants UTC. When updating local-time events, prefer Calendar API `timeZone` with an IANA ID (for example `Asia/Ulaanbaatar`) so the event displays at the intended wall-clock time.
5. **For meeting reminders, use Calendar events with popup reminders, not cron jobs.** When the user says "remind me about a meeting at X time", create a Calendar event (even a short one) with a popup reminder via `reminders` patch. Users expect calendar-native push notifications on their phone, not a chat message. Only fall back to cron jobs for recurring daily briefings, goal-accountability prompts ("Did you earn/save today?"), or when the user explicitly asks for a Telegram/Discord chat message reminder.
6. **Respect rate limits** — avoid rapid-fire sequential API calls. Batch reads when possible.

## Troubleshooting

For permission-denied errors from the *agent layer* (not Google OAuth), see `references/permission-denied-workarounds.md`.

| Problem | Fix |
|---------|-----|
| `NOT_AUTHENTICATED` | Run setup Steps 2-5 above |
| `REFRESH_FAILED` | Token expired or revoked. Run `$GSETUP --check` first (auto-refreshes if refresh_token still valid). If that fails, diagnose with `references/token-diagnosis.md` — a manual refresh attempt via Python confirms whether the refresh_token itself is dead vs the access_token just needs refreshing. If dead, `$GSETUP --revoke` then redo Steps 3-5. |
| `HttpError 403: Insufficient Permission` | Missing API scope — `$GSETUP --revoke` then redo Steps 3-5 |
| `AUTHENTICATED (partial)` or "Token missing scopes" | New write capabilities (Drive write/delete, Docs create/edit) require re-authorization. `$GSETUP --revoke` then redo Steps 3-5 to grant the upgraded scopes. |
| `HttpError 403: Access Not Configured` or `Google Docs API has not been used` | API not enabled — user needs to enable it in Google Cloud Console. **Workaround while waiting:** use Drive import to create docs — see `references/drive-import-as-doc.md`. **Note:** Drive import creates the Doc but you still need the Docs API for formatting (headings, tables, etc.). If Docs API is truly disabled, even `documents().get()` fails on the imported doc. |
| `InvalidGrantError: (invalid_grant) Missing code verifier` | PKCE code_verifier was not persisted from auth URL generation. See `references/oauth-pkce-manual-exchange.md` for manual exchange technique. |
| `InvalidGrantError: (invalid_grant) code_verifier or verifier is not needed` | setup.py's internal Flow state went stale between auth-url and auth-code turns. Do NOT retry the standard flow — use the manual PKCE exchange instead (see `references/oauth-pkce-manual-exchange.md`): generate your own PKCE values, save code_verifier to a temp file, construct auth URL by hand, exchange via HTTP POST. The session transcript from 2026-06-05 has a complete working example. |
| `ModuleNotFoundError` | Run `$GSETUP --install-deps`. If that fails because `pip` is unavailable (e.g. Nix-based Python), install deps via `uv` instead: `uv pip install google-api-python-client google-auth-oauthlib google-auth-httplib2`. Then prefix all commands with `uv run python3` instead of bare `python`, or use the `uv run --with ...` ephemeral pattern shown in the Cron runtime notes below. **Alternative: use the Hermes venv python** which has these packages pre-installed: `/opt/hermes/.venv/bin/python3`. Replace `python` or `python3` with this full path in any GAPI commands or Python snippets. |
| Google Drive/Docs/Calendar was working but suddenly stopped / app asks for setup again | The **access_token** expired. If the token file still has a valid `refresh_token`, run `$GSETUP --check` — the script auto-refreshes the token silently. Use the correct Python: `/opt/hermes/.venv/bin/python3` if system `pip` is unavailable. Check `expiry` field in `google_token.json` to confirm. Do NOT jump to full re-auth — try `--check` first. |

## Revoking Access

```bash
$GSETUP --revoke
```
