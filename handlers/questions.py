from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.for_questions import get_bool_keyboard

router = Router()  # [1]

@router.message(Command("start"))  # [2]
async def cmd_start(message: Message):
    await message.answer(
        "Вы довольны своей работой?",
        reply_markup=get_bool_keyboard()
    )

@router.message(F.text.lower() == "да")
async def answer_yes(message: Message):
    await message.answer(
        "Это здорово!",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "нет")
async def answer_no(message: Message):
    await message.answer(
        "Жаль...",
        reply_markup=ReplyKeyboardRemove()
    )