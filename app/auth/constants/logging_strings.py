# --- Auth Logging Strings ---
class AuthLoggingStrings:
    OTP_REQUEST_INITIATED = "OTP request initiated for phone_prefix: {phone_prefix}"
    OTP_SMS_SERVICE_UNAVAILABLE = "OTP request failed: SMS service unavailable."
    OTP_SENT_IN_DEV_MODE = (
        "OTP sent (dev mode) for {phone_prefix}. Debug OTP: {debug_otp_value}"
    )
    OTP_SENT_IN_PRODUCTION = "OTP dispatched for %(phone_prefix)s."
    OTP_HTTP_ERROR = "OTP request HTTP error for {phone_prefix}: {http_exc.status_code} - {http_exc.detail}"
    OTP_UNHANDLED_ERROR = "Unhandled error during OTP request for {phone_prefix}: {e}"
    OTP_VERIFICATION_ATTEMPT = (
        "OTP verification attempt for phone_prefix: {phone_prefix} from {client_host}"
    )
    OTP_SUCCESSFULLY_VERIFIED = (
        "OTP verified successfully for phone_prefix: {phone_prefix}. Tokens granted."
    )
    OTP_FAILED_VERIFICATION = "OTP verification failed for {phone_prefix}: {http_exc.status_code} - {http_exc.detail}"
    OTP_UNEXPECTED_ERROR = "An unexpected error occurred during OTP verification."
    TOKEN_REFRESH_ATTEMPT = "Token refresh attempt from client: {client_host}"  # noqa: S105
    TOKEN_REFRESH_FAILED = "Token refresh failed (invalid or expired refresh token)."  # noqa: S105
    TOKEN_SUCCESSFULLY_REFRESHED = (
        "Tokens refreshed successfully for client: {client_host}."  # noqa: S105
    )
    LOGOUT_ATTEMPT = "Logout attempt for user_id: {current_user.id}"
    LOGOUT_SUCCESS = "User user_id: {current_user.id} logged out successfully."
    LOGOUT_HTTP_ERROR = "Logout HTTP error for user_id {current_user.id}: {http_exc.status_code} - {http_exc.detail}"
    LOGOUT_UNHANDLED_ERROR = (
        "Unhandled error during logout for user_id {current_user.id}: {e}"
    )


class AuthServiceLoggingStrings:
    """Logging strings specific to the AuthService."""

    _SERVICE_NAME = "AuthService"

    PREFIX = "SERVICE: Auth - "
    OTP_GENERATED = PREFIX + "Generated new OTP ending in ...{otp_suffix}."
    OTP_RECORD_CREATED = (
        PREFIX + "OTP record ID {otp_id} created for phone: {phone_number}."
    )
    OTP_RECORD_CREATE_FAILED = (
        PREFIX + "Failed to create OTP record for phone: {phone_number}. Error: {error}"
    )
    OTP_DEV_MODE_RESPONSE = (
        PREFIX
        + "Sending OTP ending in ...{otp_suffix} in DEV mode response for phone: {phone_number}."
    )
    OTP_SENDING_VIA_SMS = (
        PREFIX + "Attempting to send OTP ID {otp_id} via SMS to phone: {phone_number}."
    )
    OTP_SMS_SERVICE_ERROR = (
        PREFIX
        + "SMS service error for OTP ID {otp_id}, phone: {phone_number}. Error: {error}"
    )
    OTP_SMS_SEND_FAILED = (
        PREFIX + "Failed to send OTP SMS for ID {otp_id} to phone: {phone_number}."
    )
    OTP_SENT_SUCCESSFULLY = (
        PREFIX + "OTP ID {otp_id} sent successfully to phone: {phone_number}."
    )

    OTP_VERIFY_REQUEST = (
        PREFIX
        + "OTP verification request for phone: {phone_number}, OTP ending in ...{otp_suffix}."
    )
    OTP_VERIFY_FAILED_REASON = (
        PREFIX
        + "OTP verification failed for phone: {phone_number}, OTP ending in ...{otp_suffix}. Reason: {reason}"
    )
    OTP_VERIFIED_SUCCESS = (
        PREFIX + "OTP ID {otp_id} successfully verified for phone: {phone_number}."
    )
    USER_NOT_FOUND_CREATING = (
        PREFIX + "User not found for phone: {phone_number}. Attempting to create."
    )
    USER_CREATE_FAILED_CRITICAL = (
        PREFIX
        + "CRITICAL - Failed to create user for phone: {phone_number} after OTP verification."
    )
    USER_CREATED_SUCCESS = (
        PREFIX + "User ID {user_id} created successfully for phone: {phone_number}."
    )
    USER_INACTIVE_LOGIN_ATTEMPT = PREFIX + "Inactive user ID {user_id} attempted login."
    USER_EXISTING_LOGIN = PREFIX + "Existing user ID {user_id} logged in."
    TOKENS_CREATED = (
        PREFIX
        + "Access and Refresh tokens created for user_id: {user_id}. Refresh JTI suffix: ...{refresh_jti_suffix}."
    )
    USER_SESSION_CREATED = (
        PREFIX
        + "User session created for user_id: {user_id}. Refresh JTI suffix: ...{refresh_jti_suffix}."
    )

    REFRESH_TOKEN_REQUEST = (
        PREFIX
        + "Refresh token request for user_id: {user_id}, token JTI suffix: ...{token_jti_suffix}."
    )
    REFRESH_TOKEN_INVALID_PAYLOAD = (
        PREFIX
        + "Refresh token has invalid payload (reason: {reason}). Token JTI suffix: ...{token_jti_suffix}."
    )
    REFRESH_TOKEN_JWT_ERROR = (
        PREFIX
        + "Refresh token JWTError: {error}. Token JTI suffix: ...{token_jti_suffix}."
    )
    REFRESH_TOKEN_NO_ACTIVE_SESSION = (
        PREFIX
        + "No active session found for refresh token. User_id: {user_id}, JTI suffix: ...{token_jti_suffix}."
    )
    REFRESH_TOKEN_USER_INACTIVE_OR_NOT_FOUND = (
        PREFIX
        + "User inactive or not found during refresh. User_id: {user_id}, JTI suffix: ...{token_jti_suffix}. Invalidating session."
    )
    REFRESH_NEW_ACCESS_TOKEN_CREATED = (
        PREFIX + "New access token created during refresh for user_id: {user_id}."
    )
    REFRESH_TOKEN_ROTATING = (
        PREFIX
        + "Rotating refresh token for user_id: {user_id}. Old JTI suffix: ...{old_token_jti_suffix}."
    )
    REFRESH_TOKEN_ROTATION_COMPLETE = (
        PREFIX
        + "Refresh token rotation complete for user_id: {user_id}. New JTI suffix: ...{new_token_jti_suffix}."
    )
    REFRESH_TOKEN_NO_ROTATION = (
        PREFIX
        + "Refresh token not rotated (setting disabled) for user_id: {user_id}, JTI suffix: ...{token_jti_suffix}."
    )

    LOGOUT_REQUEST = (
        PREFIX
        + "Logout request for user_id: {user_id} using token JTI suffix: ...{token_jti_suffix}."
    )
    LOGOUT_MALFORMED_TOKEN = (
        PREFIX
        + "Logout attempt with malformed refresh token. Requesting user_id: {requesting_user_id}, token JTI: {token_jti}, token SUB: {token_sub}."
    )
    LOGOUT_ATTEMPT_FOR_OTHER_USER = (
        PREFIX
        + "SECURITY ALERT - User {requesting_user_id} attempted to logout session for user {target_user_id} using token JTI suffix: ...{token_jti_suffix}."
    )
    LOGOUT_INVALID_EXPIRED_TOKEN = (
        PREFIX
        + "Logout attempt with invalid/expired refresh token by user {requesting_user_id}. Error: {error}. Token JTI suffix: ...{token_jti_suffix}."
    )
    LOGOUT_JTI_USER_MISMATCH_ALERT = (
        PREFIX
        + "CRITICAL SECURITY ALERT - Session JTI suffix ...{token_jti_suffix} belonged to user {session_user_id} but was attempted to be logged out by token claiming user {token_user_id}."
    )
    LOGOUT_SESSION_INVALIDATED = (
        PREFIX
        + "Session successfully invalidated for user {user_id} by JTI suffix: ...{token_jti_suffix}."
    )
    LOGOUT_NO_ACTIVE_SESSION_FOR_JTI = (
        PREFIX
        + "No active session found for JTI suffix: ...{token_jti_suffix} (user {user_id}) to logout, or already inactive."
    )
