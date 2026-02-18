from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_delete_kb(contact_id: int, contact_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"🗑 Удалить {contact_name[:20]}...",
                callback_data=f"delete_confirm:{contact_id}"
            )
        ],
        [InlineKeyboardButton(text="Отмена", callback_data="delete_cancel")]
    ])

def get_search_delete_kb(contacts: list) -> InlineKeyboardMarkup:
    kb = []
    for contact in contacts[:5]:
        kb.append([
            InlineKeyboardButton(
                text=f"{contact.name[:25]}...",
                callback_data=f"del_select:{contact.id}"
            )
        ])
    kb.append([InlineKeyboardButton(text="Назад", callback_data="del_back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)
