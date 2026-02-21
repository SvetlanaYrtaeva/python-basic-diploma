from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_movies_kb(movies):
    builder = InlineKeyboardBuilder()
    for movie in movies:
        short_title = movie['Title'][:30]
        builder.button(
            text=f"{short_title}",
            callback_data=f"view_{movie['show_id']}"
        )
    builder.button(text="Главное меню", callback_data="main_menu")
    builder.adjust(1, repeat=True)
    return builder.as_markup()
