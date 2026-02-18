from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline.actions import get_delete_kb, get_search_delete_kb
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database import AsyncSessionLocal, Contact
from states.contacts import ContactStates
from keyboards.reply.main import main_kb
from utils.validators import validate_name, validate_phone

router = Router()

@router.message(F.text == "Добавить контакт")
async def add_contact_start(message: Message, state: FSMContext):
    await message.answer("Введите фамилию контакта (только буквы):")
    await state.set_state(ContactStates.waiting_surname)

@router.message(ContactStates.waiting_surname)
async def process_surname(message: Message, state: FSMContext):
    surname = message.text.strip()
    if not validate_name(surname):
        return await message.answer("Фамилия должна содержать только буквы! Попробуйте снова:")

    await state.update_data(surname=surname)
    await message.answer("Введите имя контакта (только буквы):")
    await state.set_state(ContactStates.waiting_name)


@router.message(ContactStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not validate_name(name):
        return await message.answer("Имя должно содержать только буквы! Попробуйте снова:")

    data = await state.get_data()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Contact).where(
                Contact.user_id == message.from_user.id,
                Contact.name.ilike(f"{data['surname']} {name}%")
            )
        )
        existing_contact = result.scalars().first()

    if existing_contact:
        await message.answer(
            f"КОНТАКТ УЖЕ ЕСТЬ!\n\n"
            f"{existing_contact.name}\n"
            f"{existing_contact.phone}\n"
            f"{existing_contact.email or 'Не указан'}\n\n"
            f"Заменить этот контакт?\n"
            f"Да - введите новый телефон\n"
            f"Нет - отправьте /cancel",
            reply_markup=None
        )
        await state.update_data(name=name, existing_id=existing_contact.id)
        await state.set_state(ContactStates.confirm_replace)
        return

    await state.update_data(name=name)
    await message.answer("Введите отчество (или /skip):")
    await state.set_state(ContactStates.waiting_patronymic)

@router.message(ContactStates.confirm_replace)
async def process_replace(message: Message, state: FSMContext):
    data = await state.get_data()

    if message.text == "/cancel":
        await message.answer("Добавление отменено", reply_markup=main_kb)
        await state.clear()
        return

    try:
        if not validate_phone(message.text.strip()):
            return await message.answer("Неверный формат телефона! Пример: +79991234567")

        async with AsyncSessionLocal() as session:
            contact = await session.get(Contact, data['existing_id'])
            if contact and contact.user_id == message.from_user.id:
                contact.phone = message.text.strip()
                contact.email = None
                await session.commit()
                await session.refresh(contact)

                await message.answer(
                    f"КОНТАКТ ОБНОВЛЕН!\n\n"
                    f"{data['surname']} {data['name']}\n"
                    f"{contact.phone}\n"
                    f"ID: {contact.id}",
                    reply_markup=main_kb
                )
            else:
                await message.answer("Контакт не найден", reply_markup=main_kb)
    except:
        await message.answer("Ошибка обновления", reply_markup=main_kb)

    await state.clear()

@router.message(ContactStates.waiting_patronymic)
async def process_patronymic(message: Message, state: FSMContext):
    data = await state.get_data()
    patronymic = message.text.strip() if message.text != "/skip" else None

    if patronymic and not validate_name(patronymic):
        return await message.answer("Отчество должно содержать только буквы! Попробуйте снова или /skip:")

    await state.update_data(patronymic=patronymic)
    await message.answer("Введите номер телефона (пример: +79991234567):")
    await state.set_state(ContactStates.waiting_phone)

@router.message(ContactStates.waiting_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not validate_phone(phone):
        return await message.answer("Неверный формат! Пример: +79991234567")

    await state.update_data(phone=phone)
    await message.answer("Введите EMAIL (или /skip):")
    await state.set_state(ContactStates.waiting_email)

@router.message(ContactStates.waiting_email)
async def process_email(message: Message, state: FSMContext):
    data = await state.get_data()

    full_name = f"{data['surname']} {data['name']}"
    if data.get('patronymic'):
        full_name += f" {data['patronymic']}"

    async with AsyncSessionLocal() as session:
        contact = Contact(
            user_id=message.from_user.id,
            name=full_name,
            phone=data["phone"],
            email=message.text.strip() if message.text != "/skip" else None
        )
        session.add(contact)
        await session.commit()
        await session.refresh(contact)

    await message.answer(
        f"ДАННЫЕ КОНТАКТА СОХРАНЕНЫ!\n\n"
        f"{full_name}\n"
        f"{data['phone']}\n"
        f"{contact.email or 'Не указан'}\n"
        f"ID: {contact.id}",
        reply_markup=main_kb
    )
    await state.clear()

@router.message(F.text == "Поиск")
async def search_start(message: Message, state: FSMContext):
    await message.answer(
        "ПОИСК КОНТАКТОВ\n\n"
        "• Имя или фамилия\n"
        "• Номер телефона\n\n"
        "Пример: 'Иван', 'Петров', '+79991234567':",
        reply_markup=main_kb
    )
    await state.set_state(ContactStates.waiting_search)

@router.message(ContactStates.waiting_search)
async def process_search(message: Message, state: FSMContext):
    search_term = message.text.strip()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Contact).where(
                Contact.user_id == message.from_user.id,
                Contact.name.ilike(f"%{search_term}%")
                |
                Contact.phone.ilike(f"%{search_term.replace('+', '').replace(' ', '')}%")
            )
        )
        contacts = result.scalars().all()

    if not contacts:
        await message.answer(
            f"Контакты по запросу '{search_term}' не найдены\n"
            "Попробуйте другое имя, фамилию или номер",
            reply_markup=main_kb
        )
        await state.clear()
        return

    text = f"НАЙДЕНО ({len(contacts)}):\n\n"
    for i, contact in enumerate(contacts, 1):
        text += f"{i}. {contact.name}\n   {contact.phone}\n   {contact.id}\n\n"

    if len(text) > 4000:
        text = text[:4000] + "\n... (показаны первые результаты)"

    await message.answer(text, reply_markup=main_kb, parse_mode=None)
    await state.clear()

