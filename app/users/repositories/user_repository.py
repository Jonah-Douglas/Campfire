from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.core.constants.repository_outcomes import GeneralLogs
from app.core.logging_config import firelog
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
        firelog.debug(GeneralLogs.INIT_TEMPLATE.format(class_name=self._CLASS_NAME))

    # --- Generic Overrides ---
    def create(self, db: Session, *, obj_in: UserCreateInternal) -> User:
        """
        Generic creation is disabled for Users.
        Please use the specific workflow: create_user_for_otp_flow()
        followed by update_user_profile_completion().
        """
        _method_name = self.create.__name__
        firelog.warning(
            GeneralLogs.METHOD_ENTRY_TEMPLATE.format(
                class_name=self._CLASS_NAME, method_name=_method_name
            )
            + " - Operation explicitly not implemented."
        )

        raise NotImplementedError(
            UserRepoMessages.CREATE_NOT_IMPLEMENTED.format(model_name=self._MODEL_NAME)
        )

    # --- Custom Getters ---
    def get_by_email(self, db: Session, *, email: str) -> User:
        """
        Get a single user by email.
        Raises NoResultFound if no user is found.
        """
        _method_name = self.get_by_email.__name__
        firelog.info(
            UserRepoMessages.GET_BY_EMAIL_ATTEMPT_TEMPLATE.format(
                model_name=self._MODEL_NAME, email=email
            )
        )
        try:
            statement = select(self.model).where(self.model.email == email)
            user = db.execute(statement).scalar_one()
            firelog.info(
                UserRepoMessages.GET_BY_EMAIL_FOUND_TEMPLATE.format(
                    model_name=self._MODEL_NAME, email=email, user_id=user.id
                )
            )
            return user
        except NoResultFound:
            firelog.warning(
                UserRepoMessages.GET_BY_EMAIL_NOT_FOUND_TEMPLATE.format(
                    model_name=self._MODEL_NAME, email=email
                )
            )
            raise
        except Exception as e:
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE.format(
                    class_name=self._CLASS_NAME, method_name=_method_name, error=str(e)
                ),
                exc_info=True,
            )
            raise

    def get_by_phone_number(self, db: Session, *, phone_number: str) -> User:
        """
        Get a single user by phone number.
        Raises NoResultFound if no user is found.
        """
        _method_name = self.get_by_phone_number.__name__
        firelog.info(
            UserRepoMessages.GET_BY_PHONE_ATTEMPT_TEMPLATE.format(
                model_name=self._MODEL_NAME, phone_number=phone_number
            )
        )
        try:
            statement = select(self.model).where(
                self.model.phone_number == phone_number
            )
            user = db.execute(statement).scalar_one()
            firelog.info(
                UserRepoMessages.GET_BY_PHONE_FOUND_TEMPLATE.format(
                    model_name=self._MODEL_NAME,
                    phone_number=phone_number,
                    user_id=user.id,
                )
            )
            return user
        except NoResultFound:
            firelog.warning(
                UserRepoMessages.GET_BY_PHONE_NOT_FOUND_TEMPLATE.format(
                    model_name=self._MODEL_NAME, phone_number=phone_number
                )
            )
            raise
        except Exception as e:
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE.format(
                    class_name=self._CLASS_NAME, method_name=_method_name, error=str(e)
                ),
                exc_info=True,
            )
            raise

    # --- Custom Existence Checks ---
    def exists_by_email(self, db: Session, *, email: str) -> bool:
        """Checks if a user exists with the given email."""
        _method_name = self.exists_by_email.__name__
        firelog.info(
            f"Attempting to check existence for {self._MODEL_NAME} by email: {email} in {self._CLASS_NAME}.{_method_name}"
        )
        try:
            statement = select(
                select(self.model.id).where(self.model.email == email).exists()
            )
            exists_result = db.execute(statement).scalar_one()
            log_msg = f"{self._MODEL_NAME} with email {email} {'exists' if exists_result else 'does not exist'}."
            firelog.info(log_msg + f" ({self._CLASS_NAME}.{_method_name})")
            return exists_result
        except Exception as e:
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE.format(
                    class_name=self._CLASS_NAME, method_name=_method_name, error=str(e)
                ),
                exc_info=True,
            )
            raise

    def exists_by_phone_number(self, db: Session, *, phone_number: str) -> bool:
        """Checks if a user exists with the given phone number."""
        _method_name = self.exists_by_phone_number.__name__
        firelog.info(
            f"Attempting to check existence for {self._MODEL_NAME} by phone_number: {phone_number} in {self._CLASS_NAME}.{_method_name}"
        )
        try:
            statement = select(
                select(self.model.id)
                .where(self.model.phone_number == phone_number)
                .exists()
            )
            exists_result = db.execute(statement).scalar_one()
            log_msg = f"{self._MODEL_NAME} with phone_number {phone_number} {'exists' if exists_result else 'does not exist'}."
            firelog.info(log_msg + f" ({self._CLASS_NAME}.{_method_name})")
            return exists_result
        except Exception as e:
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE.format(
                    class_name=self._CLASS_NAME, method_name=_method_name, error=str(e)
                ),
                exc_info=True,
            )
            raise

    # --- Custom Create/Update Methods
    def create_user_for_otp_flow(self, db: Session, *, phone_number: str) -> User:
        """
        Creates a new user with minimal info after successful OTP verification.
        Sets default values for a new user.
        """
        _method_name = self.create_user_for_otp_flow.__name__
        firelog.info(
            UserRepoMessages.CREATE_OTP_USER_ATTEMPT_TEMPLATE.format(
                model_name=self._MODEL_NAME, phone_number=phone_number
            )
        )

        db_user_data = {
            "phone_number": phone_number,
            "is_active": True,
            "is_profile_complete": False,
        }
        db_user = self.model(**db_user_data)

        def _success_log(created_user: User) -> None:
            firelog.info(
                UserRepoMessages.CREATE_OTP_USER_SUCCESS_TEMPLATE.format(
                    model_name=self._MODEL_NAME,
                    phone_number=phone_number,
                    user_id=created_user.id,
                )
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
        """
        Update a new user's default profile information and marks profile as complete.
        """
        _method_name = self.update_user_profile_completion.__name__
        user_id = db_user_to_update.id
        firelog.info(
            UserRepoMessages.UPDATE_PROFILE_ATTEMPT_TEMPLATE.format(
                model_name=self._MODEL_NAME, user_id=user_id
            )
        )

        user_data_dict = profile_data.model_dump(exclude_unset=True)
        for field, value in user_data_dict.items():
            if hasattr(db_user_to_update, field):
                setattr(db_user_to_update, field, value)
                firelog.debug(
                    UserRepoMessages.UPDATE_PROFILE_FIELD_SET_TEMPLATE.format(
                        model_name=self._MODEL_NAME,
                        user_id=user_id,
                        field_name=field,
                        field_value=value,
                    )
                )
        db_user_to_update.is_profile_complete = True
        firelog.debug(
            UserRepoMessages.SET_PROFILE_COMPLETE_STATUS_TEMPLATE.format(
                status=True, model_name=self._MODEL_NAME, user_id=user_id
            )
        )

        def _success_log(updated_user: User) -> None:
            firelog.info(
                UserRepoMessages.UPDATE_PROFILE_SUCCESS_TEMPLATE.format(
                    model_name=self._MODEL_NAME, user_id=updated_user.id
                )
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
        """
        Updates the last_login_at timestamp for a user.
        """
        _method_name = self.update_last_login_at.__name__
        user_id = user_to_update.id
        firelog.info(
            UserRepoMessages.UPDATE_LAST_LOGIN_ATTEMPT_TEMPLATE.format(
                model_name=self._MODEL_NAME, user_id=user_id
            )
        )

        new_last_login_at = datetime.now(UTC)
        user_to_update.last_login_at = new_last_login_at

        def _success_log(updated_user: User) -> None:
            firelog.info(
                UserRepoMessages.UPDATE_LAST_LOGIN_SUCCESS_TEMPLATE.format(
                    last_login_at=new_last_login_at,
                    model_name=self._MODEL_NAME,
                    user_id=updated_user.id,
                )
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
        """
        Activates or deactivates a user account.
        Combines activate_user and deactivate_user.
        """
        _method_name = self.set_active_status.__name__
        user_id = user_to_update.id
        firelog.info(
            UserRepoMessages.SET_ACTIVE_STATUS_ATTEMPT_TEMPLATE.format(
                is_active=is_active, model_name=self._MODEL_NAME, user_id=user_id
            )
        )
        user_to_update.is_active = is_active

        def _success_log(updated_user: User) -> None:
            firelog.info(
                UserRepoMessages.SET_ACTIVE_STATUS_SUCCESS_TEMPLATE.format(
                    is_active=is_active,
                    model_name=self._MODEL_NAME,
                    user_id=updated_user.id,
                )
            )

        return self._execute_commit_refresh_log(
            db=db,
            db_object=user_to_update,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="active status update",
        )
