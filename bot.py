import asyncio
import logging

from aiogram import Dispatcher, Bot

from config_reader import config
from handlers.questions import router as questions_router # псевдоним questions_router
from handlers.different_types import router as types_router # псевдоним types_router

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    # Затем регистрируем роутеры в диспетчере
    # С помощью метода include_routers регистрируем хэндлеры
    # Также стоит помнить, что важен порядок регистрации(подробнее в конспекте)
    dp.include_routers(questions_router, types_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())