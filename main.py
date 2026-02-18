import asyncio
import logging
from handlers import main_router
from loader import create_dp
from database import init_db

logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

async def main() -> None:
    dp, bot = await create_dp()
    await init_db()
    logging.info("База данных готова!")

    dp.include_router(main_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
