from datetime import UTC, datetime, timedelta
import secrets

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.auth.constants import (
    AuthHttpErrorDetails,
    AuthServiceLoggingStrings as LogStr,
    AuthSuccessMessages,
)
from app.auth.constants.logging_strings import AuthServiceLoggingStrings
from app.auth.repositories.pending_otps_repository import PendingOTPRepository
from app.auth.repositories.user_sessions_repository import UserSessionRepository
from app.auth.schemas.otp_schema import OTPData
from app.auth.schemas.token_schema import Token
from app.core import security
from app.core.config import settings
from app.core.constants.security import SecurityConstants
from app.core.dependencies import get_sms_service
from app.core.logging.logger_wrapper import firelog
from app.core.services.interfaces.sms_service_interface import SMSServiceInterface
from app.users.repositories.user_repository import UserRepository


class AuthService:
    _SERVICE_NAME = AuthServiceLoggingStrings._SERVICE_NAME

    def __init__(
        self,
        sms_service: SMSServiceInterface = Depends(get_sms_service),  # noqa: B008
        user_repository: UserRepository = Depends(UserRepository),  # noqa: B008
        otp_repository: PendingOTPRepository = Depends(PendingOTPRepository),  # noqa: B008
        session_repository: UserSessionRepository = Depends(UserSessionRepository),  # noqa: B008
    ) -> None:
        self.sms_service = sms_service
        self._user_repository = user_repository
        self._otp_repository = otp_repository
        self._session_repository = session_repository
        firelog.debug(f"Initialized {self._SERVICE_NAME}.")

    def _generate_otp(self) -> str:
        """Generates a cryptographically secure 6-digit OTP."""
        otp_int = secrets.randbelow(10**6)
        otp = f"{otp_int:06d}"
        firelog.debug(LogStr.OTP_GENERATED.format(otp_suffix=otp[-3:]))
        return otp

    async def send_otp(self, db: Session, phone_number: str) -> dict:
        # JD TODO: Implement Rate Limiting for OTP requests
        # Example: check_rate_limit("otp_request", identifier=phone_number)
        # This would typically involve checking a cache (like Redis) or a DB table.
        # If rate limit exceeded, raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, ...)

        self._otp_repository.invalidate_existing_pending_otps(
            db=db, phone_number=phone_number
        )
        plaintext_otp = self._generate_otp()
        otp_suffix = plaintext_otp[-3:]

        try:
            pending_otp_record = self._otp_repository.create_pending_otp(
                db=db,
                phone_number=phone_number,
                plain_otp=plaintext_otp,
            )
            firelog.info(
                LogStr.OTP_RECORD_CREATED.format(
                    otp_id=pending_otp_record.id, phone_number=phone_number
                )
            )
        except Exception as e:
            firelog.error(
                LogStr.OTP_RECORD_CREATE_FAILED.format(
                    phone_number=phone_number, error=str(e)
                ),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=AuthHttpErrorDetails.OTP_CREATE_RECORD_FAILED,
            ) from e

        if settings.APP_ENV == "dev" and settings.DEBUG_OTP_IN_RESPONSE:
            firelog.info(
                LogStr.OTP_DEV_MODE_RESPONSE.format(
                    phone_number=phone_number, otp_suffix=otp_suffix
                )
            )
            return OTPData(
                message=AuthSuccessMessages.OTP_DEBUG_MODE,
                debug_otp=plaintext_otp,
            ).model_dump(by_alias=True)

        # Production SMS Sending Path
        otp_message = AuthSuccessMessages.OTP_MESSAGE.format(otp_code=plaintext_otp)
        try:
            firelog.debug(
                LogStr.OTP_SENDING_VIA_SMS.format(
                    phone_number=phone_number, otp_id=pending_otp_record.id
                )
            )
            sms_sent_successfully = await self.sms_service.send_sms(
                to_phone_number=phone_number, message_body=otp_message
            )
        except Exception as e:
            firelog.error(
                LogStr.OTP_SMS_SERVICE_ERROR.format(
                    phone_number=phone_number,
                    otp_id=pending_otp_record.id,
                    error=str(e),
                ),
                exc_info=True,
            )
            self._otp_repository.set_otp_sending_error(
                db=db, otp_id=pending_otp_record.id
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=AuthHttpErrorDetails.SMS_SERVICE_UNAVAILABLE,
            ) from e

        if not sms_sent_successfully:
            firelog.error(
                LogStr.OTP_SMS_SEND_FAILED.format(
                    phone_number=phone_number, otp_id=pending_otp_record.id
                )
            )
            self._otp_repository.set_otp_sending_error(
                db=db, otp_id=pending_otp_record.id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=AuthHttpErrorDetails.OTP_SMS_SEND_FAILED,
            )

        firelog.info(
            LogStr.OTP_SENT_SUCCESSFULLY.format(
                phone_number=phone_number, otp_id=pending_otp_record.id
            )
        )

        return OTPData(message=AuthSuccessMessages.OTP_SENT_SUCCESSFULLY).model_dump(
            by_alias=True
        )

    async def verify_otp_and_grant_access(
        self,
        db: Session,
        phone_number: str,
        otp_code: str,
        user_agent: str | None,
        ip_address: str | None,
    ) -> Token:
        otp_suffix = otp_code[-3:]  # For logging
        firelog.info(
            LogStr.OTP_VERIFY_REQUEST.format(
                phone_number=phone_number, otp_suffix=otp_suffix
            )
        )

        # 1. Verify and consume the OTP
        success, otp_record, message = self._otp_repository.verify_and_consume_otp(
            db=db, phone_number=phone_number, submitted_otp=otp_code
        )

        if not success or not otp_record:
            firelog.warning(
                LogStr.OTP_VERIFY_FAILED_REASON.format(
                    phone_number=phone_number, otp_suffix=otp_suffix, reason=message
                )
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message or AuthHttpErrorDetails.OTP_VERIFICATION_FAILED,
            )
        firelog.info(
            LogStr.OTP_VERIFIED_SUCCESS.format(
                phone_number=phone_number, otp_id=otp_record.id
            )
        )

        # 2. Get or Create User
        user = self._user_repository.get_by_phone_number(
            db=db, phone_number=phone_number
        )
        is_new_user = False

        if not user:
            firelog.info(
                LogStr.USER_NOT_FOUND_CREATING.format(phone_number=phone_number)
            )
            user = self._user_repository.create_user_for_otp_flow(
                db=db, phone_number=phone_number
            )
            if not user:
                firelog.critical(
                    LogStr.USER_CREATE_FAILED_CRITICAL.format(phone_number=phone_number)
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=AuthHttpErrorDetails.USER_CREATE_FAILED,
                )
            is_new_user = True
            firelog.info(
                LogStr.USER_CREATED_SUCCESS.format(
                    user_id=user.id, phone_number=phone_number
                )
            )
        else:
            if not user.is_active:
                firelog.warning(
                    LogStr.USER_INACTIVE_LOGIN_ATTEMPT.format(user_id=user.id)
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=AuthHttpErrorDetails.USER_INACTIVE,
                )
            self._user_repository.update_last_login_at(db=db, user_to_update=user)
            firelog.info(LogStr.USER_EXISTING_LOGIN.format(user_id=user.id))

        # 3. Create Access and Refresh Tokens (security module calls are fine)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token, refresh_jti = security.create_refresh_token_with_jti(
            subject=str(user.id), expires_delta=refresh_token_expires
        )
        firelog.debug(
            LogStr.TOKENS_CREATED.format(
                user_id=user.id, refresh_jti_suffix=refresh_jti[-6:]
            )
        )

        # 4. Create User Session
        session_expires_at = datetime.now(UTC) + refresh_token_expires
        self._session_repository.create_user_session(
            db=db,
            user_id=user.id,
            refresh_token_jti=refresh_jti,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=session_expires_at,
        )
        firelog.info(
            LogStr.USER_SESSION_CREATED.format(
                user_id=user.id, refresh_jti_suffix=refresh_jti[-6:]
            )
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",  # noqa: S106
            is_new_user=is_new_user,
        )

    async def refresh_access_token(
        self,
        db: Session,
        refresh_token_str: str,
        user_agent: str | None,
        ip_address: str | None,
    ) -> Token:
        jti_from_token_str = "unknown"  # noqa: S105
        try:
            payload = jwt.decode(
                refresh_token_str,
                settings.REFRESH_TOKEN_SECRET_KEY,
                algorithms=[SecurityConstants.JWT_ALGORITHM],
                options={"verify_exp": True},  # Ensure expiry is checked
            )
            user_id_from_payload_str: str | None = payload.get("sub")
            jti_from_token_str: str | None = payload.get("jti")

            if user_id_from_payload_str is None or jti_from_token_str is None:
                firelog.warning(
                    LogStr.REFRESH_TOKEN_INVALID_PAYLOAD.format(
                        reason="Missing sub or jti",
                        token_jti_suffix=jti_from_token_str[-6:]
                        if jti_from_token_str
                        else "N/A",
                    )
                )
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail=AuthHttpErrorDetails.REFRESH_TOKEN_INVALID,
                )
            user_id = int(user_id_from_payload_str)
            jti_suffix = jti_from_token_str[-6:]
            firelog.info(
                LogStr.REFRESH_TOKEN_REQUEST.format(
                    user_id=user_id, token_jti_suffix=jti_suffix
                )
            )

        except JWTError as e:
            log_jti_suffix = "N/A"
            if jti_from_token_str and jti_from_token_str != "unknown":  # noqa: S105
                log_jti_suffix = jti_from_token_str[-6:]

            firelog.warning(
                LogStr.REFRESH_TOKEN_JWT_ERROR.format(
                    error=str(e),
                    token_jti_suffix=log_jti_suffix,
                )
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail=AuthHttpErrorDetails.REFRESH_TOKEN_INVALID_OR_EXPIRED,
            ) from e
        except ValueError as e:
            firelog.warning(
                LogStr.REFRESH_TOKEN_INVALID_PAYLOAD.format(
                    reason="Invalid user ID format in sub", token_jti_suffix=jti_suffix
                )
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail=AuthHttpErrorDetails.REFRESH_TOKEN_INVALID,
            ) from e

        user_session = self._session_repository.get_active_session_by_jti_and_user(
            db=db, user_id=user_id, refresh_token_jti=jti_from_token_str
        )

        if not user_session:
            firelog.warning(
                LogStr.REFRESH_TOKEN_NO_ACTIVE_SESSION.format(
                    user_id=user_id, token_jti_suffix=jti_suffix
                )
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail=AuthHttpErrorDetails.SESSION_NOT_FOUND_OR_REVOKED,
            )

        user = self._user_repository.get(db=db, id=user_session.user_id)
        if not user or not user.is_active:
            firelog.warning(
                LogStr.REFRESH_TOKEN_USER_INACTIVE_OR_NOT_FOUND.format(
                    user_id=user_id, token_jti_suffix=jti_suffix
                )
            )
            self._session_repository.invalidate_session(
                db=db, session_to_invalidate=user_session
            )  # Invalidate the stale session
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail=AuthHttpErrorDetails.USER_INACTIVE_OR_NOT_FOUND,
            )

        # Generate new access token
        new_access_token = security.create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        firelog.debug(LogStr.REFRESH_NEW_ACCESS_TOKEN_CREATED.format(user_id=user.id))

        if settings.ROTATE_REFRESH_TOKENS:
            firelog.info(
                LogStr.REFRESH_TOKEN_ROTATING.format(
                    user_id=user.id, old_token_jti_suffix=jti_suffix
                )
            )
            self._session_repository.invalidate_session(
                db=db, session_to_invalidate=user_session
            )

            new_refresh_token, new_jti = security.create_refresh_token_with_jti(
                subject=user.id,
                expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            )
            new_session_expires_at = datetime.now(UTC) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

            self._session_repository.create_user_session(
                db=db,
                user_id=user.id,
                refresh_token_jti=new_jti,
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=new_session_expires_at,
            )
            firelog.info(
                LogStr.REFRESH_TOKEN_ROTATION_COMPLETE.format(
                    user_id=user.id, new_token_jti_suffix=new_jti[-6:]
                )
            )
            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                is_new_user=not user.is_profile_complete,
            )
        else:
            firelog.info(
                LogStr.REFRESH_TOKEN_NO_ROTATION.format(
                    user_id=user.id, token_jti_suffix=jti_suffix
                )
            )
            return Token(
                access_token=new_access_token,
                refresh_token=refresh_token_str,  # Return original refresh token
                is_new_user=not user.is_profile_complete,
            )

    async def logout_user(
        self,
        db: Session,
        current_user_id: int,
        refresh_token_to_invalidate: str,
    ) -> None:
        token_jti_suffix = "unknown_jti"  # noqa: S105
        user_id_from_logout_token_str = "unknown_user"  # noqa: S105

        try:
            payload = jwt.decode(
                refresh_token_to_invalidate,
                settings.REFRESH_TOKEN_SECRET_KEY,
                algorithms=[SecurityConstants.JWT_ALGORITHM],
                options={"verify_exp": False},
            )
            jti_from_token: str | None = payload.get("jti")
            user_id_from_logout_token_str: str | None = payload.get("sub")

            if not jti_from_token or not user_id_from_logout_token_str:
                firelog.warning(
                    LogStr.LOGOUT_MALFORMED_TOKEN.format(
                        requesting_user_id=current_user_id,
                        token_jti=jti_from_token,
                        token_sub=user_id_from_logout_token_str,
                    )
                )
                return  # Silently succeed

            token_jti_suffix = jti_from_token[-6:]
            user_id_from_logout_token = int(user_id_from_logout_token_str)

            # Security check: Ensure the refresh token belongs to the currently authenticated user
            if current_user_id != user_id_from_logout_token:
                firelog.error(
                    LogStr.LOGOUT_ATTEMPT_FOR_OTHER_USER.format(
                        requesting_user_id=current_user_id,
                        target_user_id=user_id_from_logout_token,
                        token_jti_suffix=token_jti_suffix,
                    )
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=AuthHttpErrorDetails.LOGOUT_FORBIDDEN_OTHER_USER,
                )

        except JWTError as e:
            firelog.warning(
                LogStr.LOGOUT_INVALID_EXPIRED_TOKEN.format(
                    requesting_user_id=current_user_id,
                    error=str(e),
                    token_jti_suffix=token_jti_suffix,
                )
            )
            return  # Silently succeed
        except ValueError:
            firelog.warning(
                LogStr.LOGOUT_MALFORMED_TOKEN.format(
                    requesting_user_id=current_user_id,
                    token_jti=token_jti_suffix,
                    token_sub=user_id_from_logout_token_str,
                )
            )
            return  # Silently succeed

        # At this point, jti_from_token and user_id_from_logout_token are considered valid from the token's perspective
        firelog.info(
            LogStr.LOGOUT_REQUEST.format(
                user_id=user_id_from_logout_token, token_jti_suffix=token_jti_suffix
            )
        )
        invalidated_session = self._session_repository.invalidate_session_by_jti(
            db=db, refresh_token_jti=jti_from_token
        )

        if invalidated_session:
            if invalidated_session.user_id != user_id_from_logout_token:
                firelog.critical(
                    LogStr.LOGOUT_JTI_USER_MISMATCH_ALERT.format(
                        session_user_id=invalidated_session.user_id,
                        token_user_id=user_id_from_logout_token,
                        token_jti_suffix=token_jti_suffix,
                    )
                )
            else:
                firelog.info(
                    LogStr.LOGOUT_SESSION_INVALIDATED.format(
                        user_id=user_id_from_logout_token,
                        token_jti_suffix=token_jti_suffix,
                    )
                )
        else:
            firelog.info(
                LogStr.LOGOUT_NO_ACTIVE_SESSION_FOR_JTI.format(
                    user_id=user_id_from_logout_token, token_jti_suffix=token_jti_suffix
                )
            )

        return