@router.message(F.text == "Список")
async def list_contacts(message: Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Contact).where(Contact.user_id == message.from_user.id)
        )
        contacts = result.scalars().all()

    if not contacts:
        await message.answer("У вас нет контактов", reply_markup=main_kb)
        return

    text = "ВАШИ КОНТАКТЫ:\n\n"
    for contact in contacts:
        text += f"{contact.name}\n {contact.phone}\n {contact.id}\n\n"

    await message.answer(text, reply_markup=main_kb)

@router.message(F.text == "🗑 Удалить по поиску")
async def delete_search_start(message: Message, state: FSMContext):
    await message.answer(
        "УДАЛЕНИЕ ПО ПОИСКУ\n\n"
        "Введите фамилию, имя или номер телефона:\n"
        "Пример: 'Петров', 'Иван', '+7999'",
        reply_markup=None
    )
    await state.set_state(ContactStates.delete_search)

@router.message(ContactStates.delete_search)
async def process_delete_search(message: Message, state: FSMContext):
    search_term = message.text.strip()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Contact).where(
                Contact.user_id == message.from_user.id,
                Contact.name.ilike(f"%{search_term}%") |
                Contact.phone.ilike(f"%{search_term.replace('+', '').replace(' ', '')}%")
            )
        )
        contacts = result.scalars().all()

    if not contacts:
        await message.answer(
            f"Контакты по '{search_term}' не найдены",
            reply_markup=main_kb
        )
        await state.clear()
        return

    if len(contacts) == 1:
        contact = contacts[0]
        await message.answer(
            f"{contact.name}\n"
            f"{contact.phone}\n"
            f"{contact.id}\n\n"
            f"Удалить этот контакт?",
            reply_markup=get_delete_kb(contact.id, contact.name)
        )
        return

    text = f"НАЙДЕНО ({len(contacts)}):\n\n"
    for i, contact in enumerate(contacts[:10], 1):
        text += f"{i}. {contact.name}\n   {contact.phone}\n\n"

    await message.answer(
        text + "Выберите контакт для удаления:",
        reply_markup=get_search_delete_kb(contacts)
    )

@router.callback_query(F.data.startswith("delete_confirm:"))
async def confirm_delete(callback: CallbackQuery, state: FSMContext):
    contact_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        contact = await session.get(Contact, contact_id)
        if contact and contact.user_id == callback.from_user.id:
            await session.delete(contact)
            await session.commit()

            await callback.message.edit_text(
                f"Контакт удален!\n\n"
                f"{contact.name}\n"
                f"{contact.phone}\n"
                f"{contact.id}"
            )
        else:
            await callback.message.edit_text("Контакт не найден!")

    await callback.answer()
    await state.clear()

@router.callback_query(F.data == "delete_cancel")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Удаление отменено", reply_markup=main_kb)
    await callback.answer()
    await state.clear()

@router.callback_query(F.data.startswith("del_select:"))
async def select_delete(callback: CallbackQuery, state: FSMContext):
    contact_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        contact = await session.get(Contact, contact_id)
        if contact:
            await callback.message.edit_text(
                f"{contact.name}\n"
                f"{contact.phone}\n"
                f"{contact.id}\n\n"
                f"Удалить этот контакт?",
                reply_markup=get_delete_kb(contact.id, contact.name)
            )

    await callback.answer()

@router.callback_query(F.data == "del_back")
async def back_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "УДАЛЕНИЕ ПО ПОИСКУ\n\n"
        "Введите фамилию, имя или номер:",
        reply_markup=None
    )
    await state.set_state(ContactStates.delete_search)
    await callback.answer()
