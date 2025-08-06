from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.auth.models.user_session_model import UserSession


class User(Base):
    phone_number: Mapped[str] = mapped_column(
        String(30), unique=True, index=True, nullable=False
    )
    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    first_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_enable_notifications: Mapped[bool] = mapped_column(
        Boolean, server_default=func.true(), nullable=False
    )

    is_profile_complete: Mapped[bool] = mapped_column(
        Boolean, server_default=func.false(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=func.false(), nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, server_default=func.false(), nullable=False
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, phone_number='{self.phone_number}', email='{self.email}')>"
