from datetime import UTC, datetime, timedelta

from pydantic import BaseModel
from sqlalchemy import delete, select, update as sa_update
from sqlalchemy.orm import Session

from app.auth.constants import (
    PendingOTPModelConstants,
    PendingOTPRepoMessages as RepoMsg,
)
from app.auth.models.pending_otp_model import OTPStatus, PendingOTP
from app.core.config import settings
from app.core.constants.repository_outcomes import GeneralLogs
from app.core.logging.logger_wrapper import firelog
from app.core.repositories.base_repository import BaseRepository
from app.core.security import hash_otp_value, verify_otp_value


class _DummyOTPSchema(BaseModel):
    pass


class PendingOTPRepository(
    BaseRepository[PendingOTP, _DummyOTPSchema, _DummyOTPSchema]
):
    _CLASS_NAME = __qualname__
    _MODEL_NAME = PendingOTPModelConstants.MODEL_NAME

    def __init__(self) -> None:
        super().__init__(PendingOTP)
        log_extra = {"model_name": self._MODEL_NAME}
        firelog.debug(GeneralLogs.INIT_TEMPLATE, log_extra)

    # --- Generic Overrides ---
    def create(self, db: Session, *, obj_in: _DummyOTPSchema) -> PendingOTP:
        _method_name = self.create.__name__
        firelog.debug(GeneralLogs.GENERIC_CREATE_NOT_IMPLEMENTED % self._CLASS_NAME)
        raise NotImplementedError(
            GeneralLogs.GENERIC_CREATE_NOT_IMPLEMENTED % self._CLASS_NAME
        )

    def update(
        self, db: Session, *, db_obj_to_update: PendingOTP, obj_in: _DummyOTPSchema
    ) -> PendingOTP:
        _method_name = self.update.__name__
        firelog.debug(GeneralLogs.GENERIC_UPDATE_NOT_IMPLEMENTED % self._CLASS_NAME)
        raise NotImplementedError(
            GeneralLogs.GENERIC_UPDATE_NOT_IMPLEMENTED % self._CLASS_NAME
        )

    # --- Custom Create Methods ---
    def create_pending_otp(
        self,
        db: Session,
        *,
        phone_number: str,
        plain_otp: str,
        expires_delta: timedelta | None = None,
        max_attempts: int | None = None,
    ) -> PendingOTP:
        _method_name = self.create_pending_otp.__name__
        phone_prefix = phone_number[:7] if phone_number else "N/A"

        log_extra_creating = {
            "phone_prefix": phone_prefix,
        }
        firelog.info(RepoMsg.CREATING, extra=log_extra_creating)

        expires_delta_actual = expires_delta or timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )
        max_attempts_actual = max_attempts or settings.MAX_OTP_ATTEMPTS

        hashed_otp = hash_otp_value(plain_otp)
        expires_at = datetime.now(UTC) + expires_delta_actual

        db_otp_data = {
            "status": OTPStatus.PENDING,
            "phone_number": phone_number,
            "hashed_otp": hashed_otp,
            "expires_at": expires_at,
            "attempts_left": max_attempts_actual,
        }
        db_otp = self.model(**db_otp_data)

        def _success_log(created_otp: PendingOTP) -> None:
            log_extra_success = {
                "otp_id": created_otp.id,
                "phone_prefix": phone_prefix,
            }
            firelog.info(RepoMsg.CREATED_SUCCESS, extra=log_extra_success)

        return self._execute_commit_refresh_log(
            db=db,
            db_object=db_otp,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="pending OTP creation",
        )

    # --- Custom Getters ---
    def get_active_pending_otp_by_phone(
        self, db: Session, *, phone_number: str
    ) -> PendingOTP | None:
        _method_name = self.get_active_pending_otp_by_phone.__name__
        phone_prefix = phone_number[:7] if phone_number else "N/A"

        log_extra_fetching = {"phone_prefix": phone_prefix}
        firelog.info(RepoMsg.FETCHING_ACTIVE, extra=log_extra_fetching)
        try:
            statement = (
                select(self.model)
                .where(self.model.phone_number == phone_number)
                .where(self.model.status == OTPStatus.PENDING)
                .where(self.model.expires_at > datetime.now(UTC))
                .where(self.model.attempts_left > 0)
                .order_by(self.model.created_at.desc())
            )
            otp = db.execute(statement).scalar_one_or_none()

            if otp:
                log_extra_found = {
                    "otp_id": otp.id,
                    "phone_prefix": phone_prefix,
                }
                firelog.info(RepoMsg.ACTIVE_FOUND, extra=log_extra_found)
            else:
                firelog.info(RepoMsg.NO_ACTIVE_FOUND, extra=log_extra_fetching)
            return otp
        except Exception as e:
            log_extra = {
                "class_name": self._CLASS_NAME,
                "method_name": _method_name,
                "model_name": self._MODEL_NAME,
                "error": str(e),
            }
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE, exc_info=e, extra=log_extra
            )
            raise

    # --- Custom Existence Checks (Example) ---
    def active_otp_exists_for_phone(self, db: Session, *, phone_number: str) -> bool:
        _method_name = self.active_otp_exists_for_phone.__name__
        phone_prefix = phone_number[:7] if phone_number else "N/A"

        log_extra_fetching = {"phone_prefix": phone_prefix}
        firelog.info(RepoMsg.FETCHING_ACTIVE, extra=log_extra_fetching)
        try:
            statement = select(
                select(self.model.id)
                .where(self.model.phone_number == phone_number)
                .where(self.model.status == OTPStatus.PENDING)
                .where(self.model.expires_at > datetime.now(UTC))
                .where(self.model.attempts_left > 0)
                .exists()
            )
            exists_result = db.execute(statement).scalar_one()

            log_extra_exists_check = {
                "phone_prefix": phone_prefix,
                "exists": exists_result,
            }
            if exists_result:
                firelog.info(
                    f"Active OTP check for {phone_prefix}: Found.",
                    extra=log_extra_exists_check,
                )
            else:
                firelog.info(
                    f"Active OTP check for {phone_prefix}: Not Found.",
                    extra=log_extra_exists_check,
                )
            return exists_result
        except Exception as e:
            log_extra = {
                "class_name": self._CLASS_NAME,
                "method_name": _method_name,
                "model_name": self._MODEL_NAME,
                "error": str(e),
            }
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE, exc_info=e, extra=log_extra
            )
            raise

    # --- Custom Update/Action Methods ---
    def verify_and_consume_otp(
        self, db: Session, *, phone_number: str, submitted_otp: str
    ) -> tuple[bool, PendingOTP | None, str]:
        _method_name = self.verify_and_consume_otp.__name__
        phone_prefix = phone_number[:7] if phone_number else "N/A"

        log_extra_attempt = {"phone_prefix": phone_prefix}
        firelog.info(RepoMsg.VERIFICATION_ATTEMPT, extra=log_extra_attempt)

        active_otp = self.get_active_pending_otp_by_phone(
            db=db, phone_number=phone_number
        )

        if not active_otp:
            firelog.warning(RepoMsg.VERIFY_NO_ACTIVE, extra=log_extra_attempt)
            return False, None, RepoMsg.VERIFY_NO_ACTIVE % log_extra_attempt

        otp_id = active_otp.id
        log_extra_otp_context = {
            "otp_id": otp_id,
            "phone_prefix": phone_prefix,
        }

        user_message_key_constant = ""
        user_message_args = log_extra_otp_context.copy()

        if active_otp.expires_at <= datetime.now(UTC):
            active_otp.status = OTPStatus.EXPIRED
            active_otp.attempts_left = 0
            user_message_key_constant = RepoMsg.EXPIRED_DURING_VERIFICATION
            firelog.warning(
                RepoMsg.EXPIRED_DURING_VERIFICATION, extra=log_extra_otp_context
            )
        elif not verify_otp_value(submitted_otp, active_otp.hashed_otp):
            active_otp.attempts_left -= 1
            if active_otp.attempts_left <= 0:
                active_otp.status = OTPStatus.MAX_ATTEMPTS
                user_message_key_constant = RepoMsg.MAX_ATTEMPTS_REACHED
                firelog.warning(
                    RepoMsg.MAX_ATTEMPTS_REACHED, extra=log_extra_otp_context
                )
            else:
                log_extra_invalid = {
                    **log_extra_otp_context,
                    "attempts_left": active_otp.attempts_left,
                }
                user_message_key_constant = RepoMsg.INVALID_ATTEMPT
                user_message_args.update({"attempts_left": active_otp.attempts_left})
                firelog.info(RepoMsg.INVALID_ATTEMPT, extra=log_extra_invalid)
        else:
            active_otp.status = OTPStatus.VERIFIED
            active_otp.attempts_left = (
                0  # Ensure attempts_left is zeroed out on success
            )
            user_message_key_constant = RepoMsg.SUCCESSFULLY_VERIFIED
            success = True

        final_user_message = (
            user_message_key_constant % user_message_args
            if user_message_key_constant
            else "OTP verification processed."
        )

        def _success_log_callback(updated_otp: PendingOTP) -> None:
            log_method = firelog.info if success else firelog.warning
            log_extra_callback = {
                "otp_id": updated_otp.id,
                "phone_prefix": phone_prefix,
                "status": updated_otp.status.value,
                "successful_verification": success,
            }
            if success:
                log_method(RepoMsg.SUCCESSFULLY_VERIFIED, extra=log_extra_callback)
            else:
                log_method(
                    f"OTP record {updated_otp.id} for {phone_prefix} updated after verification attempt. Final status: {updated_otp.status.value}",
                    extra=log_extra_callback,
                )

        updated_otp_record = self._execute_commit_refresh_log(
            db=db,
            db_object=active_otp,
            calling_method_name=_method_name,
            success_log_callback=_success_log_callback,
            operation_verb="OTP verification/consumption",
        )
        if "success" not in locals():
            success = False  # Default if not set

        return success, updated_otp_record if success else None, final_user_message

    def invalidate_existing_pending_otps(
        self, db: Session, *, phone_number: str
    ) -> int:
        _method_name = self.invalidate_existing_pending_otps.__name__
        phone_prefix = phone_number[:7] if phone_number else "N/A"

        log_extra_invalidating = {"phone_prefix": phone_prefix}
        firelog.info(RepoMsg.INVALIDATING_EXISTING, extra=log_extra_invalidating)
        try:
            update_statement = (
                sa_update(self.model)
                .where(self.model.phone_number == phone_number)
                .where(self.model.status == OTPStatus.PENDING)
                .values(status=OTPStatus.EXPIRED, attempts_left=0)
            )
            result = db.execute(update_statement)
            db.commit()
            count = result.rowcount

            log_extra_success_count = {
                "count": count,
                "phone_prefix": phone_prefix,
            }
            firelog.info(
                RepoMsg.INVALIDATED_SUCCESS_COUNT, extra=log_extra_success_count
            )
            return count
        except Exception as e:
            db.rollback()
            log_extra_failed = {
                "phone_prefix": phone_prefix,
                "error": str(e),
                "class_name": self._CLASS_NAME,
                "method_name": _method_name,
                "model_name": self._MODEL_NAME,
                "operation_verb": "invalidate existing pending OTPs",
            }
            firelog.error(RepoMsg.INVALIDATE_FAILED, exc_info=e, extra=log_extra_failed)
            raise

    def update_otp_status(
        self, db: Session, *, otp_record: PendingOTP, new_status: OTPStatus
    ) -> PendingOTP:
        _method_name = self.update_otp_status.__name__
        otp_id = otp_record.id
        old_status_val = otp_record.status.value if otp_record.status else "N/A"

        log_extra_updating = {
            "otp_id": otp_id,
            "old_status": old_status_val,
            "new_status": new_status.value,
        }
        firelog.info(RepoMsg.UPDATING_STATUS, extra=log_extra_updating)

        otp_record.status = new_status
        if new_status in [
            OTPStatus.EXPIRED,
            OTPStatus.VERIFIED,
            OTPStatus.MAX_ATTEMPTS,
            OTPStatus.ERROR_SENDING,
        ]:
            otp_record.attempts_left = 0

        def _success_log(updated_otp: PendingOTP) -> None:
            log_extra_success = {
                "otp_id": updated_otp.id,
                "new_status": updated_otp.status.value,
            }
            firelog.info(RepoMsg.STATUS_UPDATED_SUCCESS, extra=log_extra_success)

        return self._execute_commit_refresh_log(
            db=db,
            db_object=otp_record,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="OTP status update",
        )

    def set_otp_sending_error(self, db: Session, *, otp_id: int) -> PendingOTP | None:
        _method_name = self.set_otp_sending_error.__name__
        log_extra_otp_id = {"otp_id": otp_id}

        firelog.info(RepoMsg.SETTING_SEND_ERROR, extra=log_extra_otp_id)

        db_otp = db.get(self.model, otp_id)

        if not db_otp:
            firelog.warning(RepoMsg.SET_SEND_ERROR_NOT_FOUND, extra=log_extra_otp_id)
            return None

        db_otp.status = OTPStatus.ERROR_SENDING
        db_otp.attempts_left = 0

        def _success_log(updated_otp: PendingOTP) -> None:
            firelog.info(
                RepoMsg.SEND_ERROR_SET_SUCCESS, extra={"otp_id": updated_otp.id}
            )

        return self._execute_commit_refresh_log(
            db=db,
            db_object=db_otp,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="set OTP sending error",
        )

    def cleanup_expired_otps(self, db: Session) -> int:
        _method_name = self.cleanup_expired_otps.__name__
        log_extra_start = {"model_name": self._MODEL_NAME}
        firelog.info(RepoMsg.CLEANUP_STARTED, extra=log_extra_start)

        now = datetime.now(UTC)
        terminal_statuses = [
            OTPStatus.EXPIRED,
            OTPStatus.VERIFIED,
            OTPStatus.MAX_ATTEMPTS,
            OTPStatus.ERROR_SENDING,
        ]
        try:
            delete_statement = delete(self.model).where(
                (self.model.expires_at < now)
                | (self.model.status.in_(terminal_statuses))
            )
            result = db.execute(delete_statement)
            db.commit()
            count = result.rowcount

            log_extra_cleaned = {"count": count, "model_name": self._MODEL_NAME}
            firelog.info(RepoMsg.CLEANED_UP_SUCCESS_COUNT, extra=log_extra_cleaned)
            return count
        except Exception as e:
            db.rollback()
            log_extra_failed = {
                "error": str(e),
                "class_name": self._CLASS_NAME,
                "method_name": _method_name,
                "model_name": self._MODEL_NAME,
                "operation_verb": "cleanup expired OTPs",
            }
            firelog.error(RepoMsg.CLEANUP_FAILED, exc_info=e, extra=log_extra_failed)
            raise
