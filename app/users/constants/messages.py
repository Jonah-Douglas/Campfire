# --- User Messages ---
class UserSuccessMessages:
    PROFILE_COMPLETED = "User profile completed successfully."
    USERS_RETRIEVED = "Users retrieved successfully."
    CURRENT_USER_RETRIEVED = "Current user details retrieved successfully."
    USER_BY_ID_RETRIEVED_TEMPLATE = (
        "User details for ID {user_id} retrieved successfully."
    )
    USER_UPDATED_TEMPLATE = "User with ID {user_id} updated successfully."
    USER_DELETED_SUCCESS_TEMPLATE = "User with ID {user_id} deleted successfully."


class UserHttpErrorDetails:
    PROFILE_ALREADY_COMPLETE = "Profile has already been completed."
    FORBIDDEN_ACCESS_RESOURCE = "You do not have permission to access this resource."
    FORBIDDEN_VIEW_USER = "You do not have permission to view this user's details."
    FORBIDDEN_UPDATE_USER = "You do not have permission to update this user."
    USER_NOT_FOUND_TEMPLATE = "User with ID {user_id} not found."
    USER_NOT_FOUND_GENERIC = "User not found."

    # Service Specific Error Details
    PHONE_ALREADY_EXISTS_TEMPLATE = (
        "A user with this phone number ({phone_number}) already exists."
    )
    EMAIL_ALREADY_EXISTS_TEMPLATE = (
        "This email address ({email}) is already in use by another account."
    )
    EMAIL_ALREADY_IN_USE = "This email address is already in use."
    PHONE_ALREADY_IN_USE = "This phone number is already in use."

    USER_CREATION_FAILED = "Could not create user."
    PROFILE_COMPLETION_FAILED = "Failed to complete user profile."
    USER_UPDATE_FAILED = "Failed to update user."

    NOT_AUTHORIZED_TO_UPDATE_USER = "Not authorized to update this user."
    SUPERUSER_SELF_DELETE_NOT_ALLOWED = (
        "Superusers cannot delete their own accounts through this general endpoint."
    )
    FORBIDDEN_DELETE_USER = "You do not have permission to delete this user."
    USER_DELETE_NOT_FOUND_BY_REPO = "User to delete not found by delete operation."
    USER_DELETE_ERROR = "An error occurred while deleting the user."

    UPDATE_LAST_LOGIN_ERROR = (
        "An error occurred while updating the user's last login time."
    )

    SET_ACTIVE_STATUS_ERROR = (
        "An error occurred while setting the user's active status."
    )
