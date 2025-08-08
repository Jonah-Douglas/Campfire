# --- Pending OTPs Repo Constants ---
class PendingOTPModelConstants:
    """Constants related to the PendingOTPs model/table name."""

    TABLE_NAME = "pending_otps"
    MODEL_NAME = "PendingOTP"


class PendingOTPRepoMessages:
    PREFIX = "REPO: PendingOTP - "
    CREATING = (
        PREFIX + "Attempting to create pending OTP for phone_prefix: %(phone_prefix)s."
    )
    CREATED_SUCCESS = (
        PREFIX
        + "Pending OTP ID %(otp_id)s created successfully for phone_prefix: %(phone_prefix)s."
    )
    FETCHING_ACTIVE = (
        PREFIX + "Fetching active pending OTP for phone_prefix: %(phone_prefix)s."
    )
    ACTIVE_FOUND = (
        PREFIX
        + "Active pending OTP ID %(otp_id)s found for phone_prefix: %(phone_prefix)s."
    )
    NO_ACTIVE_FOUND = (
        PREFIX + "No active pending OTP found for phone_prefix: %(phone_prefix)s."
    )
    VERIFICATION_ATTEMPT = (
        PREFIX + "OTP verification attempt for phone_prefix: %(phone_prefix)s."
    )
    VERIFY_NO_ACTIVE = (
        PREFIX + "Verification failed for %(phone_prefix)s: No active OTP found."
    )
    EXPIRED_DURING_VERIFICATION = (
        PREFIX + "OTP ID %(otp_id)s for %(phone_prefix)s expired during verification."
    )
    MAX_ATTEMPTS_REACHED = (
        PREFIX
        + "Max OTP attempts reached for OTP ID %(otp_id)s, phone_prefix: %(phone_prefix)s."
    )
    INVALID_ATTEMPT = (
        PREFIX
        + "Invalid OTP attempt for OTP ID %(otp_id)s, %(phone_prefix)s. Attempts left: %(attempts_left)s."
    )
    SUCCESSFULLY_VERIFIED = (
        PREFIX
        + "OTP ID %(otp_id)s successfully verified for phone_prefix: %(phone_prefix)s."
    )
    VERIFY_FAILED_ERROR = (
        PREFIX
        + "Verification for OTP ID %(otp_id)s, %(phone_prefix)s failed. Error: %(error)s"
    )
    INVALIDATING_EXISTING = (
        PREFIX
        + "Invalidating existing pending OTPs for phone_prefix: %(phone_prefix)s."
    )
    INVALIDATED_SUCCESS_COUNT = (
        PREFIX
        + "%(count)s pending OTPs invalidated for phone_prefix: %(phone_prefix)s."
    )
    INVALIDATE_FAILED = (
        PREFIX
        + "Failed to invalidate OTPs for phone_prefix: %(phone_prefix)s. Error: %(error)s"
    )
    UPDATING_STATUS = (
        PREFIX
        + "Attempting to update status for OTP ID %(otp_id)s from %(old_status)s to %(new_status)s."
    )
    STATUS_UPDATED_SUCCESS = (
        PREFIX + "Status for OTP ID %(otp_id)s updated successfully to %(new_status)s."
    )
    SETTING_SEND_ERROR = (
        PREFIX + "Attempting to set sending error for OTP ID %(otp_id)s."
    )
    SEND_ERROR_SET_SUCCESS = PREFIX + "Sending error status set for OTP ID %(otp_id)s."
    SET_SEND_ERROR_NOT_FOUND = (
        PREFIX + "OTP ID %(otp_id)s not found when trying to set sending error."
    )
    CLEANUP_STARTED = PREFIX + "Starting cleanup of expired/consumed OTPs."
    CLEANED_UP_SUCCESS_COUNT = (
        PREFIX + "%(count)s expired/consumed OTPs cleaned up successfully."
    )
    CLEANUP_FAILED = PREFIX + "OTP cleanup process failed. Error: %(error)s"


# --- User Sessions Repo Constants ---
class UserSessionModelConstants:
    """Constants related to the UserSessions model/table name."""

    TABLE_NAME = "user_sessions"
    MODEL_NAME = "PendingOTP"


class UserSessionRepoMessages:
    PREFIX = "REPO: UserSession - "

    CREATING = (
        PREFIX
        + "Attempting to create user session for user_id: %(user_id)s, jti_suffix: %(jti_suffix)s."
    )
    CREATED_SUCCESS = (
        PREFIX
        + "Session ID %(session_id)s created for user_id: %(user_id)s, jti_suffix: %(jti_suffix)s."
    )
    GET_BY_JTI = PREFIX + "Fetching session by jti_suffix: %(jti_suffix)s."
    FOUND_BY_JTI = (
        PREFIX + "Session ID %(session_id)s found by jti_suffix: %(jti_suffix)s."
    )
    NOT_FOUND_BY_JTI = PREFIX + "No session found for jti_suffix: %(jti_suffix)s."
    GET_ACTIVE_BY_JTI_USER = (
        PREFIX
        + "Fetching active session for user_id: %(user_id)s, jti_suffix: %(jti_suffix)s."
    )
    ACTIVE_FOUND_BY_JTI_USER = (
        PREFIX
        + "Active session ID %(session_id)s found for user_id: %(user_id)s, jti_suffix: %(jti_suffix)s."
    )
    ACTIVE_NOT_FOUND_BY_JTI_USER = (
        PREFIX
        + "No active session found for user_id: %(user_id)s, jti_suffix: %(jti_suffix)s."
    )
    INVALIDATING = (
        PREFIX
        + "Invalidating session ID: %(session_id)s for user_id: %(user_id)s, jti_suffix: %(jti_suffix)s."
    )
    INVALIDATED_SUCCESS = (
        PREFIX
        + "Session ID: %(session_id)s invalidated for user_id: %(user_id)s, jti_suffix: %(jti_suffix)s."
    )
    INVALIDATING_BY_JTI = PREFIX + "Invalidating session by jti_suffix: %(jti_suffix)s."
    INVALIDATE_BY_JTI_NOT_FOUND = (
        PREFIX + "Session not found for invalidation by jti_suffix: %(jti_suffix)s."
    )
    INVALIDATING_ALL_FOR_USER = (
        PREFIX
        + "Invalidating all sessions for user_id: %(user_id)s, excluding jti_suffix: %(excluded_jti_suffix)s."
    )
    INVALIDATE_ALL_NONE_FOUND = (
        PREFIX
        + "No active sessions found to invalidate for user_id: %(user_id)s, excluding jti_suffix: %(excluded_jti_suffix)s."
    )
    INVALIDATED_ALL_SUCCESS_COUNT = (
        PREFIX
        + "%(count)s sessions invalidated for user_id: %(user_id)s, excluding jti_suffix: %(excluded_jti_suffix)s."
    )
    INVALIDATE_ALL_FAILED = (
        PREFIX
        + "Failed to invalidate all sessions for user_id: %(user_id)s, excluding jti_suffix: %(excluded_jti_suffix)s. Error: %(error)s"
    )
    CLEANUP_STARTED = PREFIX + "Starting cleanup of revoked/expired user sessions."
    CLEANED_UP_SUCCESS_COUNT = (
        PREFIX + "%(count)s revoked/expired user sessions cleaned up."
    )
    CLEANUP_FAILED = PREFIX + "User session cleanup process failed. Error: %(error)s"
