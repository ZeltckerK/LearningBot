import asyncio
import logging
from contextlib import suppress

import aiohttp
from typing import Optional

from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram import Dispatcher, Bot, F, types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_reader import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

user_ids = []

class CallbackValuteFactory(CallbackData, prefix='valute'):
    action: str # select or refresh
    valute: Optional[str] = None # указанная валюта

# функция выдачи колбеков
def get_valuteButtom():

    builder = InlineKeyboardBuilder()

    builder.button(
        text='USD', callback_data=CallbackValuteFactory(action='select', valute='USD')
    )
    builder.button(
        text='EUR', callback_data=CallbackValuteFactory(action='select', valute='EUR')
    )
    builder.button(
        text='CNY', callback_data=CallbackValuteFactory(action='select', valute='CNY')
    )
    builder.button(
        text='Обновить', callback_data=CallbackValuteFactory(action='refresh')
    )
    builder.adjust(4)
    return builder.as_markup()

VALUTE_BUTTOM = get_valuteButtom()

# изменяем сообщение с учетом валюты
async def editMessage_valute(message: types.Message, valute: str, valueRu: str):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f'Актуальный курс для {valute}\n'
            f'1 {valute} = {valueRu} рублей',
            reply_markup=VALUTE_BUTTOM)


# Создаем хэндлер первого выбора валюты
@dp.message(Command('rates'))
async def cmd_rates(message: types.Message):
    if not message.from_user.id in user_ids:
        user_ids.append(message.from_user.id)
        await message.answer('Выберите валюту:', reply_markup=VALUTE_BUTTOM)
    else: await message.answer('Конвертер валют уже запущен!')

# Хэндлер обработчик колбэков с action = 'select'
@dp.callback_query(CallbackValuteFactory.filter(F.action == 'select'))
async def cmd_SelectkonvertValute_valute(
        callback: types.CallbackQuery,
        callback_data: CallbackValuteFactory
):
    dataValute = callback_data.valute
    confKurs = None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.cbr-xml-daily.ru/daily_json.js') as request:
                if request.status != 200:
                    raise Exception('Сервер не смог ответить...')
                dataReq = await request.json(content_type=None)
                confKurs = dataReq['Valute'][dataValute]['Value']
    except Exception as e:
        logging.exception("Ошибка в получении курса")
        await callback.message.answer(f"Произошла ошибка: {str(e)}")

    if dataValute == 'USD':
        await editMessage_valute(callback.message, 'доллар', confKurs)
    elif dataValute == 'EUR':
        await editMessage_valute(callback.message, 'евро', confKurs)
    elif dataValute == 'CNY':
        await editMessage_valute(callback.message, 'юань', confKurs)

    await callback.answer()



async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())