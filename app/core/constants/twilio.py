# --- Twilio Constants
class TwilioServiceConstants:
    INIT_LOG_PREFIX = "TwilioSMSService Init:"
    SEND_SMS_LOG_PREFIX_TEMPLATE = "TwilioSMSService send_sms to {to_phone_number}:"
    SEND_SMS_RESULT = "Twilio API call for {to_phone_number} resulted in SID {message.sid}, Status {message.status}"

    # Configuration Messages
    CREDS_NOT_CONFIGURED = "Twilio Account SID or Auth Token is not configured."
    FROM_NUMBER_NOT_CONFIGURED = "Twilio 'From' phone number is not configured."
    FAILED_TO_INIT_CLIENT_TEMPLATE = "Failed to initialize Twilio client: {error}"
    AUTH_FAILED_TEMPLATE = "Twilio authentication failed: {error_msg}"
    CLIENT_NOT_INITIALIZED = "Twilio client not initialized or misconfigured."

    # SMS Sending Log Messages
    ATTEMPTING_TO_SEND_SMS_TEMPLATE = (
        "Attempting to send SMS. Body: '{body_preview}...' TestCreds: {use_test_creds}"
    )
    MESSAGE_ATTEMPT_RESULT_TEMPLATE = (
        "Message attempt result - SID: {sid}, Status: {status}, "
        "Error Code: {error_code}, Price: {price}"
    )
    SIMULATED_FAILURE_TEMPLATE = "SIMULATED FAILURE (Test Credentials) - Status: {status}, Error Code: {error_code}"
    ERROR_CODE_DESPITE_STATUS_TEMPLATE = (
        "Message has error code despite '{status}' status."
    )
    MESSAGE_FAILED_OR_UNDELIVERED = "Message failed or undelivered."
    MESSAGE_DELIVERED_SYNC_TEMPLATE = (
        "Message reported as delivered by API response (uncommon). SID: {sid}"
    )
    UNEXPECTED_STATUS_TEMPLATE = (
        "Twilio message has an unexpected status: {status}. SID: {sid}"
    )
    DELIVERED_WITHOUT_SID = (
        "{log_prefix} Message SID is None despite delivered status {message.status}"
    )
    MISSING_SID_AFTER_SUCCESS_AND_ERROR = (
        "SID missing after handling success with error code."
    )
    UNHANDLED_EXCEPTION = "Unhandled exception after API error processing."

    # Error Handling Helper Messages
    MAPPED_ERROR_TEMPLATE = (
        "Twilio SMS to {to_phone_number} resulted in mapped error: {error_detail}"
    )
    FAILED_WITH_STATUS_TEMPLATE = "Twilio SMS to {to_phone_number} failed with status '{status}'. Message: {error_message}"

    # Twilio API Error Messages
    API_ERROR_TEMPLATE = (
        "Twilio API Error: Status {status}, Code {code}, URI {uri}, Message: {msg}"
    )
    UNEXPECTED_SENDING_ERROR_TEMPLATE = "Unexpected error sending SMS: {error}"

    # Twilio Statuses
    STATUS_QUEUED = "queued"
    STATUS_ACCEPTED = "accepted"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_UNDELIVERED = "undelivered"
    STATUS_DELIVERED = "delivered"

    # Twilio Test Credential Indication Messages
    USING_TEST_CREDS = "Using Twilio Test Credentials for SMS."
    USING_LIVE_CREDS = "Using Twilio Live Credentials for SMS."
    CLIENT_INIT_SUCCESS = "Twilio client initialized successfully."
