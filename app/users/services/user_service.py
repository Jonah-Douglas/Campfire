from collections.abc import Sequence

from fastapi import status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.core.constants.repository_outcomes import GeneralLogs
from app.core.enums.log_levels import LogLevel
from app.core.exceptions import log_and_raise_http_exception
from app.core.logging.logger_wrapper import firelog
from app.core.services.base_service import BaseService
from app.users.constants import (
    UserHttpErrorDetails,
    UserServiceLoggingStrings as LogStr,
)
from app.users.dependencies import UserRepoDependency
from app.users.models.user_model import User
from app.users.repositories.user_repository import UserRepository
from app.users.schemas.user_schema import (
    UserCompleteProfile,
    UserCreateInternal,
    UserPublic,
    UsersPublic,
    UserUpdate,
)


class UserService(BaseService[UserRepository]):
    _SERVICE_NAME = LogStr._SERVICE_NAME

    def __init__(self, user_repository: UserRepoDependency) -> None:
        super().__init__(user_repository)
        firelog.debug(GeneralLogs.INIT_TEMPLATE % self._SERVICE_NAME)

    def get_user_by_id(self, db: Session, user_id: int) -> User:
        _method_name = self.get_user_by_id.__name__
        log_extra_attempt = {"service_name": self._SERVICE_NAME, "user_id": user_id}
        firelog.info(LogStr.GET_USER_BY_ID_ATTEMPT_TEMPLATE, extra=log_extra_attempt)
        try:
            db_user = self._repository.get(db=db, id=user_id)
            if not db_user:
                log_and_raise_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE.format(
                        user_id=user_id
                    ),
                    log_level=LogLevel.WARNING,
                    service_name=self._SERVICE_NAME,
                    method_name=_method_name,
                    additional_log_info={"user_id": user_id},
                )
            firelog.info(
                LogStr.GET_USER_BY_ID_SUCCESS_TEMPLATE, extra=log_extra_attempt
            )
            return db_user
        except NoResultFound:
            log_and_raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE.format(
                    user_id=user_id
                ),
                log_level=LogLevel.WARNING,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={"user_id": user_id},
            )

    def get_user_by_phone_number(self, db: Session, phone_number: str) -> User:
        _method_name = self.get_user_by_phone_number.__name__
        log_extra_attempt = {
            "service_name": self._SERVICE_NAME,
            "phone_number": phone_number,
        }
        firelog.info(LogStr.GET_USER_BY_PHONE_ATTEMPT_TEMPLATE, extra=log_extra_attempt)
        try:
            db_user = self._repository.get_by_phone_number(
                db=db, phone_number=phone_number
            )
            log_extra_success = {
                "service_name": self._SERVICE_NAME,
                "phone_number": phone_number,
            }
            firelog.info(
                LogStr.GET_USER_BY_PHONE_SUCCESS_TEMPLATE, extra=log_extra_success
            )
            return db_user
        except NoResultFound:
            log_and_raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=UserHttpErrorDetails.USER_NOT_FOUND_GENERIC,
                log_level=LogLevel.WARNING,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={"phone_number": phone_number},
            )

    def get_user_by_email(self, db: Session, email: str) -> User:
        _method_name = self.get_user_by_email.__name__
        log_extra_attempt = {"service_name": self._SERVICE_NAME, "email": email}
        firelog.info(LogStr.GET_USER_BY_EMAIL_ATTEMPT_TEMPLATE, extra=log_extra_attempt)
        try:
            db_user = self._repository.get_by_email(db=db, email=email)
            log_extra_success = {
                "service_name": self._SERVICE_NAME,
                "email": email,
            }
            firelog.info(
                LogStr.GET_USER_BY_EMAIL_SUCCESS_TEMPLATE, extra=log_extra_success
            )
            return db_user
        except NoResultFound:
            log_and_raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=UserHttpErrorDetails.USER_NOT_FOUND_GENERIC,
                log_level=LogLevel.WARNING,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={"email": email},
            )

    def get_users(self, db: Session, skip: int, limit: int) -> UsersPublic:
        _method_name = self.get_users.__name__
        log_extra_attempt = {
            "service_name": self._SERVICE_NAME,
            "skip": skip,
            "limit": limit,
        }
        firelog.info(LogStr.GET_USERS_ATTEMPT_TEMPLATE, extra=log_extra_attempt)
        try:
            users_from_db: Sequence[User] = self._repository.get_multi(
                db=db, skip=skip, limit=limit
            )
            count: int = self._repository.count(db=db)

            users_out_list = [UserPublic.model_validate(user) for user in users_from_db]
            result = UsersPublic(data=users_out_list, count=count)

            log_extra_success = {
                "service_name": self._SERVICE_NAME,
                "count": result.count,
            }
            firelog.info(LogStr.GET_USERS_SUCCESS_TEMPLATE, extra=log_extra_success)
            return result
        except Exception:
            log_and_raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching users.",
                log_level=LogLevel.ERROR,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                include_exc_info=True,
            )

    def create_user_via_otp(
        self, db: Session, otp_flow_payload: UserCreateInternal
    ) -> User:
        _method_name = self.create_user_via_otp.__name__
        phone = otp_flow_payload.phone_number
        log_extra_attempt = {"service_name": self._SERVICE_NAME, "phone_number": phone}
        firelog.info(LogStr.CREATE_OTP_USER_ATTEMPT_TEMPLATE, extra=log_extra_attempt)

        if self._repository.exists_by_phone_number(db=db, phone_number=phone):
            log_and_raise_http_exception(
                status_code=status.HTTP_409_CONFLICT,
                detail=UserHttpErrorDetails.PHONE_ALREADY_EXISTS_TEMPLATE % phone,
                log_level=LogLevel.WARNING,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={"phone_number": phone},
            )

        try:
            db_user = self._repository.create_user_for_otp_flow(
                db=db, phone_number=phone
            )
            log_extra_success = {
                "service_name": self._SERVICE_NAME,
                "user_id": db_user.id,
            }
            firelog.info(
                LogStr.CREATE_OTP_USER_SUCCESS_TEMPLATE, extra=log_extra_success
            )
            return db_user
        except Exception:
            log_and_raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UserHttpErrorDetails.USER_CREATION_FAILED,
                log_level=LogLevel.ERROR,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={"phone_number": phone},
                include_exc_info=True,
            )

    def complete_user_profile(
        self, db: Session, user_to_update: User, profile_in: UserCompleteProfile
    ) -> User:
        _method_name = self.complete_user_profile.__name__
        user_id = user_to_update.id
        log_extra_attempt = {"service_name": self._SERVICE_NAME, "user_id": user_id}
        firelog.info(LogStr.COMPLETE_PROFILE_ATTEMPT_TEMPLATE, extra=log_extra_attempt)

        if profile_in.email:
            try:
                if self._repository.exists_by_email(db=db, email=profile_in.email):
                    existing_user_with_email = self._repository.get_by_email(
                        db=db, email=profile_in.email
                    )
                    if existing_user_with_email.id != user_id:
                        log_and_raise_http_exception(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=UserHttpErrorDetails.EMAIL_ALREADY_EXISTS_TEMPLATE
                            % profile_in.email,
                            log_level=LogLevel.WARNING,
                            service_name=self._SERVICE_NAME,
                            method_name=_method_name,
                            additional_log_info={
                                "email": profile_in.email,
                                "current_user_id": user_id,
                            },
                        )
            except NoResultFound:
                pass

        try:
            updated_user = self._repository.update_user_profile_completion(
                db=db, db_user_to_update=user_to_update, profile_data=profile_in
            )
            log_extra_success = {
                "service_name": self._SERVICE_NAME,
                "user_id": updated_user.id,
            }
            firelog.info(
                LogStr.COMPLETE_PROFILE_SUCCESS_TEMPLATE, extra=log_extra_success
            )
            return updated_user
        except Exception:
            log_and_raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UserHttpErrorDetails.PROFILE_COMPLETION_FAILED,
                log_level=LogLevel.ERROR,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={"user_id": user_id},
                include_exc_info=True,
            )

    def _authorize_user_update(
        self,
        db_user_to_update: User,
        current_user: User,
        method_name: str,
    ) -> None:
        """Checks if the current user is authorized to update the target user."""
        if db_user_to_update.id != current_user.id and not current_user.is_superuser:
            log_and_raise_http_exception(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=UserHttpErrorDetails.NOT_AUTHORIZED_TO_UPDATE_USER,
                log_level=LogLevel.WARNING,
                service_name=self._SERVICE_NAME,
                method_name=method_name,
                additional_log_info={
                    "current_user_id": current_user.id,
                    "target_user_id": db_user_to_update.id,
                },
            )

    def _check_field_uniqueness(
        self,
        db: Session,
        field_name: str,
        field_value: str | None,
        current_field_value: str | None,
        user_id_to_update: int,
        error_detail_template: str,
        method_name: str,
    ) -> None:
        if not field_value or field_value == current_field_value:
            return

        try:
            if field_name == "phone_number":
                exists_method = self._repository.exists_by_phone_number
                get_method = self._repository.get_by_phone_number
            elif field_name == "email":
                exists_method = self._repository.exists_by_email
                get_method = self._repository.get_by_email
            else:
                firelog.error(
                    LogStr.UNSUPPORTED_FIELD,
                    extra={
                        "service_name": self._SERVICE_NAME,
                        "field_name": field_name,
                    },
                )
                return

            if exists_method(db=db, **{field_name: field_value}):
                existing_user = get_method(db=db, **{field_name: field_value})
                if existing_user.id != user_id_to_update:
                    log_and_raise_http_exception(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=error_detail_template,
                        log_level=LogLevel.WARNING,
                        service_name=self._SERVICE_NAME,
                        method_name=method_name,
                        additional_log_info={
                            field_name: field_value,
                            "target_user_id": user_id_to_update,
                        },
                    )
        except NoResultFound:
            pass
        except Exception:
            firelog.error(
                LogStr.ERROR_FIELD_UNIQUENESS,
                exc_info=True,
                extra={
                    "service_name": self._SERVICE_NAME,
                    "field_name": field_name,
                    "user_id_to_update": user_id_to_update,
                },
            )
            log_and_raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error checking {field_name} uniqueness.",
                log_level=LogLevel.ERROR,
                service_name=self._SERVICE_NAME,
                method_name=method_name,
                include_exc_info=True,
            )

    def update_user_details(
        self,
        db: Session,
        user_id_to_update: int,
        user_in: UserUpdate,
        current_user: User,
    ) -> User:
        _method_name = self.update_user_details.__name__
        log_extra_attempt = {
            "service_name": self._SERVICE_NAME,
            "current_user_id": current_user.id,
            "target_user_id": user_id_to_update,
        }
        firelog.info(LogStr.UPDATE_USER_ATTEMPT_TEMPLATE, extra=log_extra_attempt)

        db_user_to_update = self.get_user_by_id(db=db, user_id=user_id_to_update)

        self._authorize_user_update(
            db_user_to_update=db_user_to_update,
            current_user=current_user,
            method_name=_method_name,
        )

        self._check_field_uniqueness(
            db=db,
            field_name="phone_number",
            field_value=user_in.phone_number,
            current_field_value=db_user_to_update.phone_number,
            user_id_to_update=user_id_to_update,
            error_detail_template=UserHttpErrorDetails.PHONE_ALREADY_IN_USE,
            method_name=_method_name,
        )

        self._check_field_uniqueness(
            db=db,
            field_name="email",
            field_value=user_in.email,
            current_field_value=db_user_to_update.email,
            user_id_to_update=user_id_to_update,
            error_detail_template=UserHttpErrorDetails.EMAIL_ALREADY_IN_USE,
            method_name=_method_name,
        )

        try:
            update_data = user_in.model_dump(exclude_unset=True)
            if not update_data:
                firelog.info(
                    LogStr.NO_UPDATE_DATA,
                    extra={
                        "service_name": self._SERVICE_NAME,
                        "user_id_to_update": user_id_to_update,
                    },
                )
                return db_user_to_update

            updated_user = self._repository.update(
                db=db,
                db_obj_to_update=db_user_to_update,
                obj_in=user_in,
            )

            if not updated_user:
                log_and_raise_http_exception(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=UserHttpErrorDetails.USER_UPDATE_FAILED,
                    log_level=LogLevel.ERROR,
                    service_name=self._SERVICE_NAME,
                    method_name=_method_name,
                    additional_log_info={
                        "target_user_id": user_id_to_update,
                        "reason": "Repository update returned no object or failed silently.",
                    },
                )

            log_extra_success = {
                "service_name": self._SERVICE_NAME,
                "target_user_id": updated_user.id,
                "current_user_id": current_user.id,
            }
            firelog.info(LogStr.UPDATE_USER_SUCCESS_TEMPLATE, extra=log_extra_success)
            return updated_user
        except Exception as e:
            firelog.error(
                LogStr.FAILED_TO_UPDATE_USER,
                exc_info=True,
                extra={
                    "service_name": self._SERVICE_NAME,
                    "user_id_to_update": user_id_to_update,
                },
            )
            log_and_raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UserHttpErrorDetails.USER_UPDATE_FAILED,
                log_level=LogLevel.ERROR,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={
                    "target_user_id": user_id_to_update,
                    "error": str(e),
                },
                include_exc_info=True,
            )

    def remove_user(
        self, db: Session, user_id_to_delete: int, current_user: User
    ) -> bool:
        _method_name = self.remove_user.__name__
        log_extra_attempt = {
            "service_name": self._SERVICE_NAME,
            "current_user_id": current_user.id,
            "target_user_id": user_id_to_delete,
        }
        firelog.info(LogStr.REMOVE_USER_ATTEMPT_TEMPLATE, extra=log_extra_attempt)

        user_to_delete = self.get_user_by_id(db=db, user_id=user_id_to_delete)
        is_self_delete = user_to_delete.id == current_user.id

        if is_self_delete:
            if current_user.is_superuser:
                log_and_raise_http_exception(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=UserHttpErrorDetails.SUPERUSER_SELF_DELETE_NOT_ALLOWED,
                    log_level=LogLevel.WARNING,
                    service_name=self._SERVICE_NAME,
                    method_name=_method_name,
                    additional_log_info={"current_user_id": current_user.id},
                )
        elif not current_user.is_superuser:
            log_and_raise_http_exception(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=UserHttpErrorDetails.FORBIDDEN_DELETE_USER,
                log_level=LogLevel.WARNING,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={
                    "current_user_id": current_user.id,
                    "target_user_id": user_id_to_delete,
                },
            )

        try:
            deleted_user_from_repo = self._repository.delete(
                db=db, id=user_id_to_delete
            )
            if not deleted_user_from_repo:
                log_and_raise_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE.format(
                        user_id=user_id_to_delete
                    ),
                    log_level=LogLevel.WARNING,
                    service_name=self._SERVICE_NAME,
                    method_name=_method_name,
                    additional_log_info={
                        "target_user_id": user_id_to_delete,
                        "reason": "Repository delete returned None/False",
                    },
                )
            firelog.info(LogStr.REMOVE_USER_SUCCESS_TEMPLATE, extra=log_extra_attempt)
            return True
        except NoResultFound:
            log_and_raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=UserHttpErrorDetails.USER_NOT_FOUND_TEMPLATE.format(
                    user_id=user_id_to_delete
                ),
                log_level=LogLevel.WARNING,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={"target_user_id": user_id_to_delete},
            )
        except Exception:
            log_and_raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UserHttpErrorDetails.USER_DELETE_ERROR,
                log_level=LogLevel.ERROR,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={"target_user_id": user_id_to_delete},
                include_exc_info=True,
            )

    def update_user_last_login(self, db: Session, user_to_update: User) -> User:
        _method_name = self.update_user_last_login.__name__
        user_id = user_to_update.id
        log_extra = {"service_name": self._SERVICE_NAME, "user_id": user_id}
        firelog.info(LogStr.UPDATE_LAST_LOGIN_ATTEMPT_TEMPLATE, extra=log_extra)
        try:
            updated_user = self._repository.update_last_login_at(
                db=db, user_to_update=user_to_update
            )
            log_extra_success = {**log_extra, "user_id": updated_user.id}
            firelog.info(
                LogStr.UPDATE_LAST_LOGIN_SUCCESS_TEMPLATE, extra=log_extra_success
            )
            return updated_user
        except Exception:
            log_and_raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UserHttpErrorDetails.UPDATE_LAST_LOGIN_ERROR,
                log_level=LogLevel.ERROR,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={"user_id": user_id},
                include_exc_info=True,
            )

    def set_user_active_status(
        self, db: Session, user_to_update: User, is_active: bool
    ) -> User:
        _method_name = self.set_user_active_status.__name__
        user_id = user_to_update.id
        log_extra_attempt = {
            "service_name": self._SERVICE_NAME,
            "is_active": is_active,
            "user_id": user_id,
        }
        firelog.info(LogStr.SET_ACTIVE_STATUS_ATTEMPT_TEMPLATE, extra=log_extra_attempt)
        try:
            updated_user = self._repository.set_active_status(
                db=db, user_to_update=user_to_update, is_active=is_active
            )
            log_extra_success = {
                "service_name": self._SERVICE_NAME,
                "is_active": updated_user.is_active,
                "user_id": updated_user.id,
            }
            firelog.info(
                LogStr.SET_ACTIVE_STATUS_SUCCESS_TEMPLATE, extra=log_extra_success
            )
            return updated_user
        except Exception:
            log_and_raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UserHttpErrorDetails.SET_ACTIVE_STATUS_ERROR,
                log_level=LogLevel.ERROR,
                service_name=self._SERVICE_NAME,
                method_name=_method_name,
                additional_log_info={"user_id": user_id, "target_status": is_active},
                include_exc_info=True,
            )
