from collections.abc import Mapping
import contextlib
import logging
from typing import Any, Literal


class Formatter(logging.Formatter):
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[%dm"

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
        style: Literal["%", "{", "$"] = "%",  # Default to %-style
        use_colors: bool = True,
        validate: bool = True,
        defaults: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults
        )
        self.use_colors = use_colors

        if not hasattr(self, "_style"):
            raise RuntimeError("Formatter._style was not initialized by base class.")
        if self._fmt is None and style != "$":
            pass

    def formatMessage(self, record: logging.LogRecord) -> str:  # noqa: N802
        """
        Override to substitute %(key)s patterns in the log message string
        itself using items from the 'extra' dictionary, if no positional
        arguments were used for the message.
        """
        message = record.getMessage()

        if "%" in message and not record.args:
            with contextlib.suppress(KeyError, TypeError, ValueError):
                message = message % record.__dict__
        return message

    def _apply_style_formatting(self, record: logging.LogRecord) -> str:
        """
        Private helper to apply the appropriate style formatting (%, {, $)
        to the log record. Assumes self._fmt is not None at this point.
        """
        style_obj = self._style
        s: str

        if isinstance(style_obj, logging.PercentStyle | logging.StrFormatStyle):
            s = style_obj.format(record)
        elif isinstance(style_obj, logging.StringTemplateStyle):
            s = style_obj.substitute(record)
        else:
            if hasattr(style_obj, "substitute"):
                s = style_obj.substitute(record)
            elif hasattr(style_obj, "format"):
                s = style_obj.format(record)
            else:
                try:
                    s = self._fmt % record.__dict__  # type: ignore
                except Exception:
                    s = (
                        record.message
                        + " (Error: Raw formatting failed after style dispatch)"
                    )
        return s

    def format(self, record: logging.LogRecord) -> str:
        # Step 1: Let our formatMessage prepare record.message
        record.message = self.formatMessage(record)

        # Step 2: Handle time formatting (adds record.asctime)
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        # Step 3: Handle exception formatting (adds record.exc_text)
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        # Step 4: Perform the actual formatting.
        s: str
        try:
            if self._fmt is None:
                s = record.message + " (Error: Formatter self._fmt is None)"
            else:
                s = self._apply_style_formatting(record)

        except Exception as e:
            err_msg_context = record.getMessage()
            current_s_val = locals().get("s")
            if not isinstance(current_s_val, str):
                current_s_val = err_msg_context

            s = f"LOG_FORMATTING_ERROR (Style: {type(self._style).__name__}, Exc: {type(e).__name__} - {e}): {current_s_val}"

        # Step 5: Apply color if enabled
        if self.use_colors and record.levelname in self.COLORS:
            if not isinstance(s, str):
                s = str(s)
            s = (
                (self.COLOR_SEQ % (30 + self.COLORS[record.levelname]))
                + s
                + self.RESET_SEQ
            )

        return s
