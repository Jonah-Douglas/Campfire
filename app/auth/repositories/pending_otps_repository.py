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
        firelog.debug(f"Initialized {self._CLASS_NAME}.")

    # --- Generic Overrides ---
    def create(self, db: Session, *, obj_in: _DummyOTPSchema) -> PendingOTP:
        _method_name = self.create.__name__
        log_message = (
            GeneralLogs.METHOD_ENTRY_TEMPLATE.format(
                class_name=self._CLASS_NAME, method_name=_method_name
            )
            + " - Operation explicitly not implemented."
        )
        firelog.warning(log_message)
        raise NotImplementedError(GeneralLogs.GENERIC_CREATE_NOT_IMPLEMENTED)

    def update(
        self, db: Session, *, db_obj_to_update: PendingOTP, obj_in: _DummyOTPSchema
    ) -> PendingOTP:
        _method_name = self.update.__name__
        log_message = (
            GeneralLogs.METHOD_ENTRY_TEMPLATE.format(
                class_name=self._CLASS_NAME, method_name=_method_name
            )
            + " - Operation explicitly not implemented."
        )
        firelog.warning(log_message)
        raise NotImplementedError(GeneralLogs.GENERIC_UPDATE_NOT_IMPLEMENTED)

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
        firelog.info(
            RepoMsg.CREATING.format(
                model_name=self._MODEL_NAME, phone_prefix=phone_prefix
            )
        )

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
            firelog.info(
                RepoMsg.CREATED_SUCCESS.format(
                    model_name=self._MODEL_NAME,
                    otp_id=created_otp.id,
                    phone_prefix=phone_prefix,
                )
            )

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
        firelog.info(
            RepoMsg.FETCHING_ACTIVE.format(
                model_name=self._MODEL_NAME, phone_prefix=phone_prefix
            )
        )
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
                firelog.info(
                    RepoMsg.ACTIVE_FOUND.format(
                        model_name=self._MODEL_NAME,
                        otp_id=otp.id,
                        phone_prefix=phone_prefix,
                    )
                )
            else:
                firelog.info(
                    RepoMsg.NO_ACTIVE_FOUND.format(
                        model_name=self._MODEL_NAME, phone_prefix=phone_prefix
                    )
                )
            return otp
        except Exception as e:
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE.format(
                    class_name=self._CLASS_NAME, method_name=_method_name, error=str(e)
                ),
                exc_info=True,
            )
            raise

    # --- Custom Existence Checks (Example) ---
    def active_otp_exists_for_phone(self, db: Session, *, phone_number: str) -> bool:
        """Checks if an active (pending, not expired, attempts left) OTP exists for the phone."""
        _method_name = self.active_otp_exists_for_phone.__name__
        phone_prefix = phone_number[:7] if phone_number else "N/A"
        firelog.info(
            RepoMsg.FETCHING_ACTIVE.format(
                model_name=self._MODEL_NAME, phone_prefix=phone_prefix
            )
        )
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
            firelog.info(
                RepoMsg.ACTIVE_FOUND.format(
                    model_name=self._MODEL_NAME,
                    phone_prefix=phone_prefix,
                    exists=exists_result,
                )
            )
            return exists_result
        except Exception as e:
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE.format(
                    class_name=self._CLASS_NAME, method_name=_method_name, error=str(e)
                ),
                exc_info=True,
            )
            raise

    # --- Custom Update/Action Methods ---
    def verify_and_consume_otp(
        self, db: Session, *, phone_number: str, submitted_otp: str
    ) -> tuple[bool, PendingOTP | None, str]:
        _method_name = self.verify_and_consume_otp.__name__
        phone_prefix = phone_number[:7] if phone_number else "N/A"
        firelog.info(
            RepoMsg.VERIFICATION_ATTEMPT.format(
                model_name=self._MODEL_NAME, phone_prefix=phone_prefix
            )
        )
        active_otp = self.get_active_pending_otp_by_phone(
            db=db, phone_number=phone_number
        )

        if not active_otp:
            firelog.warning(
                RepoMsg.VERIFY_NO_ACTIVE.format(
                    model_name=self._MODEL_NAME, phone_prefix=phone_prefix
                )
            )
            return False, None, RepoMsg.VERIFY_NO_ACTIVE

        otp_id = active_otp.id
        message_key: str = ""
        success: bool = False

        if active_otp.expires_at <= datetime.now(UTC):
            active_otp.status = OTPStatus.EXPIRED
            active_otp.attempts_left = 0
            message_key = RepoMsg.EXPIRED_DURING_VERIFICATION
            firelog.warning(
                RepoMsg.EXPIRED_DURING_VERIFICATION.format(
                    model_name=self._MODEL_NAME,
                    otp_id=otp_id,
                    phone_prefix=phone_prefix,
                ),
            )
        elif not verify_otp_value(submitted_otp, active_otp.hashed_otp):
            active_otp.attempts_left -= 1
            if active_otp.attempts_left <= 0:
                active_otp.status = OTPStatus.MAX_ATTEMPTS
                message_key = RepoMsg.MAX_ATTEMPTS_REACHED
                firelog.warning(
                    RepoMsg.MAX_ATTEMPTS_REACHED.format(
                        model_name=self._MODEL_NAME,
                        otp_id=otp_id,
                        phone_prefix=phone_prefix,
                    ),
                )
            else:
                message_key = RepoMsg.INVALID_ATTEMPT.format(
                    attempts_left=active_otp.attempts_left
                )
                firelog.info(
                    RepoMsg.VERIFY_FAILED_ERROR.format(
                        model_name=self._MODEL_NAME,
                        otp_id=otp_id,
                        phone_prefix=phone_prefix,
                        attempts_left=active_otp.attempts_left,
                    ),
                )
        else:
            active_otp.status = OTPStatus.VERIFIED
            active_otp.attempts_left = 0
            message_key = RepoMsg.SUCCESSFULLY_VERIFIED
            success = True

        def _success_log_callback(updated_otp: PendingOTP) -> None:
            log_method = firelog.info if success else firelog.warning
            log_method(
                RepoMsg.SUCCESSFULLY_VERIFIED.format(
                    model_name=self._MODEL_NAME,
                    otp_id=updated_otp.id,
                    phone_prefix=phone_prefix,
                    status=updated_otp.status.value,
                    success=success,
                )
            )

        updated_otp_record = self._execute_commit_refresh_log(
            db=db,
            db_object=active_otp,
            calling_method_name=_method_name,
            success_log_callback=_success_log_callback,
            operation_verb="OTP verification/consumption",
        )
        return success, updated_otp_record if success else None, message_key

    def invalidate_existing_pending_otps(
        self, db: Session, *, phone_number: str
    ) -> int:
        _method_name = self.invalidate_existing_pending_otps.__name__
        phone_prefix = phone_number[:7] if phone_number else "N/A"
        firelog.info(
            RepoMsg.INVALIDATING_EXISTING.format(
                model_name=self._MODEL_NAME, phone_prefix=phone_prefix
            )
        )
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
            firelog.info(
                RepoMsg.INVALIDATED_SUCCESS_COUNT.format(
                    model_name=self._MODEL_NAME, count=count, phone_prefix=phone_prefix
                )
            )
            return count
        except Exception as e:
            db.rollback()
            firelog.error(
                RepoMsg.INVALIDATE_FAILED.format(
                    class_name=self._CLASS_NAME,
                    method_name=_method_name,
                    model_name=self._MODEL_NAME,
                    operation_verb="invalidate existing OTPs",
                    error=str(e),
                ),
                exc_info=True,
            )
            raise

    def update_otp_status(
        self, db: Session, *, otp_record: PendingOTP, new_status: OTPStatus
    ) -> PendingOTP:
        _method_name = self.update_otp_status.__name__
        otp_id = otp_record.id
        old_status_val = otp_record.status.value if otp_record.status else "N/A"

        firelog.info(
            RepoMsg.UPDATING_STATUS.format(
                model_name=self._MODEL_NAME,
                otp_id=otp_id,
                old_status=old_status_val,
                new_status=new_status.value,
            )
        )
        otp_record.status = new_status
        if new_status in [
            OTPStatus.EXPIRED,
            OTPStatus.VERIFIED,
            OTPStatus.MAX_ATTEMPTS,
            OTPStatus.ERROR_SENDING,
        ]:
            otp_record.attempts_left = 0

        def _success_log(updated_otp: PendingOTP) -> None:
            firelog.info(
                RepoMsg.STATUS_UPDATED_SUCCESS.format(
                    model_name=self._MODEL_NAME,
                    otp_id=updated_otp.id,
                    new_status=updated_otp.status.value,
                )
            )

        return self._execute_commit_refresh_log(
            db=db,
            db_object=otp_record,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="OTP status update",
        )

    def set_otp_sending_error(self, db: Session, *, otp_id: int) -> PendingOTP | None:
        _method_name = self.set_otp_sending_error.__name__
        firelog.info(
            RepoMsg.SETTING_SEND_ERROR.format(
                model_name=self._MODEL_NAME, otp_id=otp_id
            )
        )

        db_otp = db.get(self.model, otp_id)

        if not db_otp:
            firelog.warning(
                RepoMsg.SET_SEND_ERROR_NOT_FOUND.format(
                    model_name=self._MODEL_NAME, otp_id=otp_id
                )
            )
            return None

        db_otp.status = OTPStatus.ERROR_SENDING
        db_otp.attempts_left = 0

        def _success_log(updated_otp: PendingOTP) -> None:
            firelog.info(
                RepoMsg.SEND_ERROR_SET_SUCCESS.format(
                    model_name=self._MODEL_NAME, otp_id=updated_otp.id
                )
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
        firelog.info(RepoMsg.CLEANUP_STARTED.format(model_name=self._MODEL_NAME))
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
            firelog.info(
                RepoMsg.CLEANED_UP_SUCCESS_COUNT.format(
                    model_name=self._MODEL_NAME, count=count
                )
            )
            return count
        except Exception as e:
            db.rollback()
            firelog.error(
                RepoMsg.CLEANUP_FAILED.format(
                    class_name=self._CLASS_NAME,
                    method_name=_method_name,
                    model_name=self._MODEL_NAME,
                    operation_verb="cleanup expired OTPs",
                    error=str(e),
                ),
                exc_info=True,
            )
            raise
