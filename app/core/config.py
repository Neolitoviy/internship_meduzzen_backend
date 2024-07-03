from functools import lru_cache

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    host: str = os.getenv('HOST')
    port: int = int(os.getenv('PORT'))
    postgres_user: str = os.getenv('POSTGRES_USER')
    postgres_pass: str = os.getenv('POSTGRES_PASS')
    postgres_db: str = os.getenv('POSTGRES_DB')
    postgres_port: int = int(os.getenv('POSTGRES_PORT'))
    redis_host: str = os.getenv('REDIS_HOST')
    redis_port: int = int(os.getenv('REDIS_PORT'))


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
