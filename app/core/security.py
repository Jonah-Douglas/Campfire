from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import uuid

from jose import JWTError, jwt

from app.core.config import settings
from app.core.constants import SecurityConstants
from app.core.logging.logger_wrapper import firelog


class TokenCreationError(Exception):
    """Custom exception for errors during token creation."""

    pass


# --- Token Creation Functions ---
def create_access_token(
    subject: str | int | uuid.UUID, expires_delta: timedelta
) -> str:
    """
    Creates an HS256 encoded JWT access token.

    Args:
        subject: The subject of the token (e.g., user ID).
        expires_delta: Timedelta for token expiration.

    Returns:
        The encoded JWT access token.

    Raises:
        TokenCreationError: If token creation fails.
    """
    expire = datetime.now(UTC) + expires_delta
    to_encode = {
        SecurityConstants.JWT_CLAIM_EXP: expire,
        SecurityConstants.JWT_CLAIM_SUB: str(subject),
        SecurityConstants.JWT_CLAIM_IAT: datetime.now(UTC),
        SecurityConstants.JWT_CLAIM_JTI: str(uuid.uuid4()),
    }

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.ACCESS_TOKEN_SECRET_KEY,
            algorithm=SecurityConstants.JWT_ALGORITHM,
        )
        return encoded_jwt
    except JWTError as e:
        firelog.error(
            SecurityConstants.LOG_MSG_FAILED_CREATE_ACCESS_TOKEN_TEMPLATE.format(
                subject=subject, error=e
            ),
            exc_info=True,
        )
        raise TokenCreationError(
            SecurityConstants.EXC_MSG_COULD_NOT_CREATE_ACCESS_TOKEN_TEMPLATE.format(
                error=e
            )
        ) from e


def create_refresh_token_with_jti(
    subject: str | int | uuid.UUID, expires_delta: timedelta
) -> tuple[str, str]:
    """
    Creates an HS256 encoded JWT refresh token, returning the token and its JTI.

    The JTI should be stored and validated to allow for refresh token revocation
    and to detect reuse if implementing one-time use refresh tokens.

    Args:
        subject: The subject of the token (e.g., user ID).
        expires_delta: Timedelta for token expiration.

    Returns:
        A tuple containing the encoded JWT refresh token and its JTI (JWT ID).

    Raises:
        TokenCreationError: If token creation fails.
    """
    expire = datetime.now(UTC) + expires_delta
    jti_val = str(uuid.uuid4())  # Generate JTI
    to_encode = {
        SecurityConstants.JWT_CLAIM_EXP: expire,
        SecurityConstants.JWT_CLAIM_SUB: str(subject),
        SecurityConstants.JWT_CLAIM_IAT: datetime.now(UTC),
        SecurityConstants.JWT_CLAIM_JTI: jti_val,
    }

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.REFRESH_TOKEN_SECRET_KEY,
            algorithm=SecurityConstants.JWT_ALGORITHM,
        )
        return encoded_jwt, jti_val
    except JWTError as e:
        firelog.error(
            SecurityConstants.LOG_MSG_FAILED_CREATE_REFRESH_TOKEN_TEMPLATE.format(
                subject=subject, error=e
            ),
            exc_info=True,
        )
        raise TokenCreationError(
            SecurityConstants.EXC_MSG_COULD_NOT_CREATE_REFRESH_TOKEN_TEMPLATE.format(
                error=e
            )
        ) from e


# --- OTP Functions ---
class OTPConfigurationError(ValueError):
    """Error related to OTP configuration."""

    pass


def hash_otp_value(otp: str) -> str:
    """Hashes the OTP value using SHA256 with a configured salt."""
    if not hasattr(settings, "OTP_HASH_SALT") or not settings.OTP_HASH_SALT:
        raise OTPConfigurationError(SecurityConstants.EXC_MSG_OTP_SALT_NOT_CONFIGURED)

    # Ensure salt is a string if it comes from settings
    salt = str(settings.OTP_HASH_SALT)
    salted_otp = salt + otp
    return hashlib.sha256(salted_otp.encode("utf-8")).hexdigest()


def verify_otp_value(plain_otp: str, hashed_otp_from_storage: str) -> bool:
    """Verifies a plain OTP against a stored hashed OTP value."""
    try:
        newly_hashed_otp = hash_otp_value(plain_otp)
        return hmac.compare_digest(
            newly_hashed_otp.encode("utf-8"), hashed_otp_from_storage.encode("utf-8")
        )
    except OTPConfigurationError:
        firelog.error(SecurityConstants.LOG_MSG_OTP_VERIFICATION_FAILED_NO_SALT)
        return False
    except Exception as e:
        firelog.error(
            SecurityConstants.LOG_MSG_UNEXPECTED_OTP_VERIFICATION_ERROR_TEMPLATE.format(
                error=e
            ),
            exc_info=True,
        )
        return False
