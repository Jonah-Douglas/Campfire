# --- Auth Logging Strings ---
class AuthLoggingStrings:
    """Logging strings specific to the Auth API."""

    OTP_REQUEST_INITIATED = "OTP request initiated for phone_prefix: %(phone_prefix)s"
    OTP_SMS_SERVICE_UNAVAILABLE = "OTP request failed: SMS service unavailable."
    OTP_SENT_IN_DEV_MODE = (
        "OTP sent (dev mode) for %(phone_prefix)s. Debug OTP: %(debug_otp_value)s"
    )
    OTP_SENT_IN_PRODUCTION = "OTP dispatched for %(phone_prefix)s."
    OTP_HTTP_ERROR = "OTP request HTTP error for %(phone_prefix)s: %(http_status_code)s - %(http_detail)s"
    OTP_UNHANDLED_ERROR = (
        "Unhandled error during OTP request for %(phone_prefix)s: %(e)s"
    )
    OTP_VERIFICATION_ATTEMPT = "OTP verification attempt for phone_prefix: %(phone_prefix)s from %(client_host)s"
    OTP_SUCCESSFULLY_VERIFIED = (
        "OTP verified successfully for phone_prefix: %(phone_prefix)s. Tokens granted."
    )
    OTP_FAILED_VERIFICATION = "OTP verification failed for %(phone_prefix)s: %(http_status_code)s - %(http_detail)s"
    OTP_UNEXPECTED_ERROR = "An unexpected error occurred during OTP verification."
    TOKEN_REFRESH_ATTEMPT = "Token refresh attempt from client: %(client_host)s"  # noqa: S105
    TOKEN_REFRESH_FAILED = "Token refresh failed (invalid or expired refresh token)."  # noqa: S105
    TOKEN_SUCCESSFULLY_REFRESHED = (
        "Tokens refreshed successfully for client: %(client_host)s."  # noqa: S105
    )
    LOGOUT_ATTEMPT = "Logout attempt for user_id: %(user_id)s"
    LOGOUT_SUCCESS = "User user_id: %(user_id)s logged out successfully."
    LOGOUT_HTTP_ERROR = "Logout HTTP error for user_id %(user_id)s: %(http_status_code)s - %(http_detail)s"
    LOGOUT_UNHANDLED_ERROR = (
        "Unhandled error during logout for user_id %(user_id)s: %(e)s"
    )


