# --- General Global Constants
class SecurityConstants:
    # JWT Configuration
    JWT_ALGORITHM = "HS256"
    JWT_CLAIM_EXP = "exp"
    JWT_CLAIM_SUB = "sub"
    JWT_CLAIM_IAT = "iat"
    JWT_CLAIM_JTI = "jti"

    # Token Creation Log/Exception Messages
    LOG_MSG_FAILED_CREATE_ACCESS_TOKEN_TEMPLATE = (
        "Failed to create access token for subject %(subject)s: %(error)s"  # noqa: S105
    )
    EXC_MSG_COULD_NOT_CREATE_ACCESS_TOKEN_TEMPLATE = (
        "Could not create access token: %(error)s"  # noqa: S105
    )
    LOG_MSG_FAILED_CREATE_REFRESH_TOKEN_TEMPLATE = (
        "Failed to create refresh token for subject %(subject)s: %(error)s"  # noqa: S105
    )
    EXC_MSG_COULD_NOT_CREATE_REFRESH_TOKEN_TEMPLATE = (
        "Could not create refresh token: %(error)s"  # noqa: S105
    )

    # OTP Configuration/Verification Messages
    EXC_MSG_OTP_SALT_NOT_CONFIGURED = "OTP_HASH_SALT is not configured in settings."
    LOG_MSG_OTP_VERIFICATION_FAILED_NO_SALT = (
        "OTP verification failed due to missing OTP_HASH_SALT configuration."
    )
    LOG_MSG_UNEXPECTED_OTP_VERIFICATION_ERROR_TEMPLATE = (
        "Unexpected error during OTP verification: %(error)s"
    )
