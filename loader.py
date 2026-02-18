import logging
from aiogram import Bot, Dispatcher
from config_data.config import settings
from database import init_db

logging.basicConfig(level=logging.INFO)

async def create_dp() -> tuple[Dispatcher, Bot]:
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    return dp, bot

async def on_startup():
    await init_db()
    logging.info("База данных инициализирована")

async def main():
    dp, bot = await create_dp()
    await on_startup()
    await dp.start_polling(bot)
