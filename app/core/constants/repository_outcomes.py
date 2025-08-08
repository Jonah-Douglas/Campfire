# --- General Logging ---
class GeneralLogs:
    # JD TODO: Implement more of these
    INIT_TEMPLATE = "Initialized %(class_name)s."
    METHOD_ERROR_TEMPLATE = "Error in %(class_name)s.%(method_name)s: %(error)s."
    GENERIC_CREATE_NOT_IMPLEMENTED = (
        "Generic create is not implemented for %(class_model_name)s."
    )
    GENERIC_UPDATE_NOT_IMPLEMENTED = (
        "Generic update is not implemented for %(class_model_name)s."
    )
