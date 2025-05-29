from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    API_V_STR: str = "/api/v1"
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    BACKEND_CORS_ORIGINS: str

    PROJECT_NAME: str
    POSTGRES_SERVER: str
    DATABASE_PORT: int = 5432
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_USER: str


settings = Settings()
