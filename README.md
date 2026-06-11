# Hermes Telegram Agent Template

Reusable production deployment template for a Hermes Telegram bot running in polling mode with:

- DeepSeek chat through an OpenAI-compatible AI Gateway
- Telegram allowlist access control
- Image confirmation flow
- `gpt-image-2` image generation through AI Gateway

## Deploy

```sh
git clone <repo-url> hermes-telegram-agent
cd hermes-telegram-agent
cp .env.example .env
```

Edit `.env`:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USER_IDS=
OPENAI_BASE_URL=http://GATEWAY_SERVER_IP:3010/api/gateway
OPENAI_API_KEY=agf_live_xxx
OPENAI_MODEL=deepseek-chat
IMAGE_MODEL=gpt-image-2
IMAGE_CONFIRMATION_REQUIRED=true
```

Hermes uses `TELEGRAM_BOT_TOKEN` as the actual token variable. `BOT_TOKEN` is included in `.env.example` only as a common operator alias.

Replace every `GATEWAY_SERVER_IP` placeholder in both `.env` and `data/config.yaml` with the customer's AI Gateway host or domain:

```sh
grep -R "GATEWAY_SERVER_IP" .env data/config.yaml
```

Start the bot:

```sh
docker compose up -d --build
```

## Test

1. Open the new Telegram bot and send `/start`.
2. Send a normal text prompt and confirm the reply uses `deepseek-chat`.
3. Send an image request, for example: `poster hiigeed uguuch modern coffee shop 1:1`.
4. Confirm the generated summary by replying `тийм`.
5. Verify AI Gateway usage logs show chat and image requests.

## New Customer Checklist

- Create Telegram bot with `@BotFather`.
- Save the Telegram bot token into `TELEGRAM_BOT_TOKEN`.
- Get the customer's numeric Telegram user ID.
- Save that ID into `TELEGRAM_ALLOWED_USER_IDS`.
- Create AI Gateway client credentials.
- Top up the customer's tugrik balance.
- Set `OPENAI_BASE_URL` to the customer's Gateway URL.
- Set `OPENAI_API_KEY` to the customer's Gateway client API key.
- Deploy with `docker compose up -d --build`.
- Test text chat.
- Test image generation.
- Verify Gateway usage log and tugrik deduction.

## Files To Keep Secret

Do not commit real `.env` files, Telegram tokens, Gateway API keys, logs, caches, session dumps, state databases, or `data/image-router-pending.json`.
