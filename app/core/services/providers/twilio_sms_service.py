import asyncio
from typing import Never

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from twilio.rest.api.v2010.account.message import MessageInstance

from app.core.config import settings
from app.core.constants import TwilioServiceConstants
from app.core.logging.logger_wrapper import firelog
from app.core.services.interfaces.sms_service_interface import (
    ConfigurationError,
    InsufficientCreditsError,
    InvalidPhoneNumberError,
    SMSSendingError,
    SMSServiceInterface,
    SMSServiceProviderError,
)

# Mapping of some common Twilio error codes to custom exceptions
# See: https://www.twilio.com/docs/api/errors
TWILIO_ERROR_CODE_MAP = {
    "21211": InvalidPhoneNumberError,  # Invalid 'To' Phone Number
    "21212": InvalidPhoneNumberError,  # Invalid 'From' Phone Number (should be caught by config)
    "21214": InvalidPhoneNumberError,  # Unable to route message
    "21608": InsufficientCreditsError,  # The 'To' phone number is not currently reachable via SMS.
    "21610": InvalidPhoneNumberError,  # The 'To' phone number is not opted in for messages from this number.
    "21614": InvalidPhoneNumberError,  # 'To' number is not SMS-capable
    "30001": SMSServiceProviderError,  # Queue Overflow
    "30003": SMSServiceProviderError,  # Unreachable destination handset
    "30004": SMSServiceProviderError,  # Message blocked (e.g., spam filter, carrier block)
    "30005": SMSServiceProviderError,  # Unknown destination handset
    "30006": SMSServiceProviderError,  # Landline or unreachable carrier
    "30007": SMSServiceProviderError,  # Carrier Violation (content blocked)
    "30008": SMSServiceProviderError,  # Unknown error
}


class TwilioSMSService(SMSServiceInterface):
    def __init__(self) -> None:
        self.use_test_creds = settings.TWILIO_USE_TEST_CREDENTIALS
        log_prefix = TwilioServiceConstants.INIT_LOG_PREFIX

        if self.use_test_creds:
            self.account_sid = settings.TWILIO_TEST_ACCOUNT_SID
            self.auth_token = settings.TWILIO_TEST_AUTH_TOKEN
            firelog.info(f"{log_prefix} {TwilioServiceConstants.USING_TEST_CREDS}")
        else:
            self.account_sid = settings.TWILIO_ACCOUNT_SID
            self.auth_token = settings.TWILIO_AUTH_TOKEN
            firelog.info(f"{log_prefix} {TwilioServiceConstants.USING_LIVE_CREDS}")

        if not self.account_sid or not self.auth_token:
            msg = TwilioServiceConstants.CREDS_NOT_CONFIGURED
            firelog.error(f"{log_prefix} {msg}")
            raise ConfigurationError(msg, to_phone_number=None)

        self.from_phone_number = settings.TWILIO_FROM_PHONE_NUMBER
        if not self.from_phone_number:
            msg = TwilioServiceConstants.FROM_NUMBER_NOT_CONFIGURED
            firelog.error(f"{log_prefix} {msg}")
            raise ConfigurationError(msg, to_phone_number=None)

        try:
            self.client = Client(self.account_sid, self.auth_token)
            firelog.info(f"{log_prefix} {TwilioServiceConstants.CLIENT_INIT_SUCCESS}")
        except Exception as e:
            msg = TwilioServiceConstants.FAILED_TO_INIT_CLIENT_TEMPLATE.format(error=e)
            firelog.error(f"{log_prefix} {msg}", exc_info=True)
            if isinstance(e, TwilioRestException) and e.status == 401:
                raise ConfigurationError(
                    TwilioServiceConstants.AUTH_FAILED_TEMPLATE.format(error_msg=e.msg),
                    provider_error_code=str(e.code),
                ) from e
            raise SMSServiceProviderError(
                msg, provider_error_code=str(getattr(e, "code", None))
            ) from e

    def _handle_twilio_error(
        self,
        to_phone_number: str,
        error_code_str: str | None,
        error_message: str | None,
        status: str | None,
    ) -> Never:
        """Helper to raise appropriate custom exceptions based on Twilio error codes."""
        if error_code_str:
            exception_class = TWILIO_ERROR_CODE_MAP.get(
                error_code_str, SMSServiceProviderError
            )
            error_detail = f"Twilio Status: {status}, Error Code: {error_code_str}, Message: {error_message}"
            firelog.warning(
                TwilioServiceConstants.MAPPED_ERROR_TEMPLATE.format(
                    to_phone_number=to_phone_number, error_detail=error_detail
                )
            )
            raise exception_class(
                error_detail,
                provider_error_code=error_code_str,
                to_phone_number=to_phone_number,
            )
        else:
            msg = TwilioServiceConstants.FAILED_WITH_STATUS_TEMPLATE.format(
                to_phone_number=to_phone_number,
                status=status,
                error_message=error_message,
            )
            firelog.warning(msg)
            raise SMSServiceProviderError(msg, to_phone_number=to_phone_number)

    async def _make_twilio_api_call(
        self, to_phone_number: str, message_body: str
    ) -> MessageInstance:
        """Makes the actual API call to Twilio to create a message."""
        firelog.debug(TwilioServiceConstants.ATTEMPTING_TO_SEND_SMS_TEMPLATE)

        message = await asyncio.to_thread(
            self.client.messages.create,
            body=message_body,
            from_=self.from_phone_number,
            to=to_phone_number,
        )

        firelog.info(TwilioServiceConstants.SEND_SMS_RESULT)
        return message

    async def _handle_api_exception(
        self, e: Exception, to_phone_number: str, log_prefix: str
    ) -> None:  # This method will always raise
        """Handles exceptions specifically from the Twilio API call or other unexpected errors."""
        if isinstance(e, TwilioRestException):
            error_code_str = str(e.code)
            error_msg = TwilioServiceConstants.API_ERROR_TEMPLATE.format(
                status=e.status, code=e.code, uri=e.uri, msg=e.msg
            )
            firelog.error(f"{log_prefix} {error_msg}", exc_info=True)

            exception_class = TWILIO_ERROR_CODE_MAP.get(
                error_code_str, SMSServiceProviderError
            )
            if e.status == 401:
                exception_class = ConfigurationError

            # Extracting the user-facing part of the message
            user_facing_error_detail = e.msg  # Or a more processed version
            if " Message: " in error_msg:  # From your original code
                user_facing_error_detail = error_msg.split(" Message: ")[1]

            raise exception_class(
                user_facing_error_detail,
                provider_error_code=error_code_str,
                to_phone_number=to_phone_number,
            ) from e
        else:
            # Generic exception
            msg = TwilioServiceConstants.UNEXPECTED_SENDING_ERROR_TEMPLATE.format(
                error=e
            )
            firelog.error(f"{log_prefix} {msg}", exc_info=True)
            raise SMSSendingError(msg, to_phone_number=to_phone_number) from e

    def _process_twilio_message_response(
        self, message: MessageInstance, to_phone_number: str, log_prefix: str
    ) -> str:
        """Processes the Twilio message object, checks status, and handles outcomes."""

        success_statuses = [
            TwilioServiceConstants.STATUS_QUEUED,
            TwilioServiceConstants.STATUS_ACCEPTED,
            TwilioServiceConstants.STATUS_SENT,
        ]
        failure_statuses = [
            TwilioServiceConstants.STATUS_FAILED,
            TwilioServiceConstants.STATUS_UNDELIVERED,
        ]

        # Scenario 1: Success-like statuses
        if message.status in success_statuses:
            if message.error_code:
                return self._handle_success_with_error_code(
                    message, to_phone_number, log_prefix
                )

            if message.sid is None:
                msg = TwilioServiceConstants.DELIVERED_WITHOUT_SID
                firelog.error(f"{log_prefix} {msg}")
                raise SMSServiceProviderError(
                    msg,
                    provider_error_code=str(message.error_code),
                    to_phone_number=to_phone_number,
                )
            return message.sid

        # Scenario 2: Explicit failure statuses
        elif message.status in failure_statuses:
            firelog.error(
                f"{log_prefix} {TwilioServiceConstants.MESSAGE_FAILED_OR_UNDELIVERED}"
            )
            self._handle_twilio_error(
                to_phone_number,
                str(message.error_code),
                message.error_message,
                str(message.status),
            )

        # Scenario 3: Delivered status (often treated as ultimate success)
        elif message.status == TwilioServiceConstants.STATUS_DELIVERED:
            firelog.info(
                TwilioServiceConstants.MESSAGE_DELIVERED_SYNC_TEMPLATE.format(
                    log_prefix_val=log_prefix, sid=message.sid
                ).replace("{log_prefix_val} ", log_prefix)
            )
            if message.sid is None:
                msg = TwilioServiceConstants.DELIVERED_WITHOUT_SID
                firelog.error(f"{log_prefix} {msg}")
                raise SMSServiceProviderError(
                    msg,
                    provider_error_code=str(message.error_code),
                    to_phone_number=to_phone_number,
                )
            return message.sid

        # Scenario 4: Unexpected status
        else:
            msg = TwilioServiceConstants.UNEXPECTED_STATUS_TEMPLATE.format(
                status=message.status, sid=message.sid
            )
            firelog.warning(f"{log_prefix} {msg}")
            raise SMSServiceProviderError(
                msg,
                provider_error_code=str(message.error_code),
                to_phone_number=to_phone_number,
            )
        raise SMSServiceProviderError(
            "Reached unexpected end of status processing.",
            to_phone_number=to_phone_number,
        )

    def _handle_success_with_error_code(
        self, message: MessageInstance, to_phone_number: str, log_prefix: str
    ) -> str:
        """Handles cases where status is success-like but message.error_code is present."""
        if self.use_test_creds:
            firelog.warning(
                TwilioServiceConstants.SIMULATED_FAILURE_TEMPLATE.format(
                    log_prefix_val=log_prefix,
                    status=message.status,
                    error_code=message.error_code,
                ).replace("{log_prefix_val} ", log_prefix)
            )
            self._handle_twilio_error(
                to_phone_number,
                str(message.error_code),
                message.error_message,
                str(message.status),
            )
        else:
            firelog.error(
                TwilioServiceConstants.ERROR_CODE_DESPITE_STATUS_TEMPLATE.format(
                    log_prefix_val=log_prefix, status=message.status
                ).replace("{log_prefix_val} ", log_prefix)
            )
            self._handle_twilio_error(
                to_phone_number,
                str(message.error_code),
                message.error_message,
                str(message.status),
            )
        if message.sid is None:
            raise SMSServiceProviderError(
                TwilioServiceConstants.MISSING_SID_AFTER_SUCCESS_AND_ERROR,
                to_phone_number=to_phone_number,
            )
        return message.sid

    async def send_sms(self, to_phone_number: str, message_body: str) -> str:
        log_prefix = TwilioServiceConstants.SEND_SMS_LOG_PREFIX_TEMPLATE.format(
            to_phone_number=to_phone_number
        )

        if not self.client:
            msg = TwilioServiceConstants.CLIENT_NOT_INITIALIZED
            firelog.error(f"{log_prefix} {msg}")
            raise ConfigurationError(msg, to_phone_number=to_phone_number)

        if not self.from_phone_number:
            msg = TwilioServiceConstants.FROM_NUMBER_NOT_CONFIGURED
            firelog.error(f"{log_prefix} {msg}")
            raise ConfigurationError(msg, to_phone_number=to_phone_number)

        try:
            message_instance = await self._make_twilio_api_call(
                to_phone_number, message_body
            )

            firelog.info(
                TwilioServiceConstants.MESSAGE_ATTEMPT_RESULT_TEMPLATE.format(
                    log_prefix_val=log_prefix,
                    sid=message_instance.sid,
                    status=message_instance.status,
                    error_code=message_instance.error_code,
                    price=message_instance.price,
                ).replace("{log_prefix_val} ", log_prefix)
            )

            return self._process_twilio_message_response(
                message_instance, to_phone_number, log_prefix
            )

        except Exception as e:
            await self._handle_api_exception(e, to_phone_number, log_prefix)
            raise SMSSendingError(
                TwilioServiceConstants.UNHANDLED_EXCEPTION,
                to_phone_number=to_phone_number,
            ) from e
