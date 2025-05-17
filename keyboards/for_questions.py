from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_bool_keyboard() -> ReplyKeyboardMarkup:
    bd = ReplyKeyboardBuilder()
    bd.button(text='Да')
    bd.button(text='Нет')
    bd.adjust(2)
    return bd.as_markup(resize_keyboard=True)
