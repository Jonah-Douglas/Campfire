from datetime import UTC, datetime, timedelta
import secrets

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.auth.constants import (
    AuthHttpErrorDetails,
    AuthServiceLoggingStrings as LogStr,
    AuthSuccessMessages,
)
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
from app.users.models.user_model import User
from app.users.repositories.user_repository import UserRepository


class AuthService:
    _SERVICE_NAME = LogStr._SERVICE_NAME

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
        log_extra = {"otp_suffix": otp[-3:]}
        firelog.debug(LogStr.OTP_GENERATED, extra=log_extra)
        return otp

    async def send_otp(self, db: Session, phone_number: str) -> dict:
        self._otp_repository.invalidate_existing_pending_otps(
            db=db, phone_number=phone_number
        )
        plaintext_otp = self._generate_otp()

        try:
            pending_otp_record = self._otp_repository.create_pending_otp(
                db=db,
                phone_number=phone_number,
                plain_otp=plaintext_otp,
            )
            log_extra_created = {
                "otp_id": pending_otp_record.id,
                "phone_number": phone_number,
            }
            firelog.info(LogStr.OTP_RECORD_CREATED, extra=log_extra_created)
        except Exception as e:
            log_extra_create_failed = {
                "phone_number": phone_number,
                "error": str(e),
            }
            firelog.error(
                LogStr.OTP_RECORD_CREATE_FAILED,
                exc_info=e,
                extra=log_extra_create_failed,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=AuthHttpErrorDetails.OTP_CREATE_RECORD_FAILED,
            ) from e

        if settings.APP_ENV.value == "dev" and settings.DEBUG_OTP_IN_RESPONSE:
            log_extra_dev_mode = {
                "phone_number": phone_number,
                "otp": plaintext_otp,
            }
            firelog.debug(LogStr.OTP_DEV_MODE_RESPONSE, extra=log_extra_dev_mode)
            return OTPData(
                message=AuthSuccessMessages.OTP_DEBUG_MODE,
                debug_otp=plaintext_otp,
            ).model_dump(by_alias=True)

        otp_message = AuthSuccessMessages.OTP_MESSAGE % {"otp_code": plaintext_otp}
        log_extra_sms_common = {
            "phone_number": phone_number,
            "otp_id": pending_otp_record.id,
        }
        try:
            firelog.debug(LogStr.OTP_SENDING_VIA_SMS, extra=log_extra_sms_common)
            sms_sent_successfully = await self.sms_service.send_sms(
                to_phone_number=phone_number, message_body=otp_message
            )
        except Exception as e:
            log_extra_sms_error = {
                **log_extra_sms_common,
                "error": str(e),
            }
            firelog.error(
                LogStr.OTP_SMS_SERVICE_ERROR,
                exc_info=e,
                extra=log_extra_sms_error,
            )
            self._otp_repository.set_otp_sending_error(
                db=db, otp_id=pending_otp_record.id
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=AuthHttpErrorDetails.SMS_SERVICE_UNAVAILABLE,
            ) from e

        if not sms_sent_successfully:
            firelog.error(LogStr.OTP_SMS_SEND_FAILED, extra=log_extra_sms_common)
            self._otp_repository.set_otp_sending_error(
                db=db, otp_id=pending_otp_record.id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=AuthHttpErrorDetails.OTP_SMS_SEND_FAILED,
            )

        firelog.info(LogStr.OTP_SENT_SUCCESSFULLY, extra=log_extra_sms_common)

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
        otp_suffix = otp_code[-3:]
        log_extra_verify_request = {
            "phone_number": phone_number,
            "otp_suffix": otp_suffix,
        }
        firelog.info(LogStr.OTP_VERIFY_REQUEST, extra=log_extra_verify_request)

        success, otp_record, message = self._otp_repository.verify_and_consume_otp(
            db=db, phone_number=phone_number, submitted_otp=otp_code
        )

        if not success or not otp_record:
            log_extra_verify_failed = {
                **log_extra_verify_request,
                "reason": message,
            }
            firelog.warning(
                LogStr.OTP_VERIFY_FAILED_REASON, extra=log_extra_verify_failed
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message or AuthHttpErrorDetails.OTP_VERIFICATION_FAILED,
            )

        log_extra_verified_success = {
            "phone_number": phone_number,
            "otp_id": otp_record.id,
        }
        firelog.info(LogStr.OTP_VERIFIED_SUCCESS, extra=log_extra_verified_success)

        user: User | None = None
        is_new_user = False
        log_extra_user_phone = {"phone_number": phone_number}

        try:
            user = self._user_repository.get_by_phone_number(
                db=db, phone_number=phone_number
            )
        except NoResultFound:
            firelog.debug(LogStr.USER_NOT_FOUND_CREATING, extra=log_extra_user_phone)
            # User does not exist, proceed to create
            pass

        if not user:
            firelog.info(LogStr.USER_NOT_FOUND_CREATING, extra=log_extra_user_phone)
            user = self._user_repository.create_user_for_otp_flow(
                db=db, phone_number=phone_number
            )
            if not user:
                firelog.critical(
                    LogStr.USER_CREATE_FAILED_CRITICAL, extra=log_extra_user_phone
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=AuthHttpErrorDetails.USER_CREATE_FAILED,
                )
            is_new_user = True
            log_extra_user_created = {
                **log_extra_user_phone,
                "user_id": user.id,
            }
            firelog.info(LogStr.USER_CREATED_SUCCESS, extra=log_extra_user_created)
        else:
            log_extra_user_id_only = {"user_id": user.id}
            if not user.is_active:
                firelog.warning(
                    LogStr.USER_INACTIVE_LOGIN_ATTEMPT, extra=log_extra_user_id_only
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=AuthHttpErrorDetails.USER_INACTIVE,
                )
            self._user_repository.update_last_login_at(db=db, user_to_update=user)
            firelog.info(LogStr.USER_EXISTING_LOGIN, extra=log_extra_user_id_only)

        if not user:
            firelog.error(
                LogStr.USER_UNEXPECTED_NONE,
                extra=log_extra_user_phone,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=AuthHttpErrorDetails.UNEXPECTED_ERROR,
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token, refresh_jti = security.create_refresh_token_with_jti(
            subject=str(user.id), expires_delta=refresh_token_expires
        )
        log_extra_tokens = {
            "user_id": user.id,
            "refresh_jti_suffix": refresh_jti[-6:],
        }
        firelog.debug(LogStr.TOKENS_CREATED, extra=log_extra_tokens)

        session_expires_at = datetime.now(UTC) + refresh_token_expires
        self._session_repository.create_user_session(
            db=db,
            user_id=user.id,
            refresh_token_jti=refresh_jti,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=session_expires_at,
        )
        # log_extra_tokens can be reused as it has user_id and refresh_jti_suffix
        firelog.info(LogStr.USER_SESSION_CREATED, extra=log_extra_tokens)

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
        jti_from_token_str_for_logs = "unknown_jti"  # noqa: S105
        user_id = -1  # Default for logging if parsing fails early

        try:
            payload = jwt.decode(
                refresh_token_str,
                settings.REFRESH_TOKEN_SECRET_KEY,
                algorithms=[SecurityConstants.JWT_ALGORITHM],
                options={"verify_exp": True},
            )
            user_id_from_payload_str: str | None = payload.get("sub")
            jti_from_token_str: str | None = payload.get("jti")

            if user_id_from_payload_str is None or jti_from_token_str is None:
                jti_suffix_for_log = (
                    jti_from_token_str[-6:] if jti_from_token_str else "N/A"
                )
                log_extra_invalid_payload = {
                    "reason": "Missing sub or jti",
                    "token_jti_suffix": jti_suffix_for_log,
                }
                firelog.warning(
                    LogStr.REFRESH_TOKEN_INVALID_PAYLOAD,
                    extra=log_extra_invalid_payload,
                )
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail=AuthHttpErrorDetails.REFRESH_TOKEN_INVALID,
                )
            user_id = int(user_id_from_payload_str)  # Now user_id is set
            jti_from_token_str_for_logs = jti_from_token_str
            jti_suffix = jti_from_token_str[-6:]

            log_extra_refresh_request = {
                "user_id": user_id,
                "token_jti_suffix": jti_suffix,
            }
            firelog.info(LogStr.REFRESH_TOKEN_REQUEST, extra=log_extra_refresh_request)

        except JWTError as e:
            log_jti_suffix_jwt_err = (
                jti_from_token_str_for_logs[-6:]
                if jti_from_token_str_for_logs != "unknown_jti"  # noqa: S105
                else "N/A"
            )
            log_extra_jwt_error = {
                "error": str(e),
                "token_jti_suffix": log_jti_suffix_jwt_err,
            }
            firelog.warning(LogStr.REFRESH_TOKEN_JWT_ERROR, extra=log_extra_jwt_error)
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail=AuthHttpErrorDetails.REFRESH_TOKEN_INVALID_OR_EXPIRED,
            ) from e
        except ValueError as e:  # Catch if int(user_id_from_payload_str) fails
            log_jti_suffix_val_err = (
                jti_from_token_str_for_logs[-6:]
                if jti_from_token_str_for_logs != "unknown_jti"  # noqa: S105
                else "N/A"
            )
            log_extra_val_error = {
                "reason": "Invalid user ID format in sub",
                "token_jti_suffix": log_jti_suffix_val_err,
            }
            firelog.warning(
                LogStr.REFRESH_TOKEN_INVALID_PAYLOAD, extra=log_extra_val_error
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail=AuthHttpErrorDetails.REFRESH_TOKEN_INVALID,
            ) from e

        # From here, user_id and jti_suffix (from log_extra_refresh_request) are valid
        common_refresh_log_extra = log_extra_refresh_request

        user_session = self._session_repository.get_active_session_by_jti_and_user(
            db=db,
            user_id=user_id,
            refresh_token_jti=jti_from_token_str_for_logs,  # Use the full JTI
        )

        if not user_session:
            firelog.warning(
                LogStr.REFRESH_TOKEN_NO_ACTIVE_SESSION, extra=common_refresh_log_extra
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail=AuthHttpErrorDetails.SESSION_NOT_FOUND_OR_REVOKED,
            )

        user_from_db = self._user_repository.get(db=db, id=user_session.user_id)
        if not user_from_db or not user_from_db.is_active:
            firelog.warning(
                LogStr.REFRESH_TOKEN_USER_INACTIVE_OR_NOT_FOUND,
                extra=common_refresh_log_extra,
            )
            self._session_repository.invalidate_session(
                db=db, session_to_invalidate=user_session
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail=AuthHttpErrorDetails.USER_INACTIVE_OR_NOT_FOUND,
            )

        new_access_token = security.create_access_token(
            subject=str(user_from_db.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        firelog.debug(
            LogStr.REFRESH_NEW_ACCESS_TOKEN_CREATED,
            extra={"user_id": user_from_db.id},
        )

        if settings.ROTATE_REFRESH_TOKENS:
            log_extra_rotating = {
                "user_id": user_from_db.id,
                "old_token_jti_suffix": common_refresh_log_extra["token_jti_suffix"],
            }
            firelog.info(LogStr.REFRESH_TOKEN_ROTATING, extra=log_extra_rotating)
            self._session_repository.invalidate_session(
                db=db, session_to_invalidate=user_session
            )

            new_refresh_token, new_jti = security.create_refresh_token_with_jti(
                subject=str(user_from_db.id),
                expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            )
            new_session_expires_at = datetime.now(UTC) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

            self._session_repository.create_user_session(
                db=db,
                user_id=user_from_db.id,
                refresh_token_jti=new_jti,
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=new_session_expires_at,
            )
            log_extra_rotation_complete = {
                "user_id": user_from_db.id,
                "new_token_jti_suffix": new_jti[-6:],
            }
            firelog.info(
                LogStr.REFRESH_TOKEN_ROTATION_COMPLETE,
                extra=log_extra_rotation_complete,
            )
            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                is_new_user=not user_from_db.is_profile_complete,
            )
        else:
            firelog.info(
                LogStr.REFRESH_TOKEN_NO_ROTATION, extra=common_refresh_log_extra
            )
            return Token(
                access_token=new_access_token,
                refresh_token=refresh_token_str,
                is_new_user=not user_from_db.is_profile_complete,
            )

    async def logout_user(
        self,
        db: Session,
        current_user_id: int,  # This is the user ID from the access token
        refresh_token_to_invalidate: str,
    ) -> None:
        # Defaults for logging in case of early JWTError or malformed token
        log_token_jti_suffix = "unknown_jti"  # noqa: S105
        log_token_sub = "unknown_sub"  # noqa: S105

        try:
            payload = jwt.decode(
                refresh_token_to_invalidate,
                settings.REFRESH_TOKEN_SECRET_KEY,
                algorithms=[SecurityConstants.JWT_ALGORITHM],
                options={
                    "verify_exp": False
                },  # Expiry check is not critical for logout invalidation
            )
            jti_from_token: str | None = payload.get("jti")
            user_id_from_logout_token_str: str | None = payload.get("sub")

            # Update log defaults now that we have payload
            log_token_jti_suffix = jti_from_token[-6:] if jti_from_token else "N/A_JTI"
            log_token_sub = (
                user_id_from_logout_token_str
                if user_id_from_logout_token_str
                else "N/A_SUB"
            )

            if not jti_from_token or not user_id_from_logout_token_str:
                log_extra_malformed = {
                    "requesting_user_id": current_user_id,
                    "token_jti": jti_from_token,
                    "token_sub": user_id_from_logout_token_str,
                }
                firelog.warning(
                    LogStr.LOGOUT_MALFORMED_TOKEN, extra=log_extra_malformed
                )
                return

            user_id_from_logout_token = int(user_id_from_logout_token_str)

            if current_user_id != user_id_from_logout_token:
                log_extra_other_user = {
                    "requesting_user_id": current_user_id,
                    "target_user_id": user_id_from_logout_token,
                    "token_jti_suffix": log_token_jti_suffix,
                }
                firelog.error(
                    LogStr.LOGOUT_ATTEMPT_FOR_OTHER_USER, extra=log_extra_other_user
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=AuthHttpErrorDetails.LOGOUT_FORBIDDEN_OTHER_USER,
                )

        except JWTError as e:
            log_extra_jwt_error = {
                "requesting_user_id": current_user_id,
                "error": str(e),
                "token_jti_suffix": log_token_jti_suffix,
            }
            firelog.warning(
                LogStr.LOGOUT_INVALID_EXPIRED_TOKEN, extra=log_extra_jwt_error
            )
            return
        except ValueError:  # If int(user_id_from_logout_token_str) fails
            log_extra_val_error = {
                "requesting_user_id": current_user_id,
                "token_jti": log_token_jti_suffix,
                "token_sub": log_token_sub,
            }
            firelog.warning(LogStr.LOGOUT_MALFORMED_TOKEN, extra=log_extra_val_error)
            return

        # At this point, jti_from_token and user_id_from_logout_token are from a validly structured token
        # And user_id_from_logout_token matches current_user_id
        log_extra_logout_request = {
            "user_id": user_id_from_logout_token,
            "token_jti_suffix": log_token_jti_suffix,
        }
        firelog.info(LogStr.LOGOUT_REQUEST, extra=log_extra_logout_request)

        # Use the full JTI from the token for invalidation
        invalidated_session = self._session_repository.invalidate_session_by_jti(
            db=db, refresh_token_jti=jti_from_token
        )

        if invalidated_session:
            # This critical check is important
            if invalidated_session.user_id != user_id_from_logout_token:
                log_extra_mismatch = {
                    "session_user_id": invalidated_session.user_id,
                    "token_user_id": user_id_from_logout_token,
                    "token_jti_suffix": log_token_jti_suffix,
                }
                firelog.critical(
                    LogStr.LOGOUT_JTI_USER_MISMATCH_ALERT, extra=log_extra_mismatch
                )
            else:
                firelog.info(
                    LogStr.LOGOUT_SESSION_INVALIDATED, extra=log_extra_logout_request
                )
        else:
            firelog.info(
                LogStr.LOGOUT_NO_ACTIVE_SESSION_FOR_JTI, extra=log_extra_logout_request
            )
        return
