from collections.abc import Mapping
import logging
from typing import Any


class ExtraAwareFormatter(logging.Formatter):
    """
    A logging formatter that allows 'extra' dictionary items to be used
    for %-style formatting within the log message string itself.
    """

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style="%",  # noqa: ANN001
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def formatMessage(self, record: logging.LogRecord) -> str:  # noqa: N802
        msg = record.getMessage()

        try:
            if "%" in msg and record.__dict__ != record.args:
                formatted_msg = msg % record.__dict__
                return formatted_msg
        except (KeyError, TypeError, ValueError):
            pass

        return msg

    def format(self, record: logging.LogRecord) -> str:
        # Rely on base class for final formatting
        return super().format(record)
