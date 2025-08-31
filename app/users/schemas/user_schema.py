from datetime import date, datetime
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.validators import validate_phone_e164


# --- User Base Schema ---
class UserBase(BaseModel):
    """Base schema for User, containing common fields."""

    phone_number: Annotated[str, Field(examples=["+11234567890"])]
    email: Annotated[EmailStr, Field(examples=["user@example.com"])] | None = None
    first_name: Annotated[str, Field(max_length=50)] | None = None
    last_name: Annotated[str, Field(max_length=50)] | None = None
    date_of_birth: date | None = None
    is_enable_notifications: bool = True
    is_profile_complete: bool = False
    is_app_setup_complete: bool = False

    @field_validator("phone_number")
    @classmethod
    def val_phone_number(cls, v: str) -> str:
        return validate_phone_e164(v)

    model_config = {"from_attributes": True, "extra": "forbid"}


# --- User Create Schema ---
class UserCreateInternal(BaseModel):
    """Schema for internal user creation with minimal data (e.g., after OTP generation before verification)."""

    phone_number: Annotated[str, Field(examples=["+11234567890"])]

    @field_validator("phone_number")
    @classmethod
    def val_phone_number(cls, v: str) -> str:
        return validate_phone_e164(v)

    model_config = {"extra": "forbid"}


# --- User Complete Profile Schema ---
class UserCompleteProfile(BaseModel):
    """Schema for completing a user's profile after initial registration."""

    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]
    email: EmailStr
    date_of_birth: date
    is_enable_notifications: bool

    model_config = {"extra": "forbid"}


# --- User Update Schema ---
class UserUpdate(BaseModel):
    """Schema for updating user information by an authenticated user."""

    phone_number: Annotated[str, Field(examples=["+11234567890"])] | None = None
    email: EmailStr | None = None
    first_name: Annotated[str, Field(min_length=1, max_length=50)] | None = None
    last_name: Annotated[str, Field(min_length=1, max_length=50)] | None = None
    date_of_birth: date | None = None
    is_enable_notifications: bool | None = None

    @field_validator("phone_number", mode="before")
    @classmethod
    def val_phone_number(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return validate_phone_e164(v)

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_value(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update.")
        return values

    model_config = {"extra": "forbid"}


# --- User Public Schema ---
class UserPublic(UserBase):
    """Public representation of a user, typically for API responses."""

    id: int
    is_active: bool
    last_login_at: datetime | None = None
    updated_at: datetime
    created_at: datetime


# --- Users Public Schema ---
class UsersPublic(BaseModel):
    """Response model for a list of users with count."""

    data: list[UserPublic]
    count: int

    model_config = {"extra": "forbid"}
