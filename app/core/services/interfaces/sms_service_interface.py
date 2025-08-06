from abc import ABC, abstractmethod


# --- Custom Exceptions ---
class SMSSendingError(Exception):
    """Base exception for SMS sending failures."""

    def __init__(
        self,
        message: str,
        provider_error_code: str | None = None,
        to_phone_number: str | None = None,
    ) -> None:
        super().__init__(message)
        self.provider_error_code = provider_error_code
        self.to_phone_number = to_phone_number


class InvalidPhoneNumberError(SMSSendingError):
    """Indicates the recipient's phone number is invalid or not reachable."""

    pass


class SMSServiceProviderError(SMSSendingError):
    """Indicates an issue with the SMS provider itself (e.g., API down, auth failure, rate limit)."""

    pass


class InsufficientCreditsError(SMSSendingError):
    """Indicates the account does not have enough credits to send the SMS."""

    pass


class ConfigurationError(SMSSendingError):
    """Indicates a configuration problem with the SMS service."""

    pass


# --- Interface ---
class SMSServiceInterface(ABC):
    @abstractmethod
    async def send_sms(self, to_phone_number: str, message_body: str) -> str:
        """
        Sends an SMS message.

        Args:
            to_phone_number: The recipient's phone number.
            message_body: The content of the SMS.

        Returns:
            str: A unique message identifier (SID) from the provider if the message
                 was successfully accepted for delivery.

        Raises:
            InvalidPhoneNumberError: If the phone number is determined to be invalid by the provider.
            InsufficientCreditsError: If the account lacks funds for sending.
            SMSServiceProviderError: If the SMS provider encounters an internal or configuration issue,
                                     or if the message status indicates a definitive failure.
            ConfigurationError: If the service is misconfigured.
            SMSSendingError: For other generic sending errors not covered above.
        """
        pass
