from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base, Contact

def get_db_url():
    from config_data.config import settings
    return f"sqlite+aiosqlite:///{settings.db_path}"

engine = create_async_engine(get_db_url())
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

__all__ = ["engine", "AsyncSessionLocal", "init_db", "Contact", "Base"]
