# --- General Logging ---
class GeneralLogs:
    INIT_TEMPLATE = "Initialized {class_name}."
    METHOD_ENTRY_TEMPLATE = "Entering {class_name}.{method_name}."
    METHOD_ERROR_TEMPLATE = "Error in {class_name}.{method_name}: {error}."
    GENERIC_CREATE_NOT_IMPLEMENTED = "Generic create is not implemented for {self._MODEL_NAME}. Use create_pending_otp."
    GENERIC_UPDATE_NOT_IMPLEMENTED = (
        "Generic update is not implemented for {self._MODEL_NAME}."
    )
