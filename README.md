# Telegram Bot

Minimal Node.js Telegram bot with Docker deployment configuration.

## Configuration

Copy `.env.example` to `.env` on the deployment server and set the required values there. The real `.env` file is intentionally ignored and should not be committed.

Required variables:

```env
BOT_TOKEN=
NODE_ENV=production
```

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
