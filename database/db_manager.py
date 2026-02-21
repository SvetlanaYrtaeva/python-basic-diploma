import aiosqlite
from config_data.config import config

async def init_db():
    async with aiosqlite.connect(config.db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                query TEXT,
                movie_title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
        print(f"База создана: {config.db_path}")

async def get_db():
    conn = await aiosqlite.connect(config.db_path)
    try:
        yield conn
        await conn.commit()
    finally:
        await conn.close()

async def get_db_session():
    conn = await aiosqlite.connect(config.db_path)
    try:
        yield conn
        await conn.commit()
    finally:
        await conn.close()