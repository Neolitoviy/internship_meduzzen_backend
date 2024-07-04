from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str
    port: int
    postgres_user: str
    postgres_pass: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    redis_host: str
    redis_port: int

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    @property
    def sqlalchemy_database_url(self) -> str:
        return (f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_pass}@"
                f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}")


settings = Settings()