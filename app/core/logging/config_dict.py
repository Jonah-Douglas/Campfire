from app.core.config import settings
from app.core.constants.logging import LoggingConstants
from app.core.enums.log_formats import LogFormat, UvicornFormat

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # Main Campfire logs formatter
        "color_formatter": {
            "()": "app.core.logging.formatter.ColorizingFormatter",
            "fmt": LogFormat.APP_DEFAULT.value,
            "datefmt": LoggingConstants.DATE_FORMAT_STRING,
            "use_colors": settings.LOG_COLORS_ENABLED,
        },
        "extra_aware_formatter": {
            "()": "app.core.logging.formatter.ExtraAwareFormatter",
            "fmt": LogFormat.APP_DEFAULT.value,
            "datefmt": LoggingConstants.DATE_FORMAT_STRING,
        },
        "uvicorn_colored_minimal_formatter": {
            "()": "app.core.logging.uvicorn_color_formatter.UvicornLogColorFormatter",
            "fmt": UvicornFormat.COLORED_MINIMAL.value,
            "use_colors": settings.LOG_COLORS_ENABLED,
            "format_name": UvicornFormat.COLORED_MINIMAL.name,
        },
        "uvicorn_colored_detailed_formatter": {
            "()": "app.core.logging.uvicorn_color_formatter.UvicornLogColorFormatter",
            "fmt": UvicornFormat.COLORED_DETAILED.value,
            "datefmt": LoggingConstants.DATE_FORMAT_STRING,
            "use_colors": settings.LOG_COLORS_ENABLED,
            "format_name": UvicornFormat.COLORED_DETAILED.name,
        },
    },
    "handlers": {
        "console_colored": {
            "class": "logging.StreamHandler",
            "formatter": "color_formatter",
            "level": settings.LOG_LEVEL.value,
            "stream": "ext://sys.stdout",
        },
        # Handler for Application's console output
        "console_app": {
            "class": "logging.StreamHandler",
            "formatter": "extra_aware_formatter",  # Custom formatter
            "level": settings.LOG_LEVEL.value,
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
            "handlers": ["console_colored"],
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
    "root": {
        "handlers": ["console_app"],  # Or a more generic console handler
        "level": settings.LOG_LEVEL.value,
    },
}
