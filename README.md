# Telegram Bot

Minimal Node.js Telegram bot with Docker deployment configuration.

## Configuration

Copy `.env.example` to `.env` on the deployment server and set the required values there. The real `.env` file is intentionally ignored and should not be committed.

After cloning the repository:

```sh
cp .env.example .env
```

Fill in the values for the new Telegram bot:

```env
NODE_ENV=production
API_PROVIDER=custom
API_BASE_URL=http://72.62.197.97:3010/api/gateway
API_MODEL=deepseek-chat
TELEGRAM_BOT_ID=
TELEGRAM_BOT_USERNAME=
BOT_TOKEN=
TELEGRAM_ALLOWED_USER_IDS=
API_KEY=
```

Only `BOT_TOKEN` is required for the minimal bot to start. Create the token with Telegram `@BotFather`.

Safe to keep in `.env.example`: `NODE_ENV`, `API_PROVIDER`, `API_BASE_URL`, `API_MODEL`, `TELEGRAM_BOT_ID`, and `TELEGRAM_BOT_USERNAME`.

Set per server and do not commit real values: `BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_IDS`, and `API_KEY`.

## Run locally

```sh
npm install
npm run build
npm start
```

## Run with Docker Compose

```sh
docker compose up -d --build
```
