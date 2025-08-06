from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.services.interfaces.sms_service_interface import SMSServiceInterface
from app.core.services.providers.twilio_sms_service import TwilioSMSService


# --- SMS Service Dependency ---
@lru_cache
def get_twilio_sms_service_instance() -> TwilioSMSService:
    """Cached factory for TwilioSMSService instance."""
    return TwilioSMSService()


def get_sms_service(
    sms_service_impl: SMSServiceInterface = Depends(get_twilio_sms_service_instance),  # noqa: B008
) -> SMSServiceInterface:
    """Provides an instance of an SMSServiceInterface implementation."""
    return sms_service_impl


CurrentSMSService = Annotated[SMSServiceInterface, Depends(get_sms_service)]
