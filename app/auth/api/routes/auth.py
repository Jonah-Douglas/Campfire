from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.constants import (
    AuthEndpoints,
    AuthHttpErrorDetails,
    AuthLoggingStrings,
    AuthSuccessMessages,
)
from app.auth.dependencies import get_current_user
from app.auth.schemas.otp_schema import OTPData
from app.auth.schemas.pending_otp_schema import OTPRequestPayload, OTPVerifyPayload
from app.auth.schemas.token_schema import RefreshTokenRequest, Token
from app.auth.services.auth_service import AuthService
from app.core.logging.logger_wrapper import firelog
from app.core.schemas.response_schemas import GenericAPIResponse
from app.db.session import SessionDependency
from app.users.models.user_model import User

router = APIRouter()


# JD TODO: Consider implementing a refresh token deny list for enhanced security,
# allowing immediate invalidation of specific refresh tokens before their natural expiry,
# especially useful if token rotation is implemented or a token is suspected compromised.
@router.post(
    AuthEndpoints.REQUEST_OTP,
    summary="Request an OTP for phone number verification.",
    response_description="OTP sent successfully or error message.",
    response_model=GenericAPIResponse[OTPData],
    status_code=status.HTTP_200_OK,
)
async def request_otp(
    payload: OTPRequestPayload,
    session: SessionDependency,
    auth_service: AuthService = Depends(AuthService),  # noqa: B008
) -> GenericAPIResponse[OTPData]:
    """
    Initiates the One-Time Password (OTP) verification process.

    An OTP will be generated and sent to the provided phone number if the SMS service
    is operational and the phone number is in a valid format. This is typically the
    first step in user registration or phone-based login.
    """
    phone_prefix = payload.phone_number[:7] if payload.phone_number else "N/A"
    log_extra = {"endpoint": AuthEndpoints.REQUEST_OTP, "phone_prefix": phone_prefix}

    firelog.info(AuthLoggingStrings.OTP_REQUEST_INITIATED, extra=log_extra)

    if not auth_service.sms_service:
        firelog.warning(AuthLoggingStrings.OTP_SMS_SERVICE_UNAVAILABLE, extra=log_extra)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=AuthHttpErrorDetails.SMS_SERVICE_UNAVAILABLE,
        )

    phone_number = payload.phone_number

    try:
        service_outcome = await auth_service.send_otp(
            db=session, phone_number=phone_number
        )

        debug_otp_value = None
        otp_data_specific_message = AuthSuccessMessages.OTP_SENT_SUCCESSFULLY
        api_response_general_message = AuthSuccessMessages.OTP_PROCESSED_SUCCESSFULLY

        if isinstance(service_outcome, dict) and "debug_otp_value" in service_outcome:
            debug_otp_value = service_outcome["debug_otp_value"]
            otp_data_specific_message = AuthSuccessMessages.OTP_DEBUG_MODE
            api_response_general_message = AuthSuccessMessages.OTP_PROCESSED_DEV_MODE
            firelog.debug(AuthLoggingStrings.OTP_SENT_IN_DEV_MODE, extra=log_extra)
        else:
            firelog.info(AuthLoggingStrings.OTP_SENT_IN_PRODUCTION, extra=log_extra)

        otp_data_payload = OTPData(
            message=otp_data_specific_message, debug_otp=debug_otp_value
        )
        return GenericAPIResponse.success_response(
            data_payload=otp_data_payload, msg=api_response_general_message
        )
    except HTTPException:
        firelog.warning(AuthLoggingStrings.OTP_HTTP_ERROR, extra=log_extra)
        raise
    except Exception as e:
        firelog.error(
            AuthLoggingStrings.OTP_UNHANDLED_ERROR, exc_info=True, extra=log_extra
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthHttpErrorDetails.GENERIC_INTERNAL_ERROR,
        ) from e


@router.post(
    AuthEndpoints.VERIFY_OTP,
    summary="Verify OTP for login or new user registration.",
    response_description="Access and refresh tokens upon successful OTP verification.",
    response_model=GenericAPIResponse[Token],
)
async def verify_otp(
    payload: OTPVerifyPayload,
    request: Request,
    session: SessionDependency,
    auth_service: AuthService = Depends(AuthService),  # noqa: B008
) -> GenericAPIResponse[Token]:
    """
    Verifies a One-Time Password (OTP) submitted by the user.

    - If the OTP is valid for the given phone number:
        - And the user already exists: they are logged in.
        - And the user does not exist: a new user account is created and they are logged in.
    - Upon successful verification and login/registration, new access and refresh tokens
      are issued.
    - The client application should store these tokens securely.
    """
    phone_prefix = payload.phone_number[:7] if payload.phone_number else "N/A"
    client_host = request.client.host if request.client else "Unknown"
    user_agent = request.headers.get("user-agent")
    log_extra = {"endpoint": AuthEndpoints.VERIFY_OTP, "phone_prefix": phone_prefix}

    firelog.info(AuthLoggingStrings.OTP_VERIFICATION_ATTEMPT, extra=log_extra)

    try:
        token_data = await auth_service.verify_otp_and_grant_access(
            db=session,
            phone_number=payload.phone_number,
            otp_code=payload.otp_code,
            user_agent=user_agent,
            ip_address=client_host,
        )

        firelog.info(AuthLoggingStrings.OTP_SUCCESSFULLY_VERIFIED, extra=log_extra)
        return GenericAPIResponse.success_response(
            data_payload=token_data, msg=AuthSuccessMessages.OTP_VERIFIED_SUCCESS
        )
    except HTTPException:
        firelog.warning(AuthLoggingStrings.OTP_FAILED_VERIFICATION, extra=log_extra)
        raise
    except Exception as e:
        firelog.error(
            AuthLoggingStrings.OTP_UNHANDLED_ERROR, exc_info=True, extra=log_extra
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthLoggingStrings.OTP_UNEXPECTED_ERROR,
        ) from e


@router.post(
    AuthEndpoints.REFRESH_TOKEN,
    summary="Obtain a new access token using a refresh token.",
    response_description="A new set of access and refresh tokens.",
    response_model=GenericAPIResponse[Token],
)
async def refresh_access_token(
    refresh_token_body: RefreshTokenRequest,
    request: Request,
    session: SessionDependency,
    auth_service: AuthService = Depends(AuthService),  # noqa: B008
) -> GenericAPIResponse[Token]:
    """
    Exchanges a valid refresh token for a new access token (and potentially a new refresh token).

    This allows clients to maintain an active session without requiring the user
    to re-authenticate with their primary credentials (e.g., OTP) frequently.
    The client must securely store and manage the refresh token.
    """
    client_host = request.client.host if request.client else "Unknown"
    user_agent = request.headers.get("user-agent")
    log_extra = {"endpoint": AuthEndpoints.REFRESH_TOKEN, "client_host": client_host}

    firelog.info(AuthLoggingStrings.TOKEN_REFRESH_ATTEMPT, extra=log_extra)

    new_tokens = await auth_service.refresh_access_token(
        db=session,
        refresh_token_str=refresh_token_body.refresh_token,
        user_agent=user_agent,
        ip_address=client_host,
    )

    if not new_tokens:
        firelog.warning(AuthLoggingStrings.TOKEN_REFRESH_FAILED, extra=log_extra)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthHttpErrorDetails.REFRESH_TOKEN_INVALID_OR_EXPIRED,
        )

    firelog.info(AuthLoggingStrings.TOKEN_SUCCESSFULLY_REFRESHED, extra=log_extra)
    return GenericAPIResponse.success_response(
        data_payload=new_tokens, msg=AuthSuccessMessages.TOKENS_REFRESHED_SUCCESS
    )


@router.post(
    AuthEndpoints.LOGOUT,
    summary="Log out the current user and invalidate their refresh token.",
    response_description="No content is returned on successful logout.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    *,
    auth_service: AuthService = Depends(AuthService),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
    refresh_token: RefreshTokenRequest,
    session: SessionDependency,
) -> None:
    """
    Logs out the authenticated user by invalidating their specified refresh token.

    This makes the provided refresh token unusable for obtaining new access tokens.
    The client application is responsible for discarding both the access and refresh
    tokens locally upon successful logout. This endpoint requires authentication.
    """
    log_extra = {"endpoint": AuthEndpoints.LOGOUT, "user_id": current_user.id}

    firelog.info(AuthLoggingStrings.LOGOUT_ATTEMPT, extra=log_extra)
    try:
        await auth_service.logout_user(
            db=session,
            current_user_id=current_user.id,
            refresh_token_to_invalidate=refresh_token.refresh_token,
        )
        firelog.info(
            AuthLoggingStrings.LOGOUT_SUCCESS,
            extra={"endpoint": AuthEndpoints.LOGOUT, "user_id": current_user.id},
        )
    except HTTPException:
        firelog.warning(AuthLoggingStrings.LOGOUT_HTTP_ERROR, extra=log_extra)
        raise
    except Exception as e:
        firelog.error(
            AuthLoggingStrings.LOGOUT_UNHANDLED_ERROR, exc_info=True, extra=log_extra
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthHttpErrorDetails.GENERIC_INTERNAL_ERROR,
        ) from e
    return
