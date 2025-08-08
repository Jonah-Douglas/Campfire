from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import delete, select, update as sa_update
from sqlalchemy.orm import Session

from app.auth.constants import (
    UserSessionRepoMessages as RepoMsg,
)
from app.auth.constants.repository_outcomes import UserSessionModelConstants
from app.auth.models.user_session_model import UserSession
from app.core.constants.repository_outcomes import GeneralLogs
from app.core.logging.logger_wrapper import firelog
from app.core.repositories.base_repository import BaseRepository


class _DummyUserSessionSchema(BaseModel):
    pass


class UserSessionRepository(
    BaseRepository[UserSession, _DummyUserSessionSchema, _DummyUserSessionSchema]
):
    _CLASS_NAME = __qualname__
    _MODEL_NAME = UserSessionModelConstants.MODEL_NAME

    def __init__(self) -> None:
        super().__init__(UserSession)
        log_extra = {"model_name": self._MODEL_NAME}
        firelog.debug(GeneralLogs.INIT_TEMPLATE, log_extra)

    def _get_jti_suffix(self, jti: str | None) -> str:
        """Helper to safely get the JTI suffix for logging."""
        if not jti:
            return "N/A"
        return jti[-6:]

    # --- Generic Overrides ---
    def create(self, db: Session, *, obj_in: _DummyUserSessionSchema) -> UserSession:
        _method_name = self.create.__name__
        firelog.debug(GeneralLogs.GENERIC_CREATE_NOT_IMPLEMENTED % self._CLASS_NAME)
        raise NotImplementedError(
            GeneralLogs.GENERIC_CREATE_NOT_IMPLEMENTED % self._CLASS_NAME
        )

    def update(
        self,
        db: Session,
        *,
        db_obj_to_update: UserSession,
        obj_in: _DummyUserSessionSchema,
    ) -> UserSession:
        _method_name = self.update.__name__
        firelog.debug(GeneralLogs.GENERIC_UPDATE_NOT_IMPLEMENTED % self._CLASS_NAME)
        raise NotImplementedError(
            GeneralLogs.GENERIC_UPDATE_NOT_IMPLEMENTED % self._CLASS_NAME
        )

    # --- Custom Methods ---
    def create_user_session(
        self,
        db: Session,
        *,
        user_id: int,
        refresh_token_jti: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> UserSession:
        _method_name = self.create_user_session.__name__
        jti_suffix = self._get_jti_suffix(refresh_token_jti)

        log_extra_creating = {
            "user_id": user_id,
            "jti_suffix": jti_suffix,
        }
        firelog.info(RepoMsg.CREATING, extra=log_extra_creating)

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)

        db_user_session_data = {
            "user_id": user_id,
            "refresh_token_jti": refresh_token_jti,
            "expires_at": expires_at,
            "user_agent": user_agent,
            "ip_address": ip_address,
            "is_active": True,
        }
        db_session_obj = self.model(**db_user_session_data)

        def _success_log(created_session: UserSession) -> None:
            log_jti_suffix = self._get_jti_suffix(created_session.refresh_token_jti)
            log_extra_success = {
                "session_id": created_session.id,
                "user_id": created_session.user_id,
                "jti_suffix": log_jti_suffix,
            }
            firelog.info(RepoMsg.CREATED_SUCCESS, extra=log_extra_success)

        return self._execute_commit_refresh_log(
            db=db,
            db_object=db_session_obj,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="user session creation",
        )

    def get_session_by_jti(
        self, db: Session, *, refresh_token_jti: str
    ) -> UserSession | None:
        _method_name = self.get_session_by_jti.__name__
        jti_suffix = self._get_jti_suffix(refresh_token_jti)

        log_extra_jti = {"jti_suffix": jti_suffix}
        firelog.info(RepoMsg.GET_BY_JTI, extra=log_extra_jti)

        try:
            statement = select(self.model).where(
                self.model.refresh_token_jti == refresh_token_jti
            )
            session_obj = db.execute(statement).scalar_one_or_none()

            if session_obj:
                log_extra_found = {
                    "session_id": session_obj.id,
                    "jti_suffix": jti_suffix,
                }
                firelog.info(RepoMsg.FOUND_BY_JTI, extra=log_extra_found)
            else:
                firelog.info(RepoMsg.NOT_FOUND_BY_JTI, extra=log_extra_jti)
            return session_obj
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

    def get_active_session_by_jti_and_user(
        self, db: Session, *, refresh_token_jti: str, user_id: int
    ) -> UserSession | None:
        _method_name = self.get_active_session_by_jti_and_user.__name__
        jti_suffix = self._get_jti_suffix(refresh_token_jti)

        log_extra_get_active = {
            "user_id": user_id,
            "jti_suffix": jti_suffix,
        }
        firelog.info(RepoMsg.GET_ACTIVE_BY_JTI_USER, extra=log_extra_get_active)
        try:
            statement = (
                select(self.model)
                .where(self.model.refresh_token_jti == refresh_token_jti)
                .where(self.model.user_id == user_id)
                .where(self.model.is_active)
                .where(self.model.expires_at > datetime.now(UTC))
            )
            session_obj = db.execute(statement).scalar_one_or_none()
            if session_obj:
                log_extra_active_found = {
                    "session_id": session_obj.id,
                    "user_id": user_id,
                    "jti_suffix": jti_suffix,
                }
                firelog.info(
                    RepoMsg.ACTIVE_FOUND_BY_JTI_USER, extra=log_extra_active_found
                )
            else:
                firelog.info(
                    RepoMsg.ACTIVE_NOT_FOUND_BY_JTI_USER, extra=log_extra_get_active
                )
            return session_obj
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

    def invalidate_session(
        self, db: Session, *, session_to_invalidate: UserSession
    ) -> UserSession:
        _method_name = self.invalidate_session.__name__
        session_id = session_to_invalidate.id
        user_id = session_to_invalidate.user_id
        jti_suffix = self._get_jti_suffix(session_to_invalidate.refresh_token_jti)

        log_extra_invalidating = {
            "session_id": session_id,
            "user_id": user_id,
            "jti_suffix": jti_suffix,
        }
        firelog.info(RepoMsg.INVALIDATING, extra=log_extra_invalidating)

        session_to_invalidate.is_active = False
        session_to_invalidate.expires_at = datetime.now(UTC)

        def _success_log(invalidated_session: UserSession) -> None:
            log_extra_success = {
                "session_id": invalidated_session.id,
                "user_id": invalidated_session.user_id,
                "jti_suffix": self._get_jti_suffix(
                    invalidated_session.refresh_token_jti
                ),
            }
            firelog.info(RepoMsg.INVALIDATED_SUCCESS, extra=log_extra_success)

        return self._execute_commit_refresh_log(
            db=db,
            db_object=session_to_invalidate,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="user session invalidation",
        )

    def invalidate_session_by_jti(
        self, db: Session, *, refresh_token_jti: str
    ) -> UserSession | None:
        _method_name = self.invalidate_session_by_jti.__name__
        jti_suffix = self._get_jti_suffix(refresh_token_jti)

        log_extra_invalidate_jti = {"jti_suffix": jti_suffix}
        firelog.info(RepoMsg.INVALIDATING_BY_JTI, extra=log_extra_invalidate_jti)

        user_session_obj = self.get_session_by_jti(
            db=db, refresh_token_jti=refresh_token_jti
        )

        if user_session_obj:
            if not user_session_obj.is_active:
                log_extra_already_inactive = {
                    "jti_suffix": jti_suffix,
                    "session_id": user_session_obj.id,
                }
                firelog.info(
                    f"Session ID {user_session_obj.id} for JTI suffix {jti_suffix} is already inactive.",
                    extra=log_extra_already_inactive,
                )
                return user_session_obj  # Return the inactive session
            # If active, proceed to invalidate
            return self.invalidate_session(
                db=db, session_to_invalidate=user_session_obj
            )
        else:
            firelog.warning(
                RepoMsg.INVALIDATE_BY_JTI_NOT_FOUND, extra=log_extra_invalidate_jti
            )
            return None

    def invalidate_all_sessions_for_user(
        self, db: Session, *, user_id: int, exclude_jti: str | None = None
    ) -> int:
        _method_name = self.invalidate_all_sessions_for_user.__name__
        excluded_jti_suffix = self._get_jti_suffix(exclude_jti)

        log_extra_base = {
            "user_id": user_id,
            "excluded_jti_suffix": excluded_jti_suffix,
        }
        firelog.info(RepoMsg.INVALIDATING_ALL_FOR_USER, extra=log_extra_base)
        try:
            update_values = {"is_active": False, "expires_at": datetime.now(UTC)}
            statement = (
                sa_update(self.model)
                .where(self.model.user_id == user_id)
                .where(self.model.is_active)
            )
            if exclude_jti:
                statement = statement.where(self.model.refresh_token_jti != exclude_jti)

            statement = statement.values(**update_values)
            result = db.execute(statement)
            db.commit()
            count = result.rowcount

            log_extra_result = {**log_extra_base, "count": count}
            if count > 0:
                firelog.info(
                    RepoMsg.INVALIDATED_ALL_SUCCESS_COUNT, extra=log_extra_result
                )
            else:
                firelog.info(RepoMsg.INVALIDATE_ALL_NONE_FOUND, extra=log_extra_base)
            return count
        except Exception as e:
            db.rollback()
            log_extra_failed = {
                **log_extra_base,
                "error": str(e),
            }
            firelog.error(
                RepoMsg.INVALIDATE_ALL_FAILED, exc_info=e, extra=log_extra_failed
            )
            raise

    def cleanup_revoked_and_expired_sessions(self, db: Session) -> int:
        _method_name = self.cleanup_revoked_and_expired_sessions.__name__
        log_extra_start = {"model_name": self._MODEL_NAME}
        firelog.info(RepoMsg.CLEANUP_STARTED, extra=log_extra_start)

        now = datetime.now(UTC)

        try:
            delete_statement = delete(self.model).where(
                (self.model.is_active == False) | (self.model.expires_at < now)  # noqa: E712
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
                "model_name": self._MODEL_NAME,
                "error": str(e),
            }
            firelog.error(RepoMsg.CLEANUP_FAILED, exc_info=e, extra=log_extra_failed)
            raise
