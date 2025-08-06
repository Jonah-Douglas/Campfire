from collections.abc import Callable
import inspect
from typing import Any, NoReturn

from fastapi import HTTPException

from app.core.enums.log_level import LogLevel
from app.core.logging_config import firelog


def _get_caller_method_name() -> str:
    """Attempts to inspect the call stack to find the calling method's name."""
    try:
        current_py_frame = inspect.currentframe()
        if current_py_frame:
            caller_of_outer_func_frame = (
                current_py_frame.f_back.f_back if current_py_frame.f_back else None
            )
            if caller_of_outer_func_frame:
                return caller_of_outer_func_frame.f_code.co_name
            return "unknown_method_no_caller"  # log_and_raise_http_exception was called from top level
        return "unknown_method_no_current_frame"
    except Exception:
        return "unknown_method_inspection_error"


def _get_caller_service_name() -> str:
    """
    Attempts to inspect the call stack to find a service name from the calling instance.
    Looks for _SERVICE_NAME attribute or falls back to class name.
    """
    try:
        current_py_frame = inspect.currentframe()
        if not current_py_frame:
            return "unknown_service_no_current_frame"

        direct_caller_frame = current_py_frame.f_back
        if not direct_caller_frame:
            return "unknown_service_direct_caller_missing"

        original_caller_frame = direct_caller_frame.f_back
        if not original_caller_frame:
            return (
                "unknown_service_no_caller_or_no_self"  # log_and_raise called from top
            )

        if "self" in original_caller_frame.f_locals:
            instance_self = original_caller_frame.f_locals["self"]

            # Attempt 1: Get _SERVICE_NAME attribute
            service_name_val = getattr(instance_self, "_SERVICE_NAME", None)
            if isinstance(service_name_val, str):
                return service_name_val

            # Attempt 2: Fallback to class name
            if hasattr(instance_self, "__class__") and hasattr(
                instance_self.__class__, "__name__"
            ):
                class_name = instance_self.__class__.__name__
                if isinstance(class_name, str):
                    return class_name

            return "unknown_service_no_identifier"  # Has self, but no _SERVICE_NAME or class name

        # "self" not in f_locals (e.g., called from a staticmethod, classmethod, or function)
        return "unknown_service_no_self_in_caller"

    except Exception:
        return "unknown_service_inspection_error"


def _format_log_message(
    template: str | None,
    effective_context: dict[str, Any],
    default_context_str_parts: list[str],
    default_detail_msg: str,
    default_status_code: int,
) -> str:
    """Formats the log message using a template or a default structure."""
    if template:
        return template.format(**effective_context)

    # Default formatting if no template is provided
    additional_context_parts = []
    base_keys_for_default_msg = {
        "service_name",
        "method_name",
        "status_code",
        "detail_msg",
    }
    for k, v in effective_context.items():
        if k not in base_keys_for_default_msg:
            additional_context_parts.append(f"{k}='{v}'")

    full_context_str = ", ".join(default_context_str_parts + additional_context_parts)
    return f'{full_context_str} | Raising HTTPException: Status {default_status_code}, Detail: "{default_detail_msg}"'


def _prepare_log_invocation_args(
    final_log_message: str,
    additional_log_info: dict[str, Any] | None,
    actual_service_name: str,
    actual_method_name: str,
    include_exc_info: bool,
    log_level_name: str,
) -> tuple[list[Any], dict[str, Any]]:
    """Prepares positional and keyword arguments for the logger call."""
    log_args = [final_log_message]
    log_kwargs: dict[str, Any] = {}

    # Default extra info
    current_extra = {
        "service_name": actual_service_name,
        "method_name": actual_method_name,
    }
    if additional_log_info:
        current_extra.update(additional_log_info)
    log_kwargs["extra"] = current_extra

    if include_exc_info and log_level_name in ["warning", "error", "critical"]:
        log_kwargs["exc_info"] = True

    return log_args, log_kwargs


def log_and_raise_http_exception(
    *,
    status_code: int,
    detail: str,
    log_level: LogLevel,
    service_name: str | None = None,
    method_name: str | None = None,
    log_message_template: str | None = None,
    log_context_params: dict[str, Any] | None = None,
    additional_log_info: dict[str, Any] | None = None,
    include_exc_info: bool = False,
) -> NoReturn:
    """
    Logs a message using the global 'firelog' instance and then raises an HTTPException.
    It calls the appropriate method on firelog (e.g., firelog.warning, firelog.error)
    based on the LogLevel enum.

    Args:
        status_code: HTTP status code for the exception.
        detail: Detail message for the HTTPException (sent to the client).
        log_level: The app.core.enums.log_level.LogLevel enum member.
        log_message_template: Optional custom f-string style template for the log message.
        log_context_params: Dictionary of parameters to format the log_message_template.
        additional_log_info: Optional dictionary of extra key-value pairs to pass as 'extra'
                               to the firelog methods for structured logging.
        include_exc_info: If True, exception information (stack trace) is passed to
                           the logger method (typically for warning, error, critical).
    """

    actual_method_name = method_name or _get_caller_method_name()
    actual_service_name = service_name or _get_caller_service_name()

    level_name_str = log_level.name.lower()
    log_method_on_firelog: Callable[..., None] | None = getattr(
        firelog, level_name_str, None
    )

    effective_include_exc_info = include_exc_info
    if not callable(log_method_on_firelog):
        # Fallback logging if the specified log_level is invalid
        firelog.error(
            f"Invalid log_level name '{level_name_str}' for {actual_service_name}.{actual_method_name}. "
            f"Falling back to ERROR for original detail: {detail}",
            extra={
                "service_name": actual_service_name,
                "method_name": actual_method_name,
            },
            exc_info=True,  # Always include exc_info for this fallback error
        )
        log_method_on_firelog = firelog.error
        effective_include_exc_info = True
        level_name_str = "error"

    context_params = log_context_params or {}
    base_context = {
        "service_name": actual_service_name,
        "method_name": actual_method_name,
        "status_code": status_code,
        "detail_msg": detail,
    }
    effective_context_params = {**base_context, **context_params}

    # For the default message constructor
    default_log_context_parts = [
        f"service='{actual_service_name}'",
        f"method='{actual_method_name}'",
    ]

    final_log_message = _format_log_message(
        template=log_message_template,
        effective_context=effective_context_params,
        default_context_str_parts=default_log_context_parts,
        default_detail_msg=detail,
        default_status_code=status_code,
    )

    log_args, log_kwargs = _prepare_log_invocation_args(
        final_log_message=final_log_message,
        additional_log_info=additional_log_info,
        actual_service_name=actual_service_name,
        actual_method_name=actual_method_name,
        include_exc_info=effective_include_exc_info,
        log_level_name=level_name_str,
    )

    log_method_on_firelog(*log_args, **log_kwargs)
    raise HTTPException(status_code=status_code, detail=detail)