class AuthServiceLoggingStrings:
    """Logging strings specific to the AuthService."""

    _SERVICE_NAME = "AuthService"

    PREFIX = "SERVICE: Auth - "
    OTP_GENERATED = PREFIX + "Generated new OTP ending in ...%(otp_suffix)s."
    OTP_RECORD_CREATED = (
        PREFIX + "OTP record ID %(otp_id)s created for phone: %(phone_number)s."
    )
    OTP_RECORD_CREATE_FAILED = (
        PREFIX
        + "Failed to create OTP record for phone: %(phone_number)s. Error: %(error)s"
    )
    OTP_DEV_MODE_RESPONSE = (
        PREFIX
        + "Sending OTP ending in ...%(otp_suffix)s in DEV mode response for phone: %(phone_number)s."
    )
    OTP_SENDING_VIA_SMS = (
        PREFIX
        + "Attempting to send OTP ID %(otp_id)s via SMS to phone: %(phone_number)s."
    )
    OTP_SMS_SERVICE_ERROR = (
        PREFIX
        + "SMS service error for OTP ID %(otp_id)s, phone: %(phone_number)s. Error: %(error)s"
    )
    OTP_SMS_SEND_FAILED = (
        PREFIX + "Failed to send OTP SMS for ID %(otp_id)s to phone: %(phone_number)s."
    )
    OTP_SENT_SUCCESSFULLY = (
        PREFIX + "OTP ID %(otp_id)s sent successfully to phone: %(phone_number)s."
    )

    OTP_VERIFY_REQUEST = (
        PREFIX
        + "OTP verification request for phone: %(phone_number)s, OTP ending in ...%(otp_suffix)s."
    )
    OTP_VERIFY_FAILED_REASON = (
        PREFIX
        + "OTP verification failed for phone: %(phone_number)s, OTP ending in ...%(otp_suffix)s. Reason: %(reason)s"
    )
    OTP_VERIFIED_SUCCESS = (
        PREFIX + "OTP ID %(otp_id)s successfully verified for phone: %(phone_number)s."
    )
    USER_NOT_FOUND_CREATING = (
        PREFIX + "User not found for phone: %(phone_number)s. Attempting to create."
    )
    USER_CREATE_FAILED_CRITICAL = (
        PREFIX
        + "CRITICAL - Failed to create user for phone: %(phone_number)s after OTP verification."
    )
    USER_CREATED_SUCCESS = (
        PREFIX + "User ID %(user_id)s created successfully for phone: %(phone_number)s."
    )
    USER_INACTIVE_LOGIN_ATTEMPT = (
        PREFIX + "Inactive user ID %(user_id)s attempted login."
    )
    USER_EXISTING_LOGIN = PREFIX + "Existing user ID %(user_id)s logged in."
    TOKENS_CREATED = (
        PREFIX
        + "Access and Refresh tokens created for user_id: %(user_id)s. Refresh JTI suffix: ...%(refresh_jti_suffix)s."
    )
    USER_SESSION_CREATED = (
        PREFIX
        + "User session created for user_id: %(user_id)s. Refresh JTI suffix: ...%(refresh_jti_suffix)s."
    )

    REFRESH_TOKEN_REQUEST = (
        PREFIX
        + "Refresh token request for user_id: %(user_id)s, token JTI suffix: ...%(token_jti_suffix)s."
    )
    REFRESH_TOKEN_INVALID_PAYLOAD = (
        PREFIX
        + "Refresh token has invalid payload (reason: %(reason)s). Token JTI suffix: ...%(token_jti_suffix)s."
    )
    REFRESH_TOKEN_JWT_ERROR = (
        PREFIX
        + "Refresh token JWTError: %(error)s. Token JTI suffix: ...%(token_jti_suffix)s."
    )
    REFRESH_TOKEN_NO_ACTIVE_SESSION = (
        PREFIX
        + "No active session found for refresh token. User_id: %(user_id)s, JTI suffix: ...%(token_jti_suffix)s."
    )
    REFRESH_TOKEN_USER_INACTIVE_OR_NOT_FOUND = (
        PREFIX
        + "User inactive or not found during refresh. User_id: %(user_id)s, JTI suffix: ...%(token_jti_suffix)s. Invalidating session."
    )
    REFRESH_NEW_ACCESS_TOKEN_CREATED = (
        PREFIX + "New access token created during refresh for user_id: %(user_id)s."
    )
    REFRESH_TOKEN_ROTATING = (
        PREFIX
        + "Rotating refresh token for user_id: %(user_id)s. Old JTI suffix: ...%(old_token_jti_suffix)s."
    )
    REFRESH_TOKEN_ROTATION_COMPLETE = (
        PREFIX
        + "Refresh token rotation complete for user_id: %(user_id)s. New JTI suffix: ...%(new_token_jti_suffix)s."
    )
    REFRESH_TOKEN_NO_ROTATION = (
        PREFIX
        + "Refresh token not rotated (setting disabled) for user_id: %(user_id)s, JTI suffix: ...%(token_jti_suffix)s."
    )

    LOGOUT_REQUEST = (
        PREFIX
        + "Logout request for user_id: %(user_id)s using token JTI suffix: ...%(token_jti_suffix)s."
    )
    LOGOUT_MALFORMED_TOKEN = (
        PREFIX
        + "Logout attempt with malformed refresh token. Requesting user_id: %(requesting_user_id)s, token JTI: %(token_jti)s, token SUB: %(token_sub)s."
    )
    LOGOUT_ATTEMPT_FOR_OTHER_USER = (
        PREFIX
        + "SECURITY ALERT - User %(requesting_user_id)s attempted to logout session for user %(target_user_id)s using token JTI suffix: ...%(token_jti_suffix)s."
    )
    LOGOUT_INVALID_EXPIRED_TOKEN = (
        PREFIX
        + "Logout attempt with invalid/expired refresh token by user %(requesting_user_id)s. Error: %(error)s. Token JTI suffix: ...%(token_jti_suffix)s."
    )
    LOGOUT_JTI_USER_MISMATCH_ALERT = (
        PREFIX
        + "CRITICAL SECURITY ALERT - Session JTI suffix ...%(token_jti_suffix)s belonged to user %(session_user_id)s but was attempted to be logged out by token claiming user %(token_user_id)s."
    )
    LOGOUT_SESSION_INVALIDATED = (
        PREFIX
        + "Session successfully invalidated for user %(user_id)s by JTI suffix: ...%(token_jti_suffix)s."
    )
    LOGOUT_NO_ACTIVE_SESSION_FOR_JTI = (
        PREFIX
        + "No active session found for JTI suffix: ...%(token_jti_suffix)s (user %(user_id)s) to logout, or already inactive."
    )


class DependencyLoggingStrings:
    """Logging strings specific to the Auth Dependencies."""

    PREFIX = "DEPENDENCY: Auth - "
    # --- Token Processing Errors ---
    MALFORMED_TOKEN_PAYLOAD = (
        PREFIX
        + "Malformed token payload during AccessTokenPayload validation. Errors: %(error)s"
    )
    UNEXPECTED_TOKEN_PROCESSING_ERROR = (
        PREFIX + "Unexpected error during token processing. Error: %(error)s"
    )

    # --- User Retrieval/Validation Errors ---
    USER_NOT_FOUND_IN_TOKEN = (
        PREFIX + "User specified in token (user_id: %(user_id)s) not found in database."
    )
    INACTIVE_USER_AUTHENTICATION_ATTEMPT = (
        PREFIX
        + "Attempt to authenticate inactive user (user_id: %(user_id)s, identifier: %(user_identifier)s)."
    )


class ValidatorLoggingStrings:
    """Logging strings specific to the Auth Validators."""

    PREFIX = "VALIDATOR: Auth - "
    OTP_EMPTY = PREFIX + "OTP code cannot be empty."
    OTP_INCORRECT_LENGTH = PREFIX + "Invalid OTP format. Must be 6 digits long."
    OTP_NOT_DIGITS = PREFIX + "Invalid OTP format. Must contain only digits."
