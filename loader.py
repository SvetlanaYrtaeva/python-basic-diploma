from aiogram import Dispatcher
from database import init_db
from handlers import default_routers, custom_routers
from utils import set_default_commands

async def on_startup(bot, dp: Dispatcher):
    print("Инициализация бота...")
    await init_db()
    await set_default_commands(bot)

    for router in default_routers + custom_routers:
        dp.include_router(router)
    print("Бот готов к работе!")
