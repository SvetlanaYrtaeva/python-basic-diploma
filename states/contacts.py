from aiogram.fsm.state import State, StatesGroup

class ContactStates(StatesGroup):
    waiting_surname = State()
    waiting_name = State()
    waiting_patronymic = State()
    waiting_phone = State()
    waiting_email = State()
    waiting_search = State()
    confirm_replace = State()
    delete_search = State()
