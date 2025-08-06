# --- General Global Constants
class GeneralMessages:
    # JD TODO: Implement more of these
    INTERNAL_ERROR = (
        "An internal error occurred while processing your request. Please try again."
    )


# --- Standard Route Settings ---
class RouteSettings:
    # JD TODO: Do I need this header?
    HEADER_NAME = "X-Error-Code"
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 100
    MAX_LIMIT = 200
