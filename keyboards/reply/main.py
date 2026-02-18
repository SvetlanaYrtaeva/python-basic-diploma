from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить контакт")],
        [KeyboardButton(text="Поиск"), KeyboardButton(text="Список")],
        [KeyboardButton(text="Удалить по поиску")]
    ],
    resize_keyboard=True
)
