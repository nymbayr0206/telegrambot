# Telegram Group Supergroup & Topics Setup

## Why This Matters

Telegram groups that need **Topics** (separate threaded conversations within one group) must be **supergroups**. A regular group cannot use Topics. Hermes cron jobs can deliver messages to specific topics using the `telegram:chat_id:thread_id` format.

## Identifying Group vs Supergroup

| Type | Chat ID Pattern | Example | Topics? |
|------|----------------|---------|---------|
| Regular group | Short negative ID | `-5102303508` | ❌ No |
| Supergroup | ID starts with `-100` | `-1001234567890` | ✅ Yes |

Check via Telegram API:
```python
r = requests.get(f'https://api.telegram.org/bot{TOKEN}/getChat', params={'chat_id': CHAT_ID})
print(r.json()['result']['type'])  # "group" or "supergroup"
```

## Setup Sequence

### Step 1: Convert to Supergroup (if not already)

In the Telegram group:
1. Tap group name → **⋮ (3 dots) → Manage Group**
2. Look for **"Convert to Supergroup"** or **"Upgrade Group"**
3. Confirm the conversion (messages are preserved)
4. The chat ID will change — it will now start with `-100`

### Step 2: Enable Topics

1. **Manage Group → Group Type → Topics → ✅ ON**
2. Create topics using the `#` button at the bottom of the chat

### Step 3: Make Bot an Admin

For a bot to read all messages in a topics-enabled group, it must be an admin:
1. **Manage Group → Administrators → Add Admin**
2. Search for the bot username (e.g. `@Saraa01_bot`)
3. Grant at minimum: **Read Messages**
4. Save

Without admin rights, the bot's permissions show `can_send_messages: false` and it cannot read or respond to group messages reliably.

## Finding the Bot Username

**Do not assume the bot is `@HermesAgent_bot`.** The username depends on what was set up via @BotFather. Always verify:

1. Read the token from `config.yaml` → `platforms.telegram.token`
2. Call `getMe` on the Telegram API:

```bash
curl -s "https://api.telegram.org/bot${TOKEN}/getMe"
```

3. The response contains `result.username` — that's the actual bot handle.

## Cron Delivery to Topics

Once you have the supergroup chat ID and topic thread ID:

```json
{
  "deliver": "telegram:-1001234567890:12345"
}
```

The `thread_id` is the topic's message thread ID. You can discover it by:
1. Having the user send a message in the topic
2. Checking the Hermes gateway logs for `message_thread_id`
3. Or calling `getUpdates` on the Telegram API (if webhook isn't draining them)

## General Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `getChat` returns `can_send_messages: false` | Bot is not an admin | Add as admin with read permissions |
| Topics toggle is grayed out | Group is not a supergroup | Convert to supergroup first |
| Bot doesn't see messages in group | Privacy mode enabled; bot not mentioned | Use `@bot_username` prefix, or make admin |
| Cron delivers to DM instead of group | `deliver` field missing topic thread ID | Use `telegram:chat_id:thread_id` format |
| `send_message(action='list')` doesn't show group | Bot hasn't received any message from that group yet | Have user send `@bot_username hi` in the group |
