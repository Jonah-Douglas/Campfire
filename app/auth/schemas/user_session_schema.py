from datetime import datetime

from pydantic import BaseModel


# --- User Session Base Schema ---
class UserSessionBase(BaseModel):
    """Base schema for user session information."""

    user_id: int
    refresh_token_jti: str
    user_agent: str | None = None
    ip_address: str | None = None
    expires_at: datetime
    is_active: bool = True
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


# --- User Session Create Schema ---
class UserSessionCreate(BaseModel):
    """Schema for creating a new user session entry."""

    user_id: int
    refresh_token_jti: str
    user_agent: str | None = None
    ip_address: str | None = None
    expires_at: datetime

    model_config = {"extra": "forbid"}


# --- User Session Public Schema ---
class UserSessionPublic(UserSessionBase):
    """Schema representing a user session, typically for API responses or internal listings."""

    id: int


# --- User Session Update Schema ---
class UserSessionUpdate(BaseModel):
    """Schema for updating an existing user session, e.g., to change its active status."""

    is_active: bool | None = None

    model_config = {"extra": "forbid"}
