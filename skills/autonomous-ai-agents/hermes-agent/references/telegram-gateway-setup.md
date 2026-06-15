# Telegram Gateway Setup Notes

Concise workflow for connecting Hermes Gateway to Telegram when working from a Hermes source checkout or venv.

## Token format and validation

Telegram BotFather tokens must include the numeric bot id, colon, and secret suffix:

```text
1234567890:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

If the suffix alone is configured, the gateway starts but Telegram rejects it with `telegram.error.InvalidToken: Not Found` / `The token ... was rejected by the server`.

When a user pastes an incomplete or rejected token, tell them to revoke/regenerate it in @BotFather because tokens pasted into chat should be treated as exposed.

## Direct config shape

`gateway.config.load_gateway_config()` reads Telegram credentials from the `platforms.telegram` block in `config.yaml`:

```yaml
platforms:
  telegram:
    enabled: true
    token: "1234567890:AA..."
```

Top-level `telegram:` is for Telegram-specific behavior such as `reactions`, `allowed_chats`, prompts, etc.; do not put the bot token there unless the current implementation explicitly supports it.

## Start / verify loop

From a checkout where `hermes` is not on PATH, use the venv entry point explicitly:

```bash
/opt/hermes/.venv/bin/python /opt/hermes/hermes gateway run
/opt/hermes/.venv/bin/python /opt/hermes/hermes gateway status
```

Verify success by checking gateway logs for lines like:

```text
[Telegram] Connected to Telegram (polling mode)
gateway.run: ✓ telegram connected
```

## Authorization / pairing

### Method 1: Via pairing code (user messages bot first)

If the bot connects but denies users because no allowlist is configured, have the user send any message to the bot. The gateway generates a pairing code. Then use:

```bash
hermes pairing approve telegram <CODE>
```

With a checkout/venv path:

```bash
/opt/hermes/.venv/bin/python /opt/hermes/hermes pairing approve telegram <CODE>
```

After approval, the Telegram user is recognized automatically on their next message.

### Method 2: Pre-authorize by @username (before they message the bot)

When the user says "make X an admin" or "authorize X to talk to me" about someone who hasn't messaged the bot yet, pre-authorize them via the Telegram platform `allowed_chats` config.

**Step 1: Resolve @username → numeric user ID** via the Telegram Bot API:

```python
import json, urllib.request
token = "<BOT_TOKEN>"
username = "target_user"
url = f"https://api.telegram.org/bot{token}/getChat?chat_id=@{username}"
req = urllib.request.Request(url)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
# data["result"]["id"] is the numeric user ID
```

Note: This only works if the user has **messaged the bot at least once** or if the bot is a group admin and the user is in the group. If `getChat` returns `400 Bad Request: chat not found`, you cannot pre-authorize them by username alone — ask the user for the numeric Telegram user ID, or have them message the bot first so a pairing code is generated.

**Step 2: Add the user ID to `allowed_chats`** in config.yaml under `platforms.telegram`:

```yaml
platforms:
  telegram:
    enabled: true
    token: "..."
    allowed_chats:
      - 2036690188       # existing users
      - 123456789        # new user to pre-authorize
```

Edit via `hermes config edit`, then restart the gateway.

**Alternative: allow all users** (only for trusted groups):

```yaml
platforms:
  telegram:
    allowed_chats: []
```

An empty `allowed_chats` array means "allow all chats" — the bot will accept messages from any user. Use with caution.

### Method 3: Find a user ID from a group

If both bot and target user are in the same Telegram group, use `getChatAdministrators` (if user is admin) or inspect the Telegram update payload to find their ID. The bot must be a group admin for this to work reliably.
