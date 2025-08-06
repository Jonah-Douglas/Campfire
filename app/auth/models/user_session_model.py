from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.users.models.user_model import User


# --- User Session Table Model ---
class UserSession(Base):
    """
    Stores active user sessions, primarily identified by a refresh token's JTI.
    Used to manage user login state across multiple devices or extended periods.
    """

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=func.true(), index=True, nullable=False
    )

    refresh_token_jti: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, nullable=False
    )
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="sessions")

    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, jti='{self.refresh_token_jti}', active={self.is_active})>"
