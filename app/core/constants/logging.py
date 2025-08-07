# --- General Global Constants
class LoggingStrings:
    class BaseRepoLogMessages:
        DB_COMMIT_SUCCESS_TEMPLATE = "DB commit successful for {model_name} (ID: {record_id}) in method {method_name}."
        DB_REFRESH_SUCCESS_TEMPLATE = "DB refresh successful for {model_name} (ID: {record_id}) in method {method_name}."

        DB_OPERATION_ERROR_TEMPLATE = "Error during DB {operation_verb} for {model_name} in {class_name}.{method_name}: {error}"
        DB_ROLLBACK_INVOKED_TEMPLATE = (
            "DB rollback invoked in method {method_name} for {model_name} due to error."
        )
        DB_ROLLBACK_FAILURE_TEMPLATE = "CRITICAL: Failed to rollback transaction in {class_name}.{method_name} for {model_name} after error: {rollback_error}"

    class BaseRepo:
        GET_BY_ID_ATTEMPT = "Attempting to get {model_name} by ID: {id}."
        GET_BY_ID_SUCCESS = "Successfully retrieved {model_name} with ID: {id}."
        GET_BY_ID_NOT_FOUND = "{model_name} with ID: {id} not found."

        GET_MULTI_ATTEMPT = (
            "Attempting to get multiple {model_name} (skip: {skip}, limit: {limit})."
        )
        GET_MULTI_SUCCESS = "Successfully retrieved {count} {model_name}(s)."

        CREATE_ATTEMPT_WITH_PREVIEW = (
            "Attempting to create {model_name} with data preview: {data_preview}."
        )
        CREATE_SUCCESS_LOG = "{model_name} created successfully with ID: {record_id}."

        UPDATE_ATTEMPT_WITH_PREVIEW = "Attempting to update {model_name} (ID: {record_id}) with data preview: {data_preview}."
        UPDATE_SUCCESS_LOG = "{model_name} (ID: {record_id}) updated successfully."

        DELETE_ATTEMPT = "Attempting to delete {model_name} with ID: {record_id}."
        DELETE_SUCCESS_LOG = "{model_name} (ID: {record_id}) deleted successfully."

        COUNT_ATTEMPT = "Attempting to count {model_name}."
        COUNT_SUCCESS = "Count for {model_name}: {count}."

        UNEXPECTED_ERROR_DURING_OPERATION = (
            "Unexpected error during {operation_verb} in {class_name}.{method_name} "
            "for {model_name}: {error}"
        )
        ENTITY_NOT_FOUND_BY_ID_TEMPLATE = "{model_name} with ID {id} not found."
        MODEL_MISSING_ID_FOR_ORDERING = "Model {model_name} has no 'id' attribute for default ordering in get_multi."
        UPDATE_FIELD_NOT_FOUND = "Field '{field}' not found on model {model_name} during update for ID {record_id}. Skipping."
        MODEL_MISSING_ID_FOR_COUNT = "Model {model_name} has no 'id' attribute for optimized count. Counting all rows."


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
