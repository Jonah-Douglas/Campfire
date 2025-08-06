# --- Users Repo Constants ---
class UserModelConstants:
    """Constants related to the Users model/table name."""

    TABLE_NAME = "Users"
    MODEL_NAME = "User"


class UserRepoMessages:
    """Messages specific to User repository operations."""

    # Error Messages
    CREATE_NOT_IMPLEMENTED = (
        "Direct creation via this method is not supported for {model_name}s. "
        "Use create_user_for_otp_flow and then update_user_profile_completion."
    )

    # Logging - Get Operations
    GET_BY_EMAIL_ATTEMPT_TEMPLATE = "Attempting to find {model_name} by email: {email}."
    GET_BY_EMAIL_FOUND_TEMPLATE = "{model_name} found by email {email}: ID {user_id}."
    GET_BY_EMAIL_NOT_FOUND_TEMPLATE = "{model_name} not found by email: {email}."

    GET_BY_PHONE_ATTEMPT_TEMPLATE = (
        "Attempting to find {model_name} by phone number: {phone_number}."
    )
    GET_BY_PHONE_FOUND_TEMPLATE = (
        "{model_name} found by phone {phone_number}: ID {user_id}."
    )
    GET_BY_PHONE_NOT_FOUND_TEMPLATE = (
        "{model_name} not found by phone number: {phone_number}."
    )

    # Logging - Create OTP User
    CREATE_OTP_USER_ATTEMPT_TEMPLATE = (
        "Attempting to create {model_name} for OTP flow with phone: {phone_number}."
    )
    CREATE_OTP_USER_SUCCESS_TEMPLATE = "Successfully created {model_name} for OTP flow with phone {phone_number}. New {model_name} ID: {user_id}."

    # Logging - Update Profile Completion
    UPDATE_PROFILE_ATTEMPT_TEMPLATE = (
        "Attempting to complete profile for {model_name} ID: {user_id}."
    )
    UPDATE_PROFILE_SUCCESS_TEMPLATE = (
        "Successfully completed profile for {model_name} ID: {user_id}."
    )
    UPDATE_PROFILE_FIELD_SET_TEMPLATE = (
        "For {model_name} ID {user_id}, set field '{field_name}' to: {field_value}."
    )
    SET_PROFILE_COMPLETE_STATUS_TEMPLATE = (
        "Set is_profile_complete to {status} for {model_name} ID: {user_id}."
    )

    # Logging - Update Last Login
    UPDATE_LAST_LOGIN_ATTEMPT_TEMPLATE = (
        "Attempting to update last_login_at for {model_name} ID: {user_id}."
    )
    UPDATE_LAST_LOGIN_SUCCESS_TEMPLATE = "Successfully updated last_login_at for {model_name} ID: {user_id} to {last_login_at}."

    # Logging - Set Active Status
    SET_ACTIVE_STATUS_ATTEMPT_TEMPLATE = (
        "Attempting to set is_active to {is_active} for {model_name} ID: {user_id}."
    )
    SET_ACTIVE_STATUS_SUCCESS_TEMPLATE = (
        "Successfully set is_active to {is_active} for {model_name} ID: {user_id}."
    )
