# --- Pending OTPs Repo Constants ---
class PendingOTPModelConstants:
    """Constants related to the PendingOTPs model/table name."""

    TABLE_NAME = "pending_otps"
    MODEL_NAME = "PendingOTP"


class PendingOTPRepoMessages:
    PREFIX = "REPO: PendingOTP - "
    CREATING = (
        PREFIX + "Attempting to create pending OTP for phone_prefix: {phone_prefix}."
    )
    CREATED_SUCCESS = (
        PREFIX
        + "Pending OTP ID {otp_id} created successfully for phone_prefix: {phone_prefix}."
    )
    FETCHING_ACTIVE = (
        PREFIX + "Fetching active pending OTP for phone_prefix: {phone_prefix}."
    )
    ACTIVE_FOUND = (
        PREFIX
        + "Active pending OTP ID {otp_id} found for phone_prefix: {phone_prefix}."
    )
    NO_ACTIVE_FOUND = (
        PREFIX + "No active pending OTP found for phone_prefix: {phone_prefix}."
    )
    VERIFICATION_ATTEMPT = (
        PREFIX + "OTP verification attempt for phone_prefix: {phone_prefix}."
    )
    VERIFY_NO_ACTIVE = (
        PREFIX + "Verification failed for {phone_prefix}: No active OTP found."
    )
    EXPIRED_DURING_VERIFICATION = (
        PREFIX + "OTP ID {otp_id} for {phone_prefix} expired during verification."
    )
    MAX_ATTEMPTS_REACHED = (
        PREFIX
        + "Max OTP attempts reached for OTP ID {otp_id}, phone_prefix: {phone_prefix}."
    )
    INVALID_ATTEMPT = (
        PREFIX
        + "Invalid OTP attempt for OTP ID {otp_id}, {phone_prefix}. Attempts left: {attempts_left}."
    )
    SUCCESSFULLY_VERIFIED = (
        PREFIX
        + "OTP ID {otp_id} successfully verified for phone_prefix: {phone_prefix}."
    )
    VERIFY_FAILED_ERROR = (
        PREFIX
        + "Verification for OTP ID {otp_id}, {phone_prefix} failed. Error: {error}"
    )
    INVALIDATING_EXISTING = (
        PREFIX + "Invalidating existing pending OTPs for phone_prefix: {phone_prefix}."
    )
    INVALIDATED_SUCCESS_COUNT = (
        PREFIX + "{count} pending OTPs invalidated for phone_prefix: {phone_prefix}."
    )
    INVALIDATE_FAILED = (
        PREFIX
        + "Failed to invalidate OTPs for phone_prefix: {phone_prefix}. Error: {error}"
    )
    UPDATING_STATUS = (
        PREFIX
        + "Attempting to update status for OTP ID {otp_id} from {old_status} to {new_status}."
    )
    STATUS_UPDATED_SUCCESS = (
        PREFIX + "Status for OTP ID {otp_id} updated successfully to {new_status}."
    )
    SETTING_SEND_ERROR = PREFIX + "Attempting to set sending error for OTP ID {otp_id}."
    SEND_ERROR_SET_SUCCESS = PREFIX + "Sending error status set for OTP ID {otp_id}."
    SET_SEND_ERROR_NOT_FOUND = (
        PREFIX + "OTP ID {otp_id} not found when trying to set sending error."
    )
    CLEANUP_STARTED = PREFIX + "Starting cleanup of expired/consumed OTPs."
    CLEANED_UP_SUCCESS_COUNT = (
        PREFIX + "{count} expired/consumed OTPs cleaned up successfully."
    )
    CLEANUP_FAILED = PREFIX + "OTP cleanup process failed. Error: {error}"


# --- User Sessions Repo Constants ---
class UserSessionModelConstants:
    """Constants related to the UserSessions model/table name."""

    TABLE_NAME = "user_sessions"
    MODEL_NAME = "PendingOTP"


class UserSessionRepoMessages:
    PREFIX = "REPO: UserSession - "

    CREATING = (
        PREFIX
        + "Attempting to create user session for user_id: {user_id}, jti_suffix: {jti_suffix}."
    )
    CREATED_SUCCESS = (
        PREFIX
        + "Session ID {session_id} created for user_id: {user_id}, jti_suffix: {jti_suffix}."
    )
    GET_BY_JTI = PREFIX + "Fetching session by jti_suffix: {jti_suffix}."
    FOUND_BY_JTI = PREFIX + "Session ID {session_id} found by jti_suffix: {jti_suffix}."
    NOT_FOUND_BY_JTI = PREFIX + "No session found for jti_suffix: {jti_suffix}."
    GET_ACTIVE_BY_JTI_USER = (
        PREFIX
        + "Fetching active session for user_id: {user_id}, jti_suffix: {jti_suffix}."
    )
    ACTIVE_FOUND_BY_JTI_USER = (
        PREFIX
        + "Active session ID {session_id} found for user_id: {user_id}, jti_suffix: {jti_suffix}."
    )
    ACTIVE_NOT_FOUND_BY_JTI_USER = (
        PREFIX
        + "No active session found for user_id: {user_id}, jti_suffix: {jti_suffix}."
    )
    INVALIDATING = (
        PREFIX
        + "Invalidating session ID: {session_id} for user_id: {user_id}, jti_suffix: {jti_suffix}."
    )
    INVALIDATED_SUCCESS = (
        PREFIX
        + "Session ID: {session_id} invalidated for user_id: {user_id}, jti_suffix: {jti_suffix}."
    )
    INVALIDATING_BY_JTI = PREFIX + "Invalidating session by jti_suffix: {jti_suffix}."
    INVALIDATE_BY_JTI_NOT_FOUND = (
        PREFIX + "Session not found for invalidation by jti_suffix: {jti_suffix}."
    )
    INVALIDATING_ALL_FOR_USER = (
        PREFIX
        + "Invalidating all sessions for user_id: {user_id}, excluding jti_suffix: {excluded_jti_suffix}."
    )
    INVALIDATE_ALL_NONE_FOUND = (
        PREFIX
        + "No active sessions found to invalidate for user_id: {user_id}, excluding jti_suffix: {excluded_jti_suffix}."
    )
    INVALIDATED_ALL_SUCCESS_COUNT = (
        PREFIX
        + "{count} sessions invalidated for user_id: {user_id}, excluding jti_suffix: {excluded_jti_suffix}."
    )
    INVALIDATE_ALL_FAILED = (
        PREFIX
        + "Failed to invalidate all sessions for user_id: {user_id}, excluding jti_suffix: {excluded_jti_suffix}. Error: {error}"
    )
    CLEANUP_STARTED = PREFIX + "Starting cleanup of revoked/expired user sessions."
    CLEANED_UP_SUCCESS_COUNT = (
        PREFIX + "{count} revoked/expired user sessions cleaned up."
    )
    CLEANUP_FAILED = PREFIX + "User session cleanup process failed. Error: {error}"
