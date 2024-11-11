import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):

    # App
    APP_NAME:  str = os.environ.get("APP_NAME", "FastAPI")
    DEBUG: bool = bool(os.environ.get("DEBUG", False))

    # PGSql Database Config
    PGSQL_HOST: str = os.environ.get("PGSQL_HOST", '')
    PGSQL_USER: str = os.environ.get("PGSQL_USER", '')
    PGSQL_PASS: str = os.environ.get("PGSQL_PASSWORD", '')
    PGSQL_PORT: int = int(os.environ.get("PGSQL_PORT", 5432))
    PGSQL_DB: str = os.environ.get("PGSQL_DB", 'User')
    DATABASE_URI: str = f"postgresql://{PGSQL_USER}:{PGSQL_PASS}@{PGSQL_HOST}:{PGSQL_PORT}/{PGSQL_DB}?sslmode=require"
    # App Secret Key
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "") 
    REDIS_HOST: str = os.environ.get("REDIS_HOST","")
    REDIS_PORT: int = os.environ.get("REDIS_PORT", 6379)
    REDIS_PASSWORD: str = os.environ.get("REDIS_PASSWORD", "")
    REDIS_DB: int = 0
    REDIS_EXPIRATION_SECONDS: int = 60  # Cache expiration set to 1 minute 
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    


@lru_cache()
def get_settings() -> Settings:
    return Settings()