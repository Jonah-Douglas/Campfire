import logging
from typing import Literal

from app.core.constants.logging import LoggingConstants
from app.core.enums.log_formats import UvicornFormat

LEVEL_COLOR_MAP = {
    logging.DEBUG: LoggingConstants.LogColors.CYAN,
    logging.INFO: LoggingConstants.LogColors.GREEN,
    logging.WARNING: LoggingConstants.LogColors.YELLOW,
    logging.ERROR: LoggingConstants.LogColors.RED,
    logging.CRITICAL: LoggingConstants.LogColors.RED,
}


class UvicornLogColorFormatter(logging.Formatter):
    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool = True,
        format_name: str | None = None,
    ) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.use_colors = use_colors
        self.format_name = format_name
        self._actual_fmt_string = fmt

    def format(self, record: logging.LogRecord) -> str:
        s = super().format(record)

        if not self.use_colors or not record.name.startswith("uvicorn"):
            return s

        color = LEVEL_COLOR_MAP.get(record.levelno)
        if not color:
            return s

        levelname_plain = record.levelname
        colored_levelname = (
            f"{color}{levelname_plain}{LoggingConstants.LogColors.RESET}"
        )

        # Use self.format_name (or self._actual_fmt_string if you prefer to compare against raw format)
        if self.format_name == UvicornFormat.COLORED_DETAILED.name:
            plain_level_section = f"| {levelname_plain} |"
            colored_level_section = f"| {colored_levelname} |"
            if plain_level_section in s:
                s = s.replace(plain_level_section, colored_level_section, 1)
            else:
                s = s.replace(levelname_plain, colored_levelname, 1)
        elif self.format_name == UvicornFormat.COLORED_MINIMAL.name:
            if s.startswith(levelname_plain):
                s = colored_levelname + s[len(levelname_plain) :]
            else:
                s = s.replace(levelname_plain, colored_levelname, 1)
        else:
            s = s.replace(levelname_plain, colored_levelname, 1)
        return s
