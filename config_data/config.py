from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    bot_token: str
    db_path: Path = Path("./contacts.db")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
