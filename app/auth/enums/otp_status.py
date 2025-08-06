from enum import Enum


# --- OTP Status Enum ---
class OTPStatus(str, Enum):
    """
    Represents the possible status of a One-Time Password (OTP).
    """

    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
    MAX_ATTEMPTS = "max_attempts"
    ERROR_SENDING = "error_sending"
