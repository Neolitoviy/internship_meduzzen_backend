from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

path = str(Path().absolute().parent) + "\.env"  # path to env file


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    model_config = SettingsConfigDict(env_file=path, extra="allow")


settings = Settings()