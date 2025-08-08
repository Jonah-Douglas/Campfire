# --- Users Repo Constants ---
class UserModelConstants:
    """Constants related to the Users model/table name."""

    TABLE_NAME = "Users"
    MODEL_NAME = "User"


class UserRepoMessages:
    """Messages specific to User repository operations."""

    # Error Messages
    CREATE_NOT_IMPLEMENTED = (
        "Direct creation via this method is not supported for %(model_name)ss. "
        "Use create_user_for_otp_flow and then update_user_profile_completion."
    )
    EXISTENCE_CHECK_ATTEMPT_TEMPLATE = "Attempting to check existence for %(model_name)s by %(field_name)s: %(field_value)s in %(class_name)s.%(method_name)s."
    EXISTENCE_CHECK_RESULT_TEMPLATE = "%(model_name)s with %(field_name)s %(field_value)s %(exists_status)s. (%(class_name)s.%(method_name)s)"

    # Logging - Get Operations
    GET_BY_EMAIL_ATTEMPT_TEMPLATE = (
        "Attempting to find %(model_name)s by email: %(email)s."
    )
    GET_BY_EMAIL_FOUND_TEMPLATE = (
        "%(model_name)s found by email %(email)s: ID %(user_id)s."
    )
    GET_BY_EMAIL_NOT_FOUND_TEMPLATE = "%(model_name)s not found by email: %(email)s."

    GET_BY_PHONE_ATTEMPT_TEMPLATE = (
        "Attempting to find %(model_name)s by phone number: %(phone_number)s."
    )
    GET_BY_PHONE_FOUND_TEMPLATE = (
        "%(model_name)s found by phone %(phone_number)s: ID %(user_id)s."
    )
    GET_BY_PHONE_NOT_FOUND_TEMPLATE = (
        "%(model_name)s not found by phone number: %(phone_number)s."
    )

    # Logging - Create OTP User
    CREATE_OTP_USER_ATTEMPT_TEMPLATE = (
        "Attempting to create %(model_name)s for OTP flow with phone: %(phone_number)s."
    )
    CREATE_OTP_USER_SUCCESS_TEMPLATE = "Successfully created %(model_name)s for OTP flow with phone %(phone_number)s. New %(model_name)s ID: %(user_id)s."

    # Logging - Update Profile Completion
    UPDATE_PROFILE_ATTEMPT_TEMPLATE = (
        "Attempting to complete profile for %(model_name)s ID: %(user_id)s."
    )
    UPDATE_PROFILE_SUCCESS_TEMPLATE = (
        "Successfully completed profile for %(model_name)s ID: %(user_id)s."
    )
    UPDATE_PROFILE_FIELD_SET_TEMPLATE = "For %(model_name)s ID %(user_id)s, set field '%(field_name)s' to: %(field_value)s."
    SET_PROFILE_COMPLETE_STATUS_TEMPLATE = (
        "Set is_profile_complete to %(status)s for %(model_name)s ID: %(user_id)s."
    )

    # Logging - Update Last Login
    UPDATE_LAST_LOGIN_ATTEMPT_TEMPLATE = (
        "Attempting to update last_login_at for %(model_name)s ID: %(user_id)s."
    )
    UPDATE_LAST_LOGIN_SUCCESS_TEMPLATE = "Successfully updated last_login_at for %(model_name)s ID: %(user_id)s to %(last_login_at)s."

    # Logging - Set Active Status
    SET_ACTIVE_STATUS_ATTEMPT_TEMPLATE = "Attempting to set is_active to %(is_active)s for %(model_name)s ID: %(user_id)s."
    SET_ACTIVE_STATUS_SUCCESS_TEMPLATE = "Successfully set is_active to %(is_active)s for %(model_name)s ID: %(user_id)s."
