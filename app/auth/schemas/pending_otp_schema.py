from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.auth.enums.otp_status import OTPStatus
from app.auth.validators import validate_otp_format
from app.core.validators import validate_phone_e164


# --- Pending OTP Base Schema ---
class OTPBase(BaseModel):
    """Base schema for OTP, containing common fields shared across other OTP schemas."""

    phone_number: Annotated[
        str, Field(min_length=10, max_length=15, examples=["+11234567890"])
    ]
    status: OTPStatus = OTPStatus.PENDING
    attempts_left: int = Field(default=3, ge=0)
    expires_at: datetime
    created_at: datetime

    @field_validator("phone_number")
    @classmethod
    def val_phone_number(cls, v: str) -> str:
        return validate_phone_e164(v)

    model_config = {"from_attributes": True, "use_enum_values": True}


# --- Pending OTP Request/Create Input Schema ---
class OTPRequestPayload(BaseModel):
    """Schema used for a client to request a new OTP to be generated."""

    phone_number: Annotated[
        str, Field(min_length=10, max_length=15, examples=["+11234567890"])
    ]

    @field_validator("phone_number")
    @classmethod
    def val_phone_number(cls, v: str) -> str:
        return validate_phone_e164(v)

    model_config = {"extra": "forbid"}


# --- Pending OTP Verify Input Schema ---
class OTPVerifyPayload(OTPRequestPayload):
    """Schema for verifying a user's OTP."""

    otp_code: Annotated[
        str, Field(min_length=6, max_length=6, pattern=r"^\d{6}$", examples=["123456"])
    ]

    @field_validator("otp_code")
    @classmethod
    def val_otp_format(cls, v: str) -> str:
        return validate_otp_format(v)

    model_config = {"extra": "forbid"}


# --- Pending OTP Create DB Schema ---
class OTPCreateInternal(OTPBase):
    """Schema for internal representation of data needed to create a pending OTP in the DB."""

    hashed_otp: str


# --- Pending OTP Update Schema ---
class OTPUpdate(BaseModel):
    """Schema used for updating an existing pending OTP entry, allowing partial updates."""

    status: OTPStatus | None = None
    attempts_left: Annotated[int, Field(ge=0)] | None = None

    model_config = {"extra": "forbid", "use_enum_values": True}
