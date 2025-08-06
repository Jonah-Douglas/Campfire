from datetime import datetime

from sqlalchemy import DateTime, Enum as SQLAlchemyEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.auth.enums.otp_status import OTPStatus
from app.db.base_class import Base


# --- Pending OTP Table Model ---
class PendingOTP(Base):
    """
    Represents a One-Time Password (OTP) that has been generated and is awaiting
    verification, expiration, or consumption.
    """

    status: Mapped[OTPStatus] = mapped_column(
        SQLAlchemyEnum(
            OTPStatus, name="otp_status_enum", create_constraint=True, native_enum=False
        ),
        default=OTPStatus.PENDING,
        server_default=OTPStatus.PENDING.value,
        index=True,
        nullable=False,
    )
    phone_number: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    hashed_otp: Mapped[str] = mapped_column(String, nullable=False)

    attempts_left: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<PendingOTP(id={self.id}, phone_number='{self.phone_number}', status='{self.status}')>"
