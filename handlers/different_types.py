from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def cmd_type_text(message: Message):
    await message.answer('Это текстовое сообщение!')

@router.message(F.sticker)
async def cmd_type_sticker(message: Message):
    await message.answer('Это стикер!')

@router.message(F.animation)
async def cmd_type_GIF(message: Message):
    await message.answer('Это GIF!')