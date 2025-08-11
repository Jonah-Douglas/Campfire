import logging
import sys
from types import TracebackType
from typing import Any, Optional

from app.core.config import settings
from app.core.enums.log_levels import LogLevel


class FireLogger:
    """A singleton logger wrapper for the application."""

    _instance: Optional["FireLogger"] = None
    _logger: logging.Logger

    def __new__(cls) -> "FireLogger":
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._logger = logging.getLogger(settings.PROJECT_NAME)
        return cls._instance

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
        if self._logger:
            log_method = getattr(self._logger, level.name.lower(), self._logger.info)

            # Adjust stacklevel:
            # 1 = current frame (_log)
            # 2 = caller of _log (e.g., self.info, self.debug)
            effective_stack_level = 1 + 2 + stack_level_offset

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
            print(f"LOGGER NOT INITIALIZED: {level.name} - {message}", file=sys.stderr)

    def debug(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self._log(LogLevel.DEBUG, message, extra=extra)

    def info(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self._log(LogLevel.INFO, message, extra=extra)

    def warning(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
        exc_info: bool | tuple | BaseException | None = None,
    ) -> None:
        self._log(LogLevel.WARNING, message, extra=extra, exc_info=exc_info)

    def error(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
        exc_info: bool | tuple | BaseException | None = None,
    ) -> None:
        self._log(LogLevel.ERROR, message, extra=extra, exc_info=exc_info)

    def critical(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
        exc_info: bool | tuple | BaseException | None = None,
    ) -> None:
        self._log(LogLevel.CRITICAL, message, extra=extra, exc_info=exc_info)


firelog = FireLogger()
