from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states import MovieSearch
from keyboards.inline import get_movies_kb
from keyboards.reply.main_menu import get_main_menu
import requests

user_favorites = {}
router = Router()

@router.message(Command("search"))
@router.message(F.text == "Поиск фильмов")
async def start_search(message: Message, state: FSMContext):
    await message.answer("Введите название фильма:")
    await state.set_state(MovieSearch.waiting_query)

@router.message(MovieSearch.waiting_query)
async def process_query(message: Message, state: FSMContext):
    query = message.text.strip()
    url = f"https://api.tvmaze.com/search/shows?q={query}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        print(f"API ответ: {len(data)} результатов")

        if data and len(data) > 0:
            movies = []
            for item in data[:5]:
                show = item['show']
                title = show.get('name', 'Unknown')
                premiered = show.get('premiered', 'N/A')
                year = premiered[:4] if premiered else 'N/A'
                show_id = show.get('id', '0')

                movies.append({
                    "Title": f"{title} ({year})",
                    "show_id": show_id,
                    "full_title": title
                })

            kb = get_movies_kb(movies)
            await message.answer(f"Найдено: {len(movies)}", reply_markup=kb)
        else:
            await message.answer("Ничего не найдено", reply_markup=get_main_menu())

    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("Ошибка поиска", reply_markup=get_main_menu())

    await state.clear()

@router.callback_query(F.data.startswith("view_"))
async def show_movie_details(callback: CallbackQuery):
    show_id = callback.data.replace("view_", "")

    try:
        url = f"https://api.tvmaze.com/shows/{show_id}"
        response = requests.get(url, timeout=10)
        show = response.json()
        title = show.get('name', 'Unknown')
        year = show.get('premiered', 'N/A')[:4]
        genres = ', '.join(show.get('genres', [])) or 'Не указано'
        status = show.get('status', 'Не указано')
        rating = show.get('rating', {}).get('average', 'N/A')

        text = (
            f"<b>{title}</b> ({year})\n\n"
            f"<b>Жанры:</b> {genres}\n"
            f"<b>Статус:</b> {status}\n"
            f"<b>Рейтинг:</b> {rating}/10\n\n"
            f"ID: <code>{show_id}</code>"
        )

        kb = InlineKeyboardBuilder()
        kb.button(text="Добавить в избранное", callback_data=f"add_fav_{show_id}")
        kb.button(text="Главное меню", callback_data="main_menu")
        kb.adjust(1)

        await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

    except Exception as e:
        await callback.message.edit_text("Ошибка загрузки информации")

    await callback.answer()

@router.callback_query(F.data.startswith("add_fav_"))
async def add_favorite(callback: CallbackQuery):
    show_id = callback.data.replace("add_fav_", "")

    try:
        url = f"https://api.tvmaze.com/shows/{show_id}"
        response = requests.get(url, timeout=5)
        show = response.json()
        title = f"{show.get('name', 'Фильм')} ({show.get('premiered', 'N/A')[:4]})"
    except:
        title = f"Фильм {show_id}"

    user_id = callback.from_user.id
    if user_id not in user_favorites:
        user_favorites[user_id] = []

    if title not in user_favorites[user_id]:
        user_favorites[user_id].append(title)
        await callback.answer(f"{title} добавлено!", show_alert=True)
    else:
        await callback.answer("Уже в избранном!", show_alert=True)

@router.message(F.text == "Избранные фильмы")
async def show_favorites(message: Message):
    user_id = message.from_user.id
    if user_id not in user_favorites or not user_favorites[user_id]:
        await message.answer(
            "<b>Избранное пусто</b>\n\nНайдите фильм и добавьте!",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        return

    favorites_list = [f"• {title[:50]}" for title in user_favorites[user_id][-10:]]
    text = f"<b>Избранное ({len(favorites_list)}):</b>\n\n" + "\n".join(favorites_list)

    await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")

@router.callback_query(F.data == "main_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Главное меню</b>",
        parse_mode="HTML"
    )
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

