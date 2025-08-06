import re

from app.core.constants import ValidationMessages
from app.core.constants.validation import ValidationRegex
from app.core.enums.app_env import AppEnv
from app.core.enums.log_level import LogLevel


# --- Translate .env LOG_LEVEL ---
def validate_log_level_str(value: str | LogLevel) -> LogLevel:
    if isinstance(value, LogLevel):  # Already enum
        return value
    if isinstance(value, str):
        try:
            return LogLevel[value.strip().upper()]  # strip() for safety
        except KeyError:
            raise ValueError(
                ValidationMessages.INVALID_LOG_LEVEL_TEMPLATE.format(
                    value=value, valid_levels=[member.name for member in LogLevel]
                )
            ) from KeyError
    raise ValueError(
        ValidationMessages.INVALID_INPUT_TYPE_LOG_LEVEL_TEMPLATE.format(
            type_value=type(value)
        )
    )


# --- Translate .env APP_ENV ---
def validate_app_env_str(value: str | AppEnv) -> AppEnv:
    if isinstance(value, AppEnv):  # Already enum
        return value
    if isinstance(value, str):
        try:
            return AppEnv[value.strip().upper()]  # strip() for safety
        except KeyError:
            raise ValueError(
                ValidationMessages.INVALID_APP_ENV_TEMPLATE.format(
                    value=value, valid_levels=[member.name for member in AppEnv]
                )
            ) from KeyError
    raise ValueError(
        ValidationMessages.INVALID_INPUT_TYPE_APP_ENV_TEMPLATE.format(
            type_value=type(value)
        )
    )


# --- Phone Number Validation Logic ---
def validate_phone_e164(phone_number: str) -> str:
    if not phone_number:
        raise ValueError(ValidationMessages.PHONE_NUMBER_EMPTY)
    if not re.match(ValidationRegex.PHONE_NUMBER_E164, phone_number):
        raise ValueError(ValidationMessages.INVALID_PHONE_FORMAT_E164)
    return phone_number
