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
BOT_TOKEN=
TELEGRAM_BOT_ID=
TELEGRAM_BOT_USERNAME=
TELEGRAM_ALLOWED_USER_IDS=
API_KEY=
API_BASE_URL=
API_MODEL=
```

Only `BOT_TOKEN` is required for the minimal bot to start. Create the token with Telegram `@BotFather`. The bot id, username, allowed user ids, and API values are optional placeholders for each deployment.

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
