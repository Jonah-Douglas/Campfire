# --- User Logging Strings ---
class UserLoggingStrings:
    # Profile Completion
    REQUEST_COMPLETE_PROFILE_TEMPLATE = (
        "User %(user_id)s attempting to complete profile."
    )
    PROFILE_ALREADY_COMPLETE_TEMPLATE = "Attempt to complete profile for user %(user_id)s denied: Profile already complete."
    PROFILE_COMPLETED_SUCCESS_TEMPLATE = (
        "Profile completed successfully for user %(user_id)s."
    )

    # Listing Users
    LIST_USERS_REQUEST_TEMPLATE = (
        "User %(user_id)s requesting to list users. Skip: %(skip)s, Limit: %(limit)s."
    )
    USERS_LISTED_TEMPLATE = "Listed %(count)s users for user %(user_id)s."

    # Getting User Details
    GET_ME_REQUEST_TEMPLATE = "User %(user_id)s requesting their own details (/me)."
    GET_ME_SUCCESS_TEMPLATE = (
        "Successfully retrieved details for user %(user_id)s (/me)."
    )
    GET_USER_BY_ID_REQUEST_TEMPLATE = (
        "User %(current_user_id)s requesting details for user ID %(target_user_id)s."
    )
    GET_USER_BY_ID_SUCCESS_TEMPLATE = (
        "Successfully retrieved details for user ID %(target_user_id)s."
    )

    # Updating User
    UPDATE_USER_REQUEST_TEMPLATE = (
        "User %(current_user_id)s attempting to update user ID %(target_user_id)s."
    )
    USER_UPDATED_SUCCESS_TEMPLATE = "Successfully updated user ID %(target_user_id)s."

    # Deleting User
    DELETE_USER_REQUEST_TEMPLATE = (
        "User %(current_user_id)s attempting to delete user ID %(target_user_id)s."
    )
    USER_DELETED_SUCCESS_TEMPLATE = "Successfully deleted user ID %(target_user_id)s."

    # Common Issues
    FORBIDDEN_TEMPLATE = "Forbidden access attempt by user %(current_user_id)s for resource/action: %(action_description)s on target user %(target_user_id)s."


class UserServiceLoggingStrings:
    """Logging strings specific to the UserService."""

    _SERVICE_NAME = "UserService"

    # Get User Operations
    GET_USER_BY_ID_ATTEMPT_TEMPLATE = (
        "%(service_name)s: Attempting to get user by ID: %(user_id)s."
    )
    GET_USER_BY_ID_SUCCESS_TEMPLATE = (
        "%(service_name)s: Successfully retrieved user by ID: %(user_id)s."
    )
    GET_USER_BY_PHONE_ATTEMPT_TEMPLATE = (
        "%(service_name)s: Attempting to get user by phone: %(phone_number)s."
    )
    GET_USER_BY_PHONE_SUCCESS_TEMPLATE = (
        "%(service_name)s: Successfully retrieved user by phone: %(phone_number)s."
    )
    GET_USER_BY_EMAIL_ATTEMPT_TEMPLATE = (
        "%(service_name)s: Attempting to get user by email: %(email)s."
    )
    GET_USER_BY_EMAIL_SUCCESS_TEMPLATE = (
        "%(service_name)s: Successfully retrieved user by email: %(email)s."
    )
    GET_USERS_ATTEMPT_TEMPLATE = "%(service_name)s: Attempting to get users with skip: %(skip)s, limit: %(limit)s."
    GET_USERS_SUCCESS_TEMPLATE = (
        "%(service_name)s: Successfully retrieved %(count)s users."
    )

    # Create User via OTP
    CREATE_OTP_USER_ATTEMPT_TEMPLATE = "%(service_name)s: Attempting to create user via OTP for phone: %(phone_number)s."
    CREATE_OTP_USER_SUCCESS_TEMPLATE = (
        "%(service_name)s: Successfully created user via OTP. New user ID: %(user_id)s."
    )

    # Complete Profile
    COMPLETE_PROFILE_ATTEMPT_TEMPLATE = (
        "%(service_name)s: Attempting to complete profile for user ID %(user_id)s."
    )
    COMPLETE_PROFILE_SUCCESS_TEMPLATE = (
        "%(service_name)s: Successfully completed profile for user ID %(user_id)s."
    )

    # Check Field Uniqueness
    UNSUPPORTED_FIELD = "%(service_name)s: Unsupported field_name '%(field_name)s' in _check_field_uniqueness"
    ERROR_FIELD_UNIQUENESS = "%(service_name)s: Unexpected error during %(field_name)s uniqueness check for user %(user_id_to_update)s: %(e)s"

    # Update User Details
    UPDATE_USER_ATTEMPT_TEMPLATE = "%(service_name)s: User %(current_user_id)s attempting to update details for user ID %(target_user_id)s."
    UPDATE_USER_SUCCESS_TEMPLATE = "%(service_name)s: Successfully updated details for user ID %(target_user_id)s by user %(current_user_id)s."
    NO_UPDATE_DATA = "%(service_name)s: No update data provided for user %(user_id_to_update)s. Returning existing user."
    FAILED_TO_UPDATE_USER = "%(service_name)s: Failed to update user %(user_id_to_update)s in repository: %(e)s"

    # Remove User
    REMOVE_USER_ATTEMPT_TEMPLATE = "%(service_name)s: User %(current_user_id)s attempting to delete user ID %(target_user_id)s."
    REMOVE_USER_SUCCESS_TEMPLATE = "%(service_name)s: Successfully deleted user ID %(target_user_id)s by user %(current_user_id)s."

    # Update Last Login
    UPDATE_LAST_LOGIN_ATTEMPT_TEMPLATE = (
        "%(service_name)s: Attempting to update last login for user ID %(user_id)s."
    )
    UPDATE_LAST_LOGIN_SUCCESS_TEMPLATE = (
        "%(service_name)s: Successfully updated last login for user ID %(user_id)s."
    )

    # Set Active Status
    SET_ACTIVE_STATUS_ATTEMPT_TEMPLATE = "%(service_name)s: Attempting to set active status to %(is_active)s for user ID %(user_id)s."
    SET_ACTIVE_STATUS_SUCCESS_TEMPLATE = "%(service_name)s: Successfully set active status to %(is_active)s for user ID %(user_id)s."
