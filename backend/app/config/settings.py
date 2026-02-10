from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_DIR = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    model_config = SettingsConfigDict(env_file=ENV_DIR, extra="ignore")


settings = Settings()
