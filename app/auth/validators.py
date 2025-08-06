# --- OTP Validation Logic ---
def validate_otp_format(otp_code: str) -> str:
    """
    Validates the format of an OTP code.

    The OTP must be exactly 6 digits long and contain only numerical characters.

    Args:
        otp_code: The OTP code string to validate.

    Returns:
        The validated OTP code if it's in the correct format.

    Raises:
        ValueError: If the OTP code is empty, not 6 digits long,
                    or contains non-digit characters.
    """
    if not otp_code:
        raise ValueError("OTP code cannot be empty.")

    # Check length first (common, fast check)
    if len(otp_code) != 6:
        raise ValueError("Invalid OTP format. Must be 6 digits long.")

    # Check if all characters are digits
    if not otp_code.isdigit():
        raise ValueError("Invalid OTP format. Must contain only digits.")

    return otp_code
