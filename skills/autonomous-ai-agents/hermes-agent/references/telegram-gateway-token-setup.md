# Telegram gateway token setup and validation

Use this reference when configuring Hermes Gateway for Telegram.

## Durable lessons

- Bot tokens from @BotFather normally have the shape `<numeric_bot_id>:<secret>`, e.g. `123456789:AA...`. If a user provides only the secret-looking suffix without the numeric prefix and colon, Telegram will reject it with `telegram.error.InvalidToken: Not Found` / `The token ... was rejected by the server`.
- Validate the token shape before writing it into config or restarting the gateway. This avoids leaking the token into gateway logs and avoids noisy retry loops.
- If an invalid token was written and the gateway is retrying, stop the gateway, remove or disable the Telegram config, then ask the user to revoke/regenerate the token in @BotFather.
- Treat any token pasted into chat as exposed. Recommend `/revoke` in @BotFather and use a fresh token.
- Gateway startup may also warn about missing allowlists: `No user allowlists configured. All unauthorized users will be denied.` After the bot connects, configure `TELEGRAM_ALLOWED_USERS`, `GATEWAY_ALLOW_ALL_USERS=true`, or platform allowlists as appropriate.

## Safe workflow

1. Validate token format locally before applying:
   - Must contain a colon.
   - Prefix before colon should be digits.
   - Suffix should be non-empty and look like a BotFather token secret.
2. Configure using `hermes gateway setup` when possible, or set:
   ```yaml
   platforms:
     telegram:
       enabled: true
       token: "<bot_id>:<secret>"
   ```
3. Restart/run gateway and check logs only for redacted or high-level errors.
4. If Telegram rejects the token:
   - Stop the gateway to prevent retry spam.
   - Remove the invalid token from config or set `platforms.telegram.enabled: false`.
   - Tell the user to revoke/regenerate the bot token in @BotFather.
