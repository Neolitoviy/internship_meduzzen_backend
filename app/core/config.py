from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings class handles the application configuration, reading from environment variables.

    Attributes:
    -----------
    host: str
        The host address for the application.
    port: int
        The port number for the application.
    postgres_user: str
        The username for connecting to the PostgreSQL database.
    postgres_pass: str
        The password for connecting to the PostgreSQL database.
    postgres_db: str
        The name of the PostgreSQL database.
    postgres_host: str
        The host address of the PostgreSQL database.
    postgres_port: int
        The port number of the PostgreSQL database.
    redis_host: str
        The host address of the Redis server.
    redis_port: int
        The port number of the Redis server.
    jwt_secret_key: str
        The secret key used for JWT token encoding and decoding.
    jwt_algorithm: str
        The algorithm used for JWT token encoding.
    jwt_access_token_expire_minutes: int
        The expiration time for JWT access tokens, in minutes.
    auth0_domain: str
        The Auth0 domain used for authentication.
    auth0_api_audience: str
        The Auth0 API audience.
    auth0_issuer: str
        The issuer for Auth0 tokens.
    auth0_algorithms: str
        The algorithms used for verifying Auth0 tokens.
    owner: str
        The owner of the token.
        This attribute is used to differentiate between the default JWT token and the Auth0 token.
        If the 'owner' is set in the token, it indicates the use of the default JWT token,
        otherwise, the token is assumed to be from Auth0.
    """

    host: str
    port: int
    postgres_user: str
    postgres_pass: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    redis_host: str
    redis_port: int

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int

    auth0_domain: str
    auth0_api_audience: str
    auth0_issuer: str
    auth0_algorithms: str
    owner: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Constructs the SQLAlchemy database URL from the PostgreSQL settings.

        Returns:
        --------
        str: The SQLAlchemy database URL.
        """
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_pass}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


# Instantiate the settings object
settings = Settings()
