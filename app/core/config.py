from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.enums.app_env import AppEnv
from app.core.enums.log_level import LogLevel
from app.core.validators import validate_app_env_str, validate_log_level_str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    # --- Contact Info ---
    CONTACT_NAME: str
    CONTACT_URL: str
    CONTACT_EMAIL: str

    # --- API Settings ---
    API_V_STR: str
    LICENSE_NAME: str
    LICENSE_URL: str
    TOKEN_TYPE_BEARER: str
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ROTATE_REFRESH_TOKENS: bool
    OTP_DEFAULT_LENGTH: int
    OTP_HASH_SALT: str
    OTP_EXPIRE_MINUTES: int
    MAX_OTP_ATTEMPTS: int
    BACKEND_CORS_ORIGINS: str

    # --- Environment ---
    APP_ENV: AppEnv = AppEnv.DEV
    LOG_LEVEL: LogLevel = LogLevel.INFO
    DEBUG_OTP_IN_RESPONSE: bool = False

    # --- Postgres Settings ---
    PROJECT_NAME: str
    PROJECT_VERSION: str
    PROJECT_DESCRIPTION: str
    POSTGRES_SERVER: str
    DATABASE_PORT: int = 5432
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_USER: str

    # --- Twilio Settings ---
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_TEST_ACCOUNT_SID: str | None = None  # For development
    TWILIO_TEST_AUTH_TOKEN: str | None = None  # For development
    TWILIO_FROM_PHONE_NUMBER: str | None = None  # Your Twilio phone number
    # Control which credentials to use (True for development, False for production)
    TWILIO_USE_TEST_CREDENTIALS: bool = True

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def validate_log_level_str(cls, v: str | LogLevel) -> LogLevel:
        return validate_log_level_str(v)

    @field_validator("APP_ENV", mode="before")
    @classmethod
    def validate_app_env_str(cls, v: str | AppEnv) -> AppEnv:
        return validate_app_env_str(v)


settings = Settings()  # type: ignore[call-arg]
