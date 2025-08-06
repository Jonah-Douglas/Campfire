from typing import Any, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class FieldError(BaseModel):
    field: str
    message: str
    code: str | None = None


class ErrorDetail(BaseModel):
    model_config = {"frozen": True}
    code: str | None = None
    message: str | None = None  # General error message
    field_errors: list[FieldError] | None = None  # For validation errors
    debug_info: dict[str, Any] | None = None


class GenericAPIResponse[DataT](BaseModel):
    model_config = {"frozen": True}
    success: bool = True
    message: str | None = None
    data: DataT | None = None
    error: ErrorDetail | None = None

    @classmethod
    def success_response(
        cls, data_payload: DataT | None = None, msg: str = "Operation successful."
    ) -> "GenericAPIResponse[DataT]":
        return cls(success=True, message=msg, data=data_payload, error=None)

    @classmethod
    def error_response(
        cls, msg: str, error_code: str | None = None, error_details: str | None = None
    ) -> "GenericAPIResponse[DataT]":
        return cls(
            success=False,
            message=msg,
            data=None,
            error=ErrorDetail(code=error_code, message=error_details or msg),
        )
