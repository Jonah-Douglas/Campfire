from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.core.constants.repository_outcomes import GeneralLogs
from app.core.logging.logger_wrapper import firelog
from app.core.repositories.base_repository import BaseRepository
from app.users.constants import UserModelConstants, UserRepoMessages
from app.users.models.user_model import User
from app.users.schemas.user_schema import (
    UserCompleteProfile,
    UserCreateInternal,
    UserUpdate,
)


class UserRepository(BaseRepository[User, UserCreateInternal, UserUpdate]):
    _CLASS_NAME = __qualname__
    _MODEL_NAME = UserModelConstants.MODEL_NAME

    def __init__(self) -> None:
        super().__init__(User)
        log_extra = {"class_name": self._CLASS_NAME}
        firelog.debug(GeneralLogs.INIT_TEMPLATE, extra=log_extra)

    # --- Generic Overrides ---
    def create(self, db: Session, *, obj_in: UserCreateInternal) -> User:
        _method_name = self.create.__name__
        log_extra = {"model_name": self._MODEL_NAME}
        firelog.debug(UserRepoMessages.CREATE_NOT_IMPLEMENTED, extra=log_extra)
        raise NotImplementedError(UserRepoMessages.CREATE_NOT_IMPLEMENTED % log_extra)

    # --- Custom Getters ---
    def get_by_email(self, db: Session, *, email: str) -> User:
        _method_name = self.get_by_email.__name__
        log_extra_attempt = {"model_name": self._MODEL_NAME, "email": email}
        firelog.info(
            UserRepoMessages.GET_BY_EMAIL_ATTEMPT_TEMPLATE, extra=log_extra_attempt
        )
        try:
            statement = select(self.model).where(self.model.email == email)
            user = db.execute(statement).scalar_one()
            log_extra_found = {
                "model_name": self._MODEL_NAME,
                "email": email,
                "user_id": user.id,
            }
            firelog.info(
                UserRepoMessages.GET_BY_EMAIL_FOUND_TEMPLATE, extra=log_extra_found
            )
            return user
        except NoResultFound:
            log_extra_not_found = {"model_name": self._MODEL_NAME, "email": email}
            firelog.warning(
                UserRepoMessages.GET_BY_EMAIL_NOT_FOUND_TEMPLATE,
                extra=log_extra_not_found,
            )
            raise
        except Exception as e:
            log_extra_error = {
                "class_name": self._CLASS_NAME,
                "method_name": _method_name,
                "model_name": self._MODEL_NAME,
                "error": str(e),
                "email_param": email,
            }
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE, exc_info=e, extra=log_extra_error
            )
            raise

    def get_by_phone_number(self, db: Session, *, phone_number: str) -> User:
        _method_name = self.get_by_phone_number.__name__
        log_extra_attempt = {
            "model_name": self._MODEL_NAME,
            "phone_number": phone_number,
        }
        firelog.info(
            UserRepoMessages.GET_BY_PHONE_ATTEMPT_TEMPLATE, extra=log_extra_attempt
        )
        try:
            statement = select(self.model).where(
                self.model.phone_number == phone_number
            )
            user = db.execute(statement).scalar_one()
            log_extra_found = {
                "model_name": self._MODEL_NAME,
                "phone_number": phone_number,
                "user_id": user.id,
            }
            firelog.info(
                UserRepoMessages.GET_BY_PHONE_FOUND_TEMPLATE, extra=log_extra_found
            )
            return user
        except NoResultFound:
            log_extra_not_found = {
                "model_name": self._MODEL_NAME,
                "phone_number": phone_number,
            }
            firelog.warning(
                UserRepoMessages.GET_BY_PHONE_NOT_FOUND_TEMPLATE,
                extra=log_extra_not_found,
            )
            raise
        except Exception as e:
            log_extra_error = {
                "class_name": self._CLASS_NAME,
                "method_name": _method_name,
                "model_name": self._MODEL_NAME,
                "error": str(e),
                "phone_param": phone_number,
            }
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE, exc_info=e, extra=log_extra_error
            )
            raise

    # --- Custom Existence Checks ---
    def exists_by_email(self, db: Session, *, email: str) -> bool:
        _method_name = self.exists_by_email.__name__
        log_extra_attempt = {
            "model_name": self._MODEL_NAME,
            "field_name": "email",
            "field_value": email,
            "class_name": self._CLASS_NAME,
            "method_name": _method_name,
        }
        firelog.info(
            UserRepoMessages.EXISTENCE_CHECK_ATTEMPT_TEMPLATE, extra=log_extra_attempt
        )
        try:
            statement = select(
                select(self.model.id).where(self.model.email == email).exists()
            )
            exists_result = db.execute(statement).scalar_one()
            log_extra_result = {
                "model_name": self._MODEL_NAME,
                "field_name": "email",
                "field_value": email,
                "exists_status": "exists" if exists_result else "does not exist",
                "class_name": self._CLASS_NAME,
                "method_name": _method_name,
            }
            firelog.info(
                UserRepoMessages.EXISTENCE_CHECK_RESULT_TEMPLATE, extra=log_extra_result
            )
            return exists_result
        except Exception as e:
            log_extra_error = {
                "class_name": self._CLASS_NAME,
                "method_name": _method_name,
                "model_name": self._MODEL_NAME,
                "error": str(e),
                "email_param": email,
            }
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE, exc_info=e, extra=log_extra_error
            )
            raise

    def exists_by_phone_number(self, db: Session, *, phone_number: str) -> bool:
        _method_name = self.exists_by_phone_number.__name__
        log_extra_attempt = {
            "model_name": self._MODEL_NAME,
            "field_name": "phone_number",
            "field_value": phone_number,
            "class_name": self._CLASS_NAME,
            "method_name": _method_name,
        }
        firelog.info(
            UserRepoMessages.EXISTENCE_CHECK_ATTEMPT_TEMPLATE, extra=log_extra_attempt
        )
        try:
            statement = select(
                select(self.model.id)
                .where(self.model.phone_number == phone_number)
                .exists()
            )
            exists_result = db.execute(statement).scalar_one()
            log_extra_result = {
                "model_name": self._MODEL_NAME,
                "field_name": "phone_number",
                "field_value": phone_number,
                "exists_status": "exists" if exists_result else "does not exist",
                "class_name": self._CLASS_NAME,
                "method_name": _method_name,
            }
            firelog.info(
                UserRepoMessages.EXISTENCE_CHECK_RESULT_TEMPLATE, extra=log_extra_result
            )
            return exists_result
        except Exception as e:
            log_extra_error = {
                "class_name": self._CLASS_NAME,
                "method_name": _method_name,
                "model_name": self._MODEL_NAME,
                "error": str(e),
                "phone_param": phone_number,
            }
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE, exc_info=e, extra=log_extra_error
            )
            raise

    # --- Custom Create/Update Methods
    def create_user_for_otp_flow(self, db: Session, *, phone_number: str) -> User:
        _method_name = self.create_user_for_otp_flow.__name__
        log_extra_attempt = {
            "model_name": self._MODEL_NAME,
            "phone_number": phone_number,
        }
        firelog.info(
            UserRepoMessages.CREATE_OTP_USER_ATTEMPT_TEMPLATE, extra=log_extra_attempt
        )

        db_user_data = {
            "phone_number": phone_number,
            "is_active": True,
            "is_profile_complete": False,
        }
        db_user = self.model(**db_user_data)

        def _success_log(created_user: User) -> None:
            log_extra_success = {
                "model_name": self._MODEL_NAME,
                "phone_number": phone_number,
                "user_id": created_user.id,
            }
            firelog.info(
                UserRepoMessages.CREATE_OTP_USER_SUCCESS_TEMPLATE,
                extra=log_extra_success,
            )

        return self._execute_commit_refresh_log(
            db=db,
            db_object=db_user,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="OTP user creation",
        )

    def update_user_profile_completion(
        self, db: Session, *, db_user_to_update: User, profile_data: UserCompleteProfile
    ) -> User:
        _method_name = self.update_user_profile_completion.__name__
        user_id = db_user_to_update.id
        log_extra_attempt = {"model_name": self._MODEL_NAME, "user_id": user_id}
        firelog.info(
            UserRepoMessages.UPDATE_PROFILE_ATTEMPT_TEMPLATE, extra=log_extra_attempt
        )

        user_data_dict = profile_data.model_dump(exclude_unset=True)
        for field, value in user_data_dict.items():
            if hasattr(db_user_to_update, field):
                setattr(db_user_to_update, field, value)
                log_extra_field_set = {
                    "model_name": self._MODEL_NAME,
                    "user_id": user_id,
                    "field_name": field,
                    "field_value": value,
                }
                firelog.debug(
                    UserRepoMessages.UPDATE_PROFILE_FIELD_SET_TEMPLATE,
                    extra=log_extra_field_set,
                )

        db_user_to_update.is_profile_complete = True
        log_extra_status = {
            "status": True,
            "model_name": self._MODEL_NAME,
            "user_id": user_id,
        }
        firelog.debug(
            UserRepoMessages.SET_PROFILE_COMPLETE_STATUS_TEMPLATE,
            extra=log_extra_status,
        )

        def _success_log(updated_user: User) -> None:
            log_extra_success = {
                "model_name": self._MODEL_NAME,
                "user_id": updated_user.id,
            }
            firelog.info(
                UserRepoMessages.UPDATE_PROFILE_SUCCESS_TEMPLATE,
                extra=log_extra_success,
            )

        return self._execute_commit_refresh_log(
            db=db,
            db_object=db_user_to_update,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="profile completion update",
        )

    # --- Utility Functions ---
    def update_last_login_at(self, db: Session, *, user_to_update: User) -> User:
        _method_name = self.update_last_login_at.__name__
        user_id = user_to_update.id
        log_extra_attempt = {"model_name": self._MODEL_NAME, "user_id": user_id}
        firelog.info(
            UserRepoMessages.UPDATE_LAST_LOGIN_ATTEMPT_TEMPLATE, extra=log_extra_attempt
        )

        new_last_login_at = datetime.now(UTC)
        user_to_update.last_login_at = new_last_login_at

        def _success_log(updated_user: User) -> None:
            log_extra_success = {
                "last_login_at": new_last_login_at,
                "model_name": self._MODEL_NAME,
                "user_id": updated_user.id,
            }
            firelog.info(
                UserRepoMessages.UPDATE_LAST_LOGIN_SUCCESS_TEMPLATE,
                extra=log_extra_success,
            )

        return self._execute_commit_refresh_log(
            db=db,
            db_object=user_to_update,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="last login at update",
        )

    def set_active_status(
        self, db: Session, *, user_to_update: User, is_active: bool
    ) -> User:
        _method_name = self.set_active_status.__name__
        user_id = user_to_update.id
        log_extra_attempt = {
            "is_active": is_active,
            "model_name": self._MODEL_NAME,
            "user_id": user_id,
        }
        firelog.info(
            UserRepoMessages.SET_ACTIVE_STATUS_ATTEMPT_TEMPLATE, extra=log_extra_attempt
        )
        user_to_update.is_active = is_active

        def _success_log(updated_user: User) -> None:
            log_extra_success = {
                "is_active": updated_user.is_active,
                "model_name": self._MODEL_NAME,
                "user_id": updated_user.id,
            }
            firelog.info(
                UserRepoMessages.SET_ACTIVE_STATUS_SUCCESS_TEMPLATE,
                extra=log_extra_success,
            )

        return self._execute_commit_refresh_log(
            db=db,
            db_object=user_to_update,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="active status update",
        )
