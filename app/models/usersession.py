from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone

from app.models import user


# UserSession model
class UserSession(SQLModel, table=True):
    __tablename__ = "user_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    refresh_token_jti: str = Field(index=True, unique=True)
    user_agent: str | None = Field(default=None)
    ip_address: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    is_active: bool = Field(default=True)

    # Relationship back to User
    user: "user.User" = Relationship(back_populates="sessions")