from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    bot_token: str
    omdb_api_key: str = "2c27184b"
    db_path: str = "./movies.db"
    tmdb_api_key: str = "5TT5AJ0-GCYM1VH-MR5SJGQ-9WPMJEP"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False
    )

config = Config()
