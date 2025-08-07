from app.core.config import settings
from app.core.constants.logging import LoggingConstants
from app.core.enums.log_formats import LogFormat, UvicornFormat

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "extra_aware_formatter": {
            "()": "app.core.logging.formatter.ExtraAwareFormatter",
            "format": LogFormat.APP_DEFAULT.value,  # Your main app log format
            "datefmt": LoggingConstants.DATE_FORMAT_STRING,
        },
        "uvicorn_colored_minimal_formatter": {
            "()": "app.core.logging.uvicorn_color_formatter.UvicornLogColorFormatter",
            "format": UvicornFormat.COLORED_MINIMAL.value,
            "use_colors": settings.LOG_COLORS_ENABLED,
            "format_name": UvicornFormat.COLORED_MINIMAL.name,
        },
        "uvicorn_colored_detailed_formatter": {
            "()": "app.core.logging.uvicorn_color_formatter.UvicornLogColorFormatter",
            "format": UvicornFormat.COLORED_DETAILED.value,
            "datefmt": LoggingConstants.DATE_FORMAT_STRING,
            "use_colors": settings.LOG_COLORS_ENABLED,
            "format_name": UvicornFormat.COLORED_DETAILED.name,
        },
    },
    "handlers": {
        # Handler for your application's console output
        "console_app": {
            "class": "logging.StreamHandler",
            "formatter": "extra_aware_formatter",  # Use your custom formatter
            "level": settings.LOG_LEVEL.value,  # Get level from settings
            "stream": "ext://sys.stdout",  # Output to standard out
        },
        # Handler for Uvicorn's error and general ASGI messages
        "console_uvicorn_error": {
            "class": "logging.StreamHandler",
            "formatter": "uvicorn_colored_minimal_formatter",
            "level": settings.UVICORN_LOG_LEVEL.value,
            "stream": "ext://sys.stdout",
        },
        "console_uvicorn_access": {
            "class": "logging.StreamHandler",
            "formatter": "uvicorn_colored_minimal_formatter",
            "level": settings.UVICORN_LOG_LEVEL.value,
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        settings.PROJECT_NAME: {
            "handlers": ["console_app"],
            "level": settings.LOG_LEVEL.value,
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console_uvicorn_error"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console_uvicorn_access"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.asgi": {
            "handlers": ["console_uvicorn_error"],
            "level": "INFO",
            "propagate": False,
        },
        # JD TODO: Consider adding twilio to its own formatter if desired
        "twilio.http_client": {
            "handlers": ["console_app"],  # Or a specific handler
            "level": "WARNING",
            "propagate": False,
        },
        "watchfiles": {
            "handlers": ["console_uvicorn_error"],
            "level": "WARNING",
            "propagate": False,
        },
    },
    "root": {  # Optional: Configure the root logger as a fallback
        # If your application and Uvicorn loggers have propagate=False,
        # the root logger won't see their messages.
        # This can be useful for catching logs from libraries that don't have specific loggers configured.
        "handlers": ["console_app"],  # Or a more generic console handler
        "level": settings.LOG_LEVEL.value,  # Or a higher level like "WARNING"
    },
}
