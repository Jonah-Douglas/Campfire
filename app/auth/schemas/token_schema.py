from datetime import datetime

from pydantic import BaseModel, Field


# --- Token Response ---
class Token(BaseModel):
    access_token: str
    refresh_token: str
    is_new_user: bool
    token_type: str = "bearer"  # noqa: S105


# --- Token Request Schemas ---
class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        ...,
        description="The refresh token provided by the client.",
        examples=["your_example_token_here"],
    )


# --- Base JWT Payload Definitions ---
class BaseTokenPayload(BaseModel):
    sub: int | None = None  # UserID
    exp: datetime | None = None  # Expiration time
    iat: datetime | None = None  # Issued at time


# --- Access Token Payload ---
class AccessTokenPayload(BaseTokenPayload):
    # Sub and exp required for a full access token schema
    sub: int  # pyright: ignore[reportGeneralTypeIssues]
    exp: datetime  # pyright: ignore[reportGeneralTypeIssues]
    token_type: str = "access"  # noqa: S105


# --- Refresh Token Payload ---
class RefreshTokenPayload(BaseTokenPayload):
    token_type: str = "refresh"  # noqa: S105
    jti: str | None = None
