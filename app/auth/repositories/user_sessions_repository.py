from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import delete, select, update as sa_update
from sqlalchemy.orm import Session

from app.auth.constants import (
    UserSessionModelConstants,
    UserSessionRepoMessages as RepoMsg,
)
from app.auth.models.user_session_model import UserSession
from app.core.constants.repository_outcomes import GeneralLogs
from app.core.logging_config import firelog
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
        firelog.debug(GeneralLogs.INIT_TEMPLATE.format(class_name=self._CLASS_NAME))

    def _get_jti_suffix(self, jti: str | None) -> str:
        """Helper to safely get the JTI suffix for logging."""
        if not jti:
            return "N/A"
        return jti[-6:]

    # --- Generic Overrides ---
    def create(self, db: Session, *, obj_in: _DummyUserSessionSchema) -> UserSession:
        _method_name = self.create.__name__
        log_message = (
            GeneralLogs.METHOD_ENTRY_TEMPLATE.format(
                class_name=self._CLASS_NAME, method_name=_method_name
            )
            + " - Operation explicitly not implemented for UserSession."
        )
        firelog.warning(log_message)
        raise NotImplementedError(
            GeneralLogs.GENERIC_CREATE_NOT_IMPLEMENTED.format(
                model_name=self._MODEL_NAME
            )
        )

    def update(
        self,
        db: Session,
        *,
        db_obj_to_update: UserSession,
        obj_in: _DummyUserSessionSchema,
    ) -> UserSession:
        _method_name = self.update.__name__
        session_id = self._get_record_id(db_obj_to_update)
        jti_suffix = self._get_jti_suffix(
            getattr(db_obj_to_update, "refresh_token_jti", None)
        )

        log_message = (
            GeneralLogs.METHOD_ENTRY_TEMPLATE.format(
                class_name=self._CLASS_NAME, method_name=_method_name
            )
            + f" - Operation explicitly not implemented for {self._MODEL_NAME} ID: {session_id}, JTI Suffix: {jti_suffix}"
        )
        firelog.warning(log_message)
        raise NotImplementedError(
            GeneralLogs.GENERIC_UPDATE_NOT_IMPLEMENTED.format(
                model_name=self._MODEL_NAME
            )
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
        firelog.info(RepoMsg.CREATING.format(user_id=user_id, jti_suffix=jti_suffix))

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
            firelog.info(
                RepoMsg.CREATED_SUCCESS.format(
                    session_id=created_session.id,
                    user_id=created_session.user_id,
                    jti_suffix=log_jti_suffix,
                )
            )

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
        firelog.info(RepoMsg.GET_BY_JTI.format(jti_suffix=jti_suffix))

        try:
            statement = select(self.model).where(
                self.model.refresh_token_jti == refresh_token_jti
            )
            session_obj = db.execute(statement).scalar_one_or_none()

            if session_obj:
                firelog.info(
                    RepoMsg.FOUND_BY_JTI.format(
                        session_id=session_obj.id, jti_suffix=jti_suffix
                    )
                )
            else:
                firelog.info(RepoMsg.NOT_FOUND_BY_JTI.format(jti_suffix=jti_suffix))
            return session_obj
        except Exception as e:
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE.format(
                    class_name=self._CLASS_NAME,
                    method_name=_method_name,
                    model_name=self._MODEL_NAME,
                    error=str(e),
                ),
                exc_info=True,
            )
            raise

    def get_active_session_by_jti_and_user(
        self, db: Session, *, refresh_token_jti: str, user_id: int
    ) -> UserSession | None:
        _method_name = self.get_active_session_by_jti_and_user.__name__
        jti_suffix = self._get_jti_suffix(refresh_token_jti)
        firelog.info(
            RepoMsg.GET_ACTIVE_BY_JTI_USER.format(
                user_id=user_id, jti_suffix=jti_suffix
            )
        )
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
                firelog.info(
                    RepoMsg.ACTIVE_FOUND_BY_JTI_USER.format(
                        session_id=session_obj.id,
                        user_id=user_id,
                        jti_suffix=jti_suffix,
                    )
                )
            else:
                firelog.info(
                    RepoMsg.ACTIVE_NOT_FOUND_BY_JTI_USER.format(
                        user_id=user_id, jti_suffix=jti_suffix
                    )
                )
            return session_obj
        except Exception as e:
            firelog.error(
                GeneralLogs.METHOD_ERROR_TEMPLATE.format(
                    class_name=self._CLASS_NAME,
                    method_name=_method_name,
                    model_name=self._MODEL_NAME,
                    error=str(e),
                ),
                exc_info=True,
            )
            raise

    def invalidate_session(
        self, db: Session, *, session_to_invalidate: UserSession
    ) -> UserSession:
        _method_name = self.invalidate_session.__name__
        session_id = session_to_invalidate.id
        user_id = session_to_invalidate.user_id
        jti_suffix = self._get_jti_suffix(session_to_invalidate.refresh_token_jti)

        firelog.info(
            RepoMsg.INVALIDATING.format(
                session_id=session_id, user_id=user_id, jti_suffix=jti_suffix
            )
        )

        session_to_invalidate.is_active = False
        session_to_invalidate.expires_at = datetime.now(UTC)

        def _success_log(invalidated_session: UserSession) -> None:
            log_session_id = invalidated_session.id
            log_user_id = invalidated_session.user_id
            log_jti_suffix = self._get_jti_suffix(invalidated_session.refresh_token_jti)
            firelog.info(
                RepoMsg.INVALIDATED_SUCCESS.format(
                    session_id=log_session_id,
                    user_id=log_user_id,
                    jti_suffix=log_jti_suffix,
                )
            )

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
        firelog.info(RepoMsg.INVALIDATING_BY_JTI.format(jti_suffix=jti_suffix))

        user_session_obj = self.get_session_by_jti(
            db=db, refresh_token_jti=refresh_token_jti
        )

        if user_session_obj:
            if not user_session_obj.is_active:
                firelog.info(
                    RepoMsg.INVALIDATE_BY_JTI_NOT_FOUND.format(
                        session_id=user_session_obj.id, jti_suffix=jti_suffix
                    )
                )
                return user_session_obj
            return self.invalidate_session(
                db=db, session_to_invalidate=user_session_obj
            )
        else:
            firelog.warning(
                RepoMsg.INVALIDATE_BY_JTI_NOT_FOUND.format(jti_suffix=jti_suffix)
            )
            return None

    def invalidate_all_sessions_for_user(
        self, db: Session, *, user_id: int, exclude_jti: str | None = None
    ) -> int:
        _method_name = self.invalidate_all_sessions_for_user.__name__
        excluded_jti_suffix = self._get_jti_suffix(exclude_jti)
        firelog.info(
            RepoMsg.INVALIDATING_ALL_FOR_USER.format(
                user_id=user_id, excluded_jti_suffix=excluded_jti_suffix
            )
        )
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

            if count > 0:
                firelog.info(
                    RepoMsg.INVALIDATED_ALL_SUCCESS_COUNT.format(
                        count=count,
                        user_id=user_id,
                        excluded_jti_suffix=excluded_jti_suffix,
                    )
                )
            else:
                firelog.info(
                    RepoMsg.INVALIDATE_ALL_NONE_FOUND.format(
                        user_id=user_id, excluded_jti_suffix=excluded_jti_suffix
                    )
                )
            return count
        except Exception as e:
            db.rollback()
            firelog.error(
                RepoMsg.INVALIDATE_ALL_FAILED.format(
                    user_id=user_id,
                    excluded_jti_suffix=excluded_jti_suffix,
                    error=str(e),
                ),
                exc_info=True,
            )
            raise

    def cleanup_revoked_and_expired_sessions(self, db: Session) -> int:
        _method_name = self.cleanup_revoked_and_expired_sessions.__name__
        firelog.info(RepoMsg.CLEANUP_STARTED.format(model_name=self._MODEL_NAME))
        now = datetime.now(UTC)

        try:
            delete_statement = delete(self.model).where(
                (self.model.is_active == False) | (self.model.expires_at < now)  # noqa: E712
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
                    model_name=self._MODEL_NAME, error=str(e)
                ),
                exc_info=True,
            )
            raise
