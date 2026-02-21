from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from keyboards.reply.main_menu import get_main_menu  # ← ПРЯМОЙ ИМПОРТ

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Бот для поиска фильмов!\n"
        "Нажмите 'Поиск фильмов' или /search",
        reply_markup=get_main_menu()
    )

@router.message(Command("help"))
@router.message(F.text == "Помощь")
async def cmd_help(message: Message):
    await message.answer("Введите /search для начала поиска.", reply_markup=get_main_menu())
