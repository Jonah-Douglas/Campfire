import logging
from logging.handlers import RotatingFileHandler
import sys
from types import TracebackType
from typing import Any, Optional

from app.core.config import settings
from app.core.enums.log_level import LogLevel


# --- Logging Wrapper ---
class Logger:
    _instance: Optional["Logger"] = None
    _logger: logging.Logger | None = None

    LOG_FORMAT = "%(levelname)s | %(asctime)s | %(name)s | %(module)s.%(funcName)s:%(lineno)d | %(message)s"
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __new__(cls) -> "Logger":
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._configure_logger()
        return cls._instance

    def _configure_logger(
        self,
        logger_name: str = settings.PROJECT_NAME,
        log_to_console: bool = True,
        log_to_file: bool = False,
        log_file_path: str = "app.log",
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
    ) -> None:
        """Configures the underlying Python logger."""
        if Logger._logger is not None:
            return

        effective_log_level_enum = settings.LOG_LEVEL
        Logger._logger = logging.getLogger(logger_name)
        Logger._logger.setLevel(effective_log_level_enum.value)

        formatter = logging.Formatter(self.LOG_FORMAT, datefmt=self.DATE_FORMAT)

        handlers = []
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            handlers.append(console_handler)

        if log_to_file:
            file_handler = RotatingFileHandler(
                log_file_path, maxBytes=max_bytes, backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)

        if not handlers:
            logging.basicConfig(
                level=effective_log_level_enum.value,
                format=self.LOG_FORMAT,
                datefmt=self.DATE_FORMAT,
            )
            Logger._logger = logging.getLogger(logger_name)
        else:
            for handler in handlers:
                Logger._logger.addHandler(handler)
            Logger._logger.propagate = (
                False  # Prevent duplicate logs if root logger also has handlers
            )

    def _log(
        self,
        level: LogLevel,
        message: str,
        extra: dict[str, Any] | None = None,
        exc_info: bool
        | tuple[type[BaseException], BaseException, TracebackType | None]
        | BaseException
        | None = None,
        stack_level_offset: int = 0,
    ) -> None:
        # --- Stack Levels ---
        # 1 = current frame (_log)
        # 2 = caller of _log (e.g., self.info, self.debug)
        # 3 = caller of self.info (e.g., the function in main.py or your service)

        if Logger._logger:
            # The 'extra' dictionary can be used to pass additional context
            # that can be incorporated into log formats or processed by structured logging.
            log_method = getattr(
                Logger._logger, level.name.lower(), Logger._logger.info
            )

            effective_stack_level = (
                1 + 2 + stack_level_offset
            )  # 1 (current) + 2 (our wrappers) + any additional offset

            if extra:
                log_method(
                    message,
                    extra=extra,
                    exc_info=exc_info,
                    stacklevel=effective_stack_level,
                )
            else:
                log_method(message, exc_info=exc_info, stacklevel=effective_stack_level)
        else:
            # Fallback if logger somehow not initialized, though __new__ should handle this
            print(f"LOGGER NOT INITIALIZED: {level.name} - {message}", file=sys.stderr)

    def debug(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self._log(LogLevel.DEBUG, message, extra=extra)

    def info(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self._log(LogLevel.INFO, message, extra=extra)

    def warning(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
        exc_info: bool
        | tuple[type[BaseException], BaseException, TracebackType | None]
        | BaseException
        | None = None,
    ) -> None:
        self._log(LogLevel.WARNING, message, extra=extra, exc_info=exc_info)

    def error(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
        exc_info: bool
        | tuple[type[BaseException], BaseException, TracebackType | None]
        | BaseException
        | None = None,
    ) -> None:
        self._log(LogLevel.ERROR, message, extra=extra, exc_info=exc_info)

    def critical(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
        exc_info: bool
        | tuple[type[BaseException], BaseException, TracebackType | None]
        | BaseException
        | None = None,
    ) -> None:
        self._log(LogLevel.CRITICAL, message, extra=extra, exc_info=exc_info)


firelog = Logger()
