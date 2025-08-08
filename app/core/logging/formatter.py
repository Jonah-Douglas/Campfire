from collections.abc import Mapping
import logging
from typing import Any, Literal


class ExtraAwareFormatter(logging.Formatter):
    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style="%",  # noqa: ANN001
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
    ) -> None:
        if fmt is None:
            fmt = "%(message)s"
        super().__init__(
            fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults
        )

    # JD - This can't be overridden without breaking the formatting, leave it commented out for now
    # def formatMessage(self, record: logging.LogRecord) -> str:
    #     return record.getMessage()

    def format(self, record: logging.LogRecord) -> str:
        try:
            return super().format(record)
        except Exception:
            return record.getMessage()


class ColorizingFormatter(logging.Formatter):
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    # Styles
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[%dm"
    # BOLD_SEQ = "\033[1m"

    COLORS = {  # noqa: RUF012
        "WARNING": YELLOW,
        "INFO": WHITE,
        "DEBUG": BLUE,
        "CRITICAL": RED,
        "ERROR": RED,
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool = True,
        validate: bool = True,
        defaults: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults
        )
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        s = super().format(record)

        if self.use_colors and record.levelname in self.COLORS:
            s = (
                (self.COLOR_SEQ % (30 + self.COLORS[record.levelname]))
                + s
                + self.RESET_SEQ
            )

        return s
