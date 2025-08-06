# --- Validation Constants
class ValidationMessages:
    # Log Level Validation
    INVALID_LOG_LEVEL_TEMPLATE = (
        "Invalid log level string: '{value}'. Must be one of {valid_levels}."
    )
    INVALID_INPUT_TYPE_LOG_LEVEL_TEMPLATE = (
        "Invalid input type for LogLevel: {type_value}"
    )

    # App Environment Validation
    INVALID_APP_ENV_TEMPLATE = (
        "Invalid app environment string: '{value}'. Must be one of {valid_levels}."
    )
    INVALID_INPUT_TYPE_APP_ENV_TEMPLATE = "Invalid input type for AppEnv: {type_value}"

    # Phone Number Validation
    PHONE_NUMBER_EMPTY = "Phone number cannot be empty."
    INVALID_PHONE_FORMAT_E164 = "Invalid phone number format. Expected E.164 format (e.g., +11234567890). Actual: {phone_number}"


class ValidationRegex:
    PHONE_NUMBER_E164 = r"^\+[1-9]\d{1,14}$"
