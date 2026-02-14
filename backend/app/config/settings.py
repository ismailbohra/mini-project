from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_DIR = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str = "redis://localhost:6379/0"
    LOG_LEVEL: str = "INFO"
    ASSETS_DIR: str = "app/assets"  # Relative to backend root
    model_config = SettingsConfigDict(env_file=ENV_DIR, extra="ignore")


settings = Settings()
