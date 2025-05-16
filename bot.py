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
        logging.exception("Ошибка в получении курса")
        await message.answer(f"Произошла ошибка: {str(e)}")


# Создаем хэндлер первого выбора валюты
@dp.message(Command('rates'))
async def cmd_rates(message: types.Message):
    if not message.from_user.id in user_data.keys():
        user_data[message.from_user.id] = None
        await message.answer('Выберите валюту:', reply_markup=VALUTE_BUTTOM)
    else: await message.answer('Конвертер валют уже запущен!')

async def show_currency(message, dataValute: str, confKurs: str, edit: Optional[str] = ''):

    valut_conf = {'USD': 'доллар', 'EUR': 'евро', 'CNY': 'юань'}
    await editMessage_valute(message, valut_conf[dataValute], confKurs, edit)


# Хэндлер обработчик колбэков с action = 'select'
@dp.callback_query(CallbackValuteFactory.filter(F.action == 'select'))
async def cmd_SelectkonvertValute_valute(
        callback: types.CallbackQuery,
        callback_data: CallbackValuteFactory
):
    dataValute = callback_data.valute

    confKurs = await get_APIvalute(callback.message, dataValute)

    user_data[callback.from_user.id] = dataValute

    if dataValute == 'USD':
        await editMessage_valute(callback.message, 'доллар', confKurs)
    elif dataValute == 'EUR':
        await editMessage_valute(callback.message, 'евро', confKurs)
    elif dataValute == 'CNY':
        await editMessage_valute(callback.message, 'юань', confKurs)
    elif dataValute not in ['USD', 'EUR', 'CNY']:
        await callback.message.edit_text("Невалидная валюта", reply_markup=VALUTE_BUTTOM)

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

    print(f"User {user_id} state:", user_data.get(user_id))
    dataValute = user_data.get(callback.from_user.id, 0)
    confKurs = await get_APIvalute(callback.message, str(dataValute))

    if dataValute == 'USD':
        await editMessage_valute(callback.message, 'доллар', confKurs, edit='Обновлено')
    elif dataValute == 'EUR':
        await editMessage_valute(callback.message, 'евро', confKurs, edit='Обновлено')
    elif dataValute == 'CNY':
        await editMessage_valute(callback.message, 'юань', confKurs, edit='Обновлено')
    elif dataValute not in ['USD', 'EUR', 'CNY']:
        await callback.message.edit_text("Невалидная валюта", reply_markup=VALUTE_BUTTOM)

    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())