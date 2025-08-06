from pydantic import BaseModel, Field


class OTPData(BaseModel):
    otp_specific_message: str | None = Field(default=None, alias="message")
    debug_otp: str | None = None

    model_config = {"populate_by_name": True}
