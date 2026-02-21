from aiogram import Bot
from aiogram.types import BotCommand

async def set_default_commands(bot: Bot):

    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="search", description="Поиск фильмов"),
        BotCommand(command="help", description="Помощь")
    ]
    await bot.set_my_commands(commands)
