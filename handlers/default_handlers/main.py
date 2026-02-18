from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from keyboards.reply.main import main_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в телефонный справочник!\n\n"
        "Выберите действие:",
        reply_markup=main_kb
    )
