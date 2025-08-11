# --- Auth Messages ---
class AuthSuccessMessages:
    """Messages directly shown to the user for successful operations or general info."""

    OTP_MESSAGE = "Your Campfire verification code is: %(otp_code)s"
    LOGOUT_SUCCESS = "You have been successfully logged out."
    OTP_SENT_SUCCESSFULLY = "OTP has been dispatched via SMS."
    OTP_PROCESSED_SUCCESSFULLY = "OTP processed successfully."
    OTP_DEBUG_MODE = "OTP available in debug_otp."
    OTP_PROCESSED_DEV_MODE = "OTP processed successfully (dev mode)."
    OTP_VERIFIED_SUCCESS = "OTP verified successfully. Tokens granted."
    TOKENS_REFRESHED_SUCCESS = "Tokens refreshed successfully."


class AuthHttpErrorDetails:
    """Detailed error messages intended for the 'detail' field of FastAPI's HTTPException.
    These are user-facing error explanations.
    """

    # OTP Related Errors
    OTP_VERIFICATION_FAILED = (
        "OTP verification failed. The code may be invalid, expired, or already used."
    )
    OTP_CREATE_RECORD_FAILED = "Failed to initiate OTP process. Please try again."
    OTP_SMS_SEND_FAILED = "Failed to send OTP via SMS. Please try again."

    # Session Related Errors
    SESSION_NOT_FOUND_OR_REVOKED = "Session not found or has been revoked."

    # User Account Related Errors
    USER_CREATE_FAILED = "Failed to create user account. Please try again."
    USER_INACTIVE = "Your account is currently inactive."
    USER_INACTIVE_OR_NOT_FOUND = "User account is inactive or not found."
    UNEXPECTED_ERROR = "Unexpected error in user processing."

    # Token Related Errors
    REFRESH_TOKEN_INVALID = "Invalid or expired refresh token."  # noqa: S105
    REFRESH_TOKEN_INVALID_OR_EXPIRED = "Refresh token is invalid or has expired."  # noqa: S105

    # General & Miscellaneous Errors
    SMS_SERVICE_UNAVAILABLE = (
        "SMS service is currently unavailable. Please try again later."
    )
    LOGOUT_FORBIDDEN_OTHER_USER = (
        "You are not authorized to perform this logout action."
    )
    GENERIC_INTERNAL_ERROR = "An unexpected error occurred. Please try again later."
