# --- User Logging Strings ---
class UserLoggingStrings:
    # Profile Completion
    REQUEST_COMPLETE_PROFILE_TEMPLATE = "User {user_id} attempting to complete profile."
    PROFILE_ALREADY_COMPLETE_TEMPLATE = "Attempt to complete profile for user {user_id} denied: Profile already complete."
    PROFILE_COMPLETED_SUCCESS_TEMPLATE = (
        "Profile completed successfully for user {user_id}."
    )

    # Listing Users
    LIST_USERS_REQUEST_TEMPLATE = (
        "User {user_id} requesting to list users. Skip: {skip}, Limit: {limit}."
    )
    USERS_LISTED_TEMPLATE = "Listed {count} users for user {user_id}."

    # Getting User Details
    GET_ME_REQUEST_TEMPLATE = "User {user_id} requesting their own details (/me)."
    GET_ME_SUCCESS_TEMPLATE = "Successfully retrieved details for user {user_id} (/me)."
    GET_USER_BY_ID_REQUEST_TEMPLATE = (
        "User {current_user_id} requesting details for user ID {target_user_id}."
    )
    GET_USER_BY_ID_SUCCESS_TEMPLATE = (
        "Successfully retrieved details for user ID {target_user_id}."
    )

    # Updating User
    UPDATE_USER_REQUEST_TEMPLATE = (
        "User {current_user_id} attempting to update user ID {target_user_id}."
    )
    USER_UPDATED_SUCCESS_TEMPLATE = "Successfully updated user ID {target_user_id}."

    # Deleting User
    DELETE_USER_REQUEST_TEMPLATE = (
        "User {current_user_id} attempting to delete user ID {target_user_id}."
    )
    USER_DELETED_SUCCESS_TEMPLATE = "Successfully deleted user ID {target_user_id}."

    # Common Issues
    FORBIDDEN_TEMPLATE = "Forbidden access attempt by user {current_user_id} for resource/action: {action_description} on target user {target_user_id}."
    USER_NOT_FOUND_TEMPLATE = "User with ID {user_id} not found for action: {action}."


class UserServiceLoggingStrings:
    """Logging strings specific to the UserService."""

    _SERVICE_NAME = "UserService"

    # Get User Operations
    GET_USER_BY_ID_ATTEMPT_TEMPLATE = (
        "{service_name}: Attempting to get user by ID: {user_id}."
    )
    GET_USER_BY_ID_SUCCESS_TEMPLATE = (
        "{service_name}: Successfully retrieved user by ID: {user_id}."
    )
    GET_USER_BY_PHONE_ATTEMPT_TEMPLATE = (
        "{service_name}: Attempting to get user by phone: {phone_number}."
    )
    GET_USER_BY_PHONE_SUCCESS_TEMPLATE = (
        "{service_name}: Successfully retrieved user by phone: {phone_number}."
    )
    GET_USER_BY_EMAIL_ATTEMPT_TEMPLATE = (
        "{service_name}: Attempting to get user by email: {email}."
    )
    GET_USER_BY_EMAIL_SUCCESS_TEMPLATE = (
        "{service_name}: Successfully retrieved user by email: {email}."
    )
    GET_USERS_ATTEMPT_TEMPLATE = (
        "{service_name}: Attempting to get users with skip: {skip}, limit: {limit}."
    )
    GET_USERS_SUCCESS_TEMPLATE = "{service_name}: Successfully retrieved {count} users."

    # Create User via OTP
    CREATE_OTP_USER_ATTEMPT_TEMPLATE = (
        "{service_name}: Attempting to create user via OTP for phone: {phone_number}."
    )
    CREATE_OTP_USER_SUCCESS_TEMPLATE = (
        "{service_name}: Successfully created user via OTP. New user ID: {user_id}."
    )

    # Complete Profile
    COMPLETE_PROFILE_ATTEMPT_TEMPLATE = (
        "{service_name}: Attempting to complete profile for user ID {user_id}."
    )
    COMPLETE_PROFILE_SUCCESS_TEMPLATE = (
        "{service_name}: Successfully completed profile for user ID {user_id}."
    )

    # Update User Details
    UPDATE_USER_ATTEMPT_TEMPLATE = "{service_name}: User {current_user_id} attempting to update details for user ID {target_user_id}."
    UPDATE_USER_SUCCESS_TEMPLATE = "{service_name}: Successfully updated details for user ID {target_user_id} by user {current_user_id}."

    # Remove User
    REMOVE_USER_ATTEMPT_TEMPLATE = "{service_name}: User {current_user_id} attempting to delete user ID {target_user_id}."
    REMOVE_USER_SUCCESS_TEMPLATE = "{service_name}: Successfully deleted user ID {target_user_id} by user {current_user_id}."

    # Update Last Login
    UPDATE_LAST_LOGIN_ATTEMPT_TEMPLATE = (
        "{service_name}: Attempting to update last login for user ID {user_id}."
    )
    UPDATE_LAST_LOGIN_SUCCESS_TEMPLATE = (
        "{service_name}: Successfully updated last login for user ID {user_id}."
    )

    # Set Active Status
    SET_ACTIVE_STATUS_ATTEMPT_TEMPLATE = "{service_name}: Attempting to set active status to {is_active} for user ID {user_id}."
    SET_ACTIVE_STATUS_SUCCESS_TEMPLATE = "{service_name}: Successfully set active status to {is_active} for user ID {user_id}."
