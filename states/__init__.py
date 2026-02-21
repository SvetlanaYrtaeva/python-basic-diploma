from aiogram.fsm.state import State, StatesGroup

class MovieSearch(StatesGroup):
    waiting_query = State()
    waiting_year = State()

__all__ = ["MovieSearch"]
