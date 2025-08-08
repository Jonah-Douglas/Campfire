# --- General Global Constants
class LoggingStrings:
    class BaseRepoLogMessages:
        DB_COMMIT_SUCCESS_TEMPLATE = "DB commit successful for %(model_name)s (ID: %(record_id)s) in method %(method_name)s."
        DB_REFRESH_SUCCESS_TEMPLATE = "DB refresh successful for %(model_name)s (ID: %(record_id)s) in method %(method_name)s."

        DB_OPERATION_ERROR_TEMPLATE = "Error during DB %(operation_verb)s for %(model_name)s in %(class_name)s.%(method_name)s: %(error)s"
        DB_ROLLBACK_INVOKED_TEMPLATE = "DB rollback invoked in method %(method_name)s for %(model_name)s due to error."
        DB_ROLLBACK_FAILURE_TEMPLATE = "CRITICAL: Failed to rollback transaction in %(class_name)s.%(method_name)s for %(model_name)s after error: %(rollback_error)s"

    class BaseRepo:
        GET_BY_ID_ATTEMPT = "Attempting to get %(model_name)s by ID: %(id)s."
        GET_BY_ID_SUCCESS = "Successfully retrieved %(model_name)s with ID: %(id)s."
        GET_BY_ID_NOT_FOUND = "%(model_name)s with ID: %(id)s not found."

        GET_MULTI_ATTEMPT = "Attempting to get multiple %(model_name)s (skip: %(skip)s, limit: %(limit)s)."
        GET_MULTI_SUCCESS = "Successfully retrieved %(count)s %(model_name)s(s)."

        CREATE_ATTEMPT_WITH_PREVIEW = (
            "Attempting to create %(model_name)s with data preview: %(data_preview)s."
        )
        CREATE_SUCCESS_LOG = (
            "%(model_name)s created successfully with ID: %(record_id)s."
        )

        UPDATE_ATTEMPT_WITH_PREVIEW = "Attempting to update %(model_name)s (ID: %(record_id)s) with data preview: %(data_preview)s."
        UPDATE_SUCCESS_LOG = "%(model_name)s (ID: %(record_id)s) updated successfully."

        DELETE_ATTEMPT = "Attempting to delete %(model_name)s with ID: %(record_id)s."
        DELETE_SUCCESS_LOG = "%(model_name)s (ID: %(record_id)s) deleted successfully."

        COUNT_ATTEMPT = "Attempting to count %(model_name)s."
        COUNT_SUCCESS = "Count for %(model_name)s: %(count)s."

        UNEXPECTED_ERROR_DURING_OPERATION = (
            "Unexpected error during %(operation_verb)s in %(class_name)s.%(method_name)s "
            "for %(model_name)s: %(error)s"
        )
        ENTITY_NOT_FOUND_BY_ID_TEMPLATE = "%(model_name)s with ID %(id)s not found."
        MODEL_MISSING_ID_FOR_ORDERING = "Model %(model_name)s has no 'id' attribute for default ordering in get_multi."
        UPDATE_FIELD_NOT_FOUND = "Field '%(field)s' not found on model %(model_name)s during update for ID %(record_id)s. Skipping."
        MODEL_MISSING_ID_FOR_COUNT = "Model %(model_name)s has no 'id' attribute for optimized count. Counting all rows."


class LoggingConstants:
    DATE_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"

    class LogColors:
        RESET = "\033[0m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
