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

user_data = {}

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

# Создаем хэндлер первого выбора валюты
@dp.message(Command('rates'))
async def cmd_rates(message: types.Message):
    if not message.from_user.id in user_data.keys():
        user_data[message.from_user.id] = None
        await message.answer('Выберите валюту:', reply_markup=VALUTE_BUTTOM)
    else: await message.answer('Конвертер валют уже запущен!')


# изменяем сообщение с учетом валюты
async def editMessage_valute(message: types.Message, valute: str, valueRu: str, edit: Optional[str] = ''):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f'Актуальный курс для {valute} {edit}\n'
            f'1 {valute} = {valueRu} рублей',
            reply_markup=VALUTE_BUTTOM)

# Вынесем получение данных из API в отдельную функцию
async def get_APIvalute(message: types.Message, dataValute: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.cbr-xml-daily.ru/daily_json.js') as request:
                if request.status != 200:
                    raise Exception('Сервер не смог ответить...')
                dataReq = await request.json(content_type=None)
                confKurs = dataReq['Valute'][dataValute]['Value']
                return confKurs
    except Exception as e:
        logging.exception(f"Произошла ошибка: {str(e)}")
        await message.answer('Что то пошло не так, попробуйте позже...')


async def show_currency(message, dataValute: str, edit: Optional[str] = ''):
    confKurs = await get_APIvalute(message, dataValute)
    valut_conf = {'USD': 'доллар', 'EUR': 'евро', 'CNY': 'юань'}
    await editMessage_valute(message, valut_conf[dataValute], confKurs, edit)


# Хэндлер обработчик колбэков с action = 'select'
@dp.callback_query(CallbackValuteFactory.filter(F.action == 'select'))
async def cmd_SelectkonvertValute_valute(
        callback: types.CallbackQuery,
        callback_data: CallbackValuteFactory
):
    dataValute = callback_data.valute
    user_data[callback.from_user.id] = dataValute

    await show_currency(callback.message, dataValute)

    await callback.answer()

@dp.callback_query(CallbackValuteFactory.filter(F.action == 'refresh'))
async def cmd_RefreshkonvertValute_valute(
        callback: types.CallbackQuery
):
    user_id = callback.from_user.id

    if user_id not in user_data or user_data[user_id] is None:
        with suppress(TelegramBadRequest):
            await callback.message.edit_text('Сначала выберите валюту', reply_markup=VALUTE_BUTTOM)
        return

    dataValute = user_data.get(callback.from_user.id, 0)

    await show_currency(callback.message, str(dataValute), edit='(Обновлено)')

    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())