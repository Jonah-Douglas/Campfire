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
        _init_log_prefix = TwilioServiceConstants.INIT_LOG_PREFIX

        log_extra_init = {"use_test_creds": self.use_test_creds}

        if self.use_test_creds:
            self.account_sid = settings.TWILIO_TEST_ACCOUNT_SID
            self.auth_token = settings.TWILIO_TEST_AUTH_TOKEN
            firelog.info(
                f"{_init_log_prefix} {TwilioServiceConstants.USING_TEST_CREDS}",
                extra=log_extra_init,
            )
        else:
            self.account_sid = settings.TWILIO_ACCOUNT_SID
            self.auth_token = settings.TWILIO_AUTH_TOKEN
            firelog.info(
                f"{_init_log_prefix} {TwilioServiceConstants.USING_LIVE_CREDS}",
                extra=log_extra_init,
            )

        if not self.account_sid or not self.auth_token:
            msg = TwilioServiceConstants.CREDS_NOT_CONFIGURED
            firelog.error(f"{_init_log_prefix} {msg}", extra=log_extra_init)
            raise ConfigurationError(msg, to_phone_number=None)

        self.from_phone_number = settings.TWILIO_FROM_PHONE_NUMBER
        if not self.from_phone_number:
            msg = TwilioServiceConstants.FROM_NUMBER_NOT_CONFIGURED
            firelog.error(f"{_init_log_prefix} {msg}", extra=log_extra_init)
            raise ConfigurationError(msg, to_phone_number=None)

        try:
            self.client = Client(self.account_sid, self.auth_token)
            firelog.info(
                f"{_init_log_prefix} {TwilioServiceConstants.CLIENT_INIT_SUCCESS}",
                extra=log_extra_init,
            )
        except Exception as e:
            log_extra_init_fail = {**log_extra_init, "error": str(e)}
            firelog.error(
                f"{_init_log_prefix} {TwilioServiceConstants.FAILED_TO_INIT_CLIENT_TEMPLATE}",
                exc_info=True,
                extra=log_extra_init_fail,
            )
            if isinstance(e, TwilioRestException) and e.status == 401:
                raise ConfigurationError(
                    TwilioServiceConstants.AUTH_FAILED_TEMPLATE.format(error_msg=e.msg),
                    provider_error_code=str(e.code),
                ) from e
            raise SMSServiceProviderError(
                TwilioServiceConstants.FAILED_TO_INIT_CLIENT_TEMPLATE
                % log_extra_init_fail,
                provider_error_code=str(getattr(e, "code", None)),
            ) from e

    def _handle_twilio_error(
        self,
        to_phone_number: str,
        error_code_str: str | None,
        error_message: str | None,
        status: str | None,
        current_log_prefix: str,
    ) -> Never:
        """Helper to raise appropriate custom exceptions based on Twilio error codes."""
        if error_code_str:
            exception_class = TWILIO_ERROR_CODE_MAP.get(
                error_code_str, SMSServiceProviderError
            )
            error_detail_for_exc = f"Twilio Status: {status}, Error Code: {error_code_str}, Message: {error_message}"
            log_extra_mapped_error = {
                "to_phone_number": to_phone_number,
                "error_detail": error_detail_for_exc,
            }
            firelog.warning(
                f"{current_log_prefix} {TwilioServiceConstants.MAPPED_ERROR_TEMPLATE}",
                extra=log_extra_mapped_error,
            )
            raise exception_class(
                error_detail_for_exc,
                provider_error_code=error_code_str,
                to_phone_number=to_phone_number,
            )
        else:
            log_extra_failed_status = {
                "to_phone_number": to_phone_number,
                "status": str(status),
                "error_message": str(error_message),
            }
            firelog.warning(
                f"{current_log_prefix} {TwilioServiceConstants.FAILED_WITH_STATUS_TEMPLATE}",
                extra=log_extra_failed_status,
            )
            raise SMSServiceProviderError(
                TwilioServiceConstants.FAILED_WITH_STATUS_TEMPLATE
                % log_extra_failed_status,
                to_phone_number=to_phone_number,
            )

    async def _make_twilio_api_call(
        self, to_phone_number: str, message_body: str, current_log_prefix: str
    ) -> MessageInstance:
        """Makes the actual API call to Twilio to create a message."""
        body_preview = message_body[:50]
        log_extra_attempt = {
            "body_preview": body_preview,
            "use_test_creds": self.use_test_creds,
            "to_phone_number": to_phone_number,
        }
        firelog.debug(
            f"{current_log_prefix} {TwilioServiceConstants.ATTEMPTING_TO_SEND_SMS_TEMPLATE}",
            extra=log_extra_attempt,
        )

        message = await asyncio.to_thread(
            self.client.messages.create,
            body=message_body,
            from_=self.from_phone_number,
            to=to_phone_number,
        )
        log_extra_result = {
            "to_phone_number": to_phone_number,
            "message_sid": message.sid,
            "message_status": message.status,
        }
        firelog.info(
            f"{current_log_prefix} {TwilioServiceConstants.SEND_SMS_RESULT}",
            extra=log_extra_result,
        )
        return message

    async def _handle_api_exception(
        self, e: Exception, to_phone_number: str, current_log_prefix: str
    ) -> Never:
        """Handles exceptions specifically from the Twilio API call or other unexpected errors."""
        if isinstance(e, TwilioRestException):
            error_code_str = str(e.code)
            log_extra_api_error = {
                "status": e.status,
                "code": e.code,
                "uri": e.uri,
                "twilio_msg": e.msg,
                "to_phone_number": to_phone_number,
            }
            firelog.error(
                f"{current_log_prefix} {TwilioServiceConstants.API_ERROR_TEMPLATE}",
                exc_info=True,
                extra=log_extra_api_error,
            )

            exception_class = TWILIO_ERROR_CODE_MAP.get(
                error_code_str, SMSServiceProviderError
            )
            if e.status == 401:
                exception_class = ConfigurationError

            user_facing_error_detail = e.msg
            raise exception_class(
                user_facing_error_detail,
                provider_error_code=error_code_str,
                to_phone_number=to_phone_number,
            ) from e
        else:
            log_extra_unexpected = {"error": str(e), "to_phone_number": to_phone_number}
            firelog.error(
                f"{current_log_prefix} {TwilioServiceConstants.UNEXPECTED_SENDING_ERROR_TEMPLATE}",
                exc_info=True,
                extra=log_extra_unexpected,
            )
            raise SMSSendingError(
                TwilioServiceConstants.UNEXPECTED_SENDING_ERROR_TEMPLATE
                % log_extra_unexpected,
                to_phone_number=to_phone_number,
            ) from e

    def _process_twilio_message_response(
        self, message: MessageInstance, to_phone_number: str, current_log_prefix: str
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

        log_extra_base_response = {
            "sid": message.sid,
            "status": message.status,
            "error_code": message.error_code,
            "to_phone_number": to_phone_number,
        }

        if message.status in success_statuses:
            if message.error_code:
                return self._handle_success_with_error_code(
                    message, to_phone_number, current_log_prefix
                )
            if message.sid is None:
                log_extra_no_sid = {
                    **log_extra_base_response,
                    "message_status": message.status,
                }
                firelog.error(
                    f"{current_log_prefix} {TwilioServiceConstants.DELIVERED_WITHOUT_SID}",
                    extra=log_extra_no_sid,
                )
                raise SMSServiceProviderError(
                    TwilioServiceConstants.DELIVERED_WITHOUT_SID % log_extra_no_sid,
                    provider_error_code=str(message.error_code),
                    to_phone_number=to_phone_number,
                )
            return message.sid

        elif message.status in failure_statuses:
            firelog.error(
                f"{current_log_prefix} {TwilioServiceConstants.MESSAGE_FAILED_OR_UNDELIVERED}",
                extra=log_extra_base_response,
            )
            self._handle_twilio_error(
                to_phone_number,
                str(message.error_code),
                message.error_message,
                str(message.status),
                current_log_prefix,
            )

        elif message.status == TwilioServiceConstants.STATUS_DELIVERED:
            firelog.info(
                f"{current_log_prefix} {TwilioServiceConstants.MESSAGE_DELIVERED_SYNC_TEMPLATE}",
                extra={
                    "sid": message.sid,
                    "to_phone_number": to_phone_number,
                },
            )
            if message.sid is None:
                log_extra_no_sid_delivered = {
                    **log_extra_base_response,
                    "message_status": message.status,
                }
                firelog.error(
                    f"{current_log_prefix} {TwilioServiceConstants.DELIVERED_WITHOUT_SID}",
                    extra=log_extra_no_sid_delivered,
                )
                raise SMSServiceProviderError(
                    TwilioServiceConstants.DELIVERED_WITHOUT_SID
                    % log_extra_no_sid_delivered,
                    provider_error_code=str(message.error_code),
                    to_phone_number=to_phone_number,
                )
            return message.sid

        else:
            log_extra_unexpected_status = {
                "status": message.status,
                "sid": message.sid,
                "to_phone_number": to_phone_number,
            }
            firelog.warning(
                f"{current_log_prefix} {TwilioServiceConstants.UNEXPECTED_STATUS_TEMPLATE}",
                extra=log_extra_unexpected_status,
            )
            raise SMSServiceProviderError(
                TwilioServiceConstants.UNEXPECTED_STATUS_TEMPLATE
                % log_extra_unexpected_status,
                provider_error_code=str(message.error_code),
                to_phone_number=to_phone_number,
            )
        raise SMSServiceProviderError(
            f"{current_log_prefix} Reached unexpected end of status processing.",
            to_phone_number=to_phone_number,
        )

    def _handle_success_with_error_code(
        self, message: MessageInstance, to_phone_number: str, current_log_prefix: str
    ) -> str:
        """Handles cases where status is success-like but message.error_code is present."""
        log_extra_sim_fail = {
            "status": message.status,
            "error_code": message.error_code,
            "to_phone_number": to_phone_number,
        }
        if self.use_test_creds:
            firelog.warning(
                f"{current_log_prefix} {TwilioServiceConstants.SIMULATED_FAILURE_TEMPLATE}",
                extra=log_extra_sim_fail,
            )
            self._handle_twilio_error(
                to_phone_number,
                str(message.error_code),
                message.error_message,
                str(message.status),
                current_log_prefix,
            )
        else:
            firelog.error(
                f"{current_log_prefix} {TwilioServiceConstants.ERROR_CODE_DESPITE_STATUS_TEMPLATE}",
                extra={
                    "status": message.status,
                    "to_phone_number": to_phone_number,
                },
            )
            self._handle_twilio_error(
                to_phone_number,
                str(message.error_code),
                message.error_message,
                str(message.status),
                current_log_prefix,
            )
        if message.sid is None:
            log_extra_missing_sid = {"to_phone_number": to_phone_number}
            firelog.error(
                f"{current_log_prefix} {TwilioServiceConstants.MISSING_SID_AFTER_SUCCESS_AND_ERROR}",
                extra=log_extra_missing_sid,
            )
            raise SMSServiceProviderError(
                TwilioServiceConstants.MISSING_SID_AFTER_SUCCESS_AND_ERROR,
                to_phone_number=to_phone_number,
            )
        return message.sid

    async def send_sms(self, to_phone_number: str, message_body: str) -> str:
        _current_op_log_prefix = TwilioServiceConstants.SEND_SMS_LOG_PREFIX_TEMPLATE % {
            "to_phone_number": to_phone_number
        }
        log_extra_send_op = {"to_phone_number": to_phone_number}

        if not self.client:
            msg = TwilioServiceConstants.CLIENT_NOT_INITIALIZED
            firelog.error(f"{_current_op_log_prefix} {msg}", extra=log_extra_send_op)
            raise ConfigurationError(msg, to_phone_number=to_phone_number)

        if not self.from_phone_number:
            msg = TwilioServiceConstants.FROM_NUMBER_NOT_CONFIGURED
            firelog.error(f"{_current_op_log_prefix} {msg}", extra=log_extra_send_op)
            raise ConfigurationError(msg, to_phone_number=to_phone_number)

        try:
            message_instance = await self._make_twilio_api_call(
                to_phone_number, message_body, _current_op_log_prefix
            )

            log_extra_attempt_result = {
                "sid": message_instance.sid,
                "status": message_instance.status,
                "error_code": message_instance.error_code,
                "price": message_instance.price,
                "to_phone_number": to_phone_number,
            }
            firelog.info(
                f"{_current_op_log_prefix} {TwilioServiceConstants.MESSAGE_ATTEMPT_RESULT_TEMPLATE}",
                extra=log_extra_attempt_result,
            )

            return self._process_twilio_message_response(
                message_instance, to_phone_number, _current_op_log_prefix
            )

        except Exception as e:
            await self._handle_api_exception(e, to_phone_number, _current_op_log_prefix)
            log_extra_unhandled = {"to_phone_number": to_phone_number, "error": str(e)}
            firelog.critical(
                f"{_current_op_log_prefix} {TwilioServiceConstants.UNHANDLED_EXCEPTION}",
                exc_info=True,
                extra=log_extra_unhandled,
            )
            raise SMSSendingError(
                TwilioServiceConstants.UNHANDLED_EXCEPTION % log_extra_unhandled,
                to_phone_number=to_phone_number,
            ) from e
