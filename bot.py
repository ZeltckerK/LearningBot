import asyncio
import logging

from aiogram import Dispatcher, Bot

from config_reader import config

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())