const process = require('node:process');
const { Telegraf } = require('telegraf');
require('dotenv').config();

const token = process.env.BOT_TOKEN;

if (!token) {
  console.error('BOT_TOKEN is required. Set it in the .env file or environment.');
  process.exit(1);
}

const bot = new Telegraf(token);

bot.start((ctx) => ctx.reply('Bot is running.'));
bot.command('ping', (ctx) => ctx.reply('pong'));
bot.on('text', (ctx) => ctx.reply('Message received.'));

async function shutdown(signal) {
  console.log(`Received ${signal}. Stopping bot...`);
  bot.stop(signal);
  process.exit(0);
}

process.once('SIGINT', shutdown);
process.once('SIGTERM', shutdown);

bot
  .launch()
  .then(() => {
    console.log('Telegram bot started.');
  })
  .catch((error) => {
    console.error('Telegram bot failed to start:', error.message);
    process.exit(1);
  });
