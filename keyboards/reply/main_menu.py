from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поиск фильмов")],
            [KeyboardButton(text="Избранные фильмы")],
            [KeyboardButton(text="Помощь")]
        ],
        resize_keyboard=True
    )
