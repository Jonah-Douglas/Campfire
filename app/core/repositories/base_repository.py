from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.constants import LoggingStrings
from app.core.logging.logger_wrapper import firelog
from app.db.base_class import Base

_ModelType = TypeVar("_ModelType", bound=Base)  # Type of the SQLAlchemy model
_CreateSchemaType = TypeVar(
    "_CreateSchemaType", bound=BaseModel
)  # Pydantic schema for creation
_UpdateSchemaType = TypeVar(
    "_UpdateSchemaType", bound=BaseModel
)  # Pydantic schema for updates


class BaseRepository[
    ModelType: Base,
    CreateSchemaType: BaseModel,
    UpdateSchemaType: BaseModel,
]:
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model
        self._CLASS_NAME = self.__class__.__qualname__
        self._MODEL_NAME = model.__name__

    def _get_record_id(self, db_object: ModelType) -> Any:  # noqa: ANN401
        return getattr(db_object, "id", "N/A (no id attribute)")

    def _execute_commit_refresh_log(
        self,
        db: Session,
        db_object: ModelType,
        calling_method_name: str,
        success_log_callback: Callable[[ModelType], None],
        operation_verb: str = "persistence",
    ) -> ModelType:
        record_id = self._get_record_id(db_object)
        log_context_base = {
            "model_name": self._MODEL_NAME,
            "record_id": record_id,
            "method_name": calling_method_name,
            "class_name": self._CLASS_NAME,
            "operation_verb": operation_verb,
        }
        try:
            db.add(db_object)
            db.commit()
            firelog.info(
                LoggingStrings.BaseRepoLogMessages.DB_COMMIT_SUCCESS_TEMPLATE,
                extra=log_context_base,
            )
            db.refresh(db_object)
            firelog.info(
                LoggingStrings.BaseRepoLogMessages.DB_REFRESH_SUCCESS_TEMPLATE,
                extra=log_context_base,
            )
            success_log_callback(db_object)
            return db_object
        except SQLAlchemyError as e:
            log_context_error = {**log_context_base, "error": str(e)}
            firelog.error(
                LoggingStrings.BaseRepoLogMessages.DB_OPERATION_ERROR_TEMPLATE,
                exc_info=True,
                extra=log_context_error,
            )
            try:
                db.rollback()
                firelog.warning(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_INVOKED_TEMPLATE,
                    extra=log_context_base,
                )
            except Exception as rb_exc:
                log_context_rollback_failure = {
                    **log_context_base,
                    "rollback_error": str(rb_exc),
                }
                firelog.critical(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_FAILURE_TEMPLATE,
                    exc_info=True,
                    extra=log_context_rollback_failure,
                )
            raise
        except Exception as e:
            log_context_unexpected_error = {**log_context_base, "error": str(e)}
            firelog.error(
                LoggingStrings.BaseRepo.UNEXPECTED_ERROR_DURING_OPERATION,
                exc_info=True,
                extra=log_context_unexpected_error,
            )
            try:
                if db.is_active:
                    db.rollback()
                    firelog.warning(
                        LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_INVOKED_TEMPLATE,
                        extra=log_context_base,
                    )
            except Exception as rb_exc:
                log_context_rollback_failure = {
                    **log_context_base,
                    "rollback_error": str(rb_exc),
                }
                firelog.critical(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_FAILURE_TEMPLATE,
                    exc_info=True,
                    extra=log_context_rollback_failure,
                )
            raise

    def _execute_commit_log_for_delete(
        self,
        db: Session,
        db_object_to_delete: ModelType,
        calling_method_name: str,
        success_log_callback: Callable[[ModelType], None],
        operation_verb: str = "deletion",
    ) -> ModelType:
        record_id = self._get_record_id(db_object_to_delete)
        log_context_base = {
            "model_name": self._MODEL_NAME,
            "record_id": record_id,
            "method_name": calling_method_name,
            "class_name": self._CLASS_NAME,
            "operation_verb": operation_verb,
        }
        try:
            db.delete(db_object_to_delete)
            db.commit()
            firelog.info(
                LoggingStrings.BaseRepoLogMessages.DB_COMMIT_SUCCESS_TEMPLATE,
                extra=log_context_base,
            )
            success_log_callback(db_object_to_delete)
            return db_object_to_delete
        except SQLAlchemyError as e:
            log_context_error = {**log_context_base, "error": str(e)}
            firelog.error(
                LoggingStrings.BaseRepoLogMessages.DB_OPERATION_ERROR_TEMPLATE,
                exc_info=True,
                extra=log_context_error,
            )
            try:
                db.rollback()
                firelog.warning(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_INVOKED_TEMPLATE,
                    extra=log_context_base,
                )
            except Exception as rb_exc:
                log_context_rollback_failure = {
                    **log_context_base,
                    "rollback_error": str(rb_exc),
                }
                firelog.critical(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_FAILURE_TEMPLATE,
                    exc_info=True,
                    extra=log_context_rollback_failure,
                )
            raise
        except Exception as e:
            log_context_unexpected_error = {**log_context_base, "error": str(e)}
            firelog.error(
                LoggingStrings.BaseRepo.UNEXPECTED_ERROR_DURING_OPERATION,
                exc_info=True,
                extra=log_context_unexpected_error,
            )
            try:
                if db.is_active:
                    db.rollback()
                    firelog.warning(
                        LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_INVOKED_TEMPLATE,
                        extra=log_context_base,
                    )
            except Exception as rb_exc:
                log_context_rollback_failure = {
                    **log_context_base,
                    "rollback_error": str(rb_exc),
                }
                firelog.critical(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_FAILURE_TEMPLATE,
                    exc_info=True,
                    extra=log_context_rollback_failure,
                )
            raise

    def get(self, db: Session, id: Any) -> ModelType:  # noqa: ANN401
        log_extra_get = {"model_name": self._MODEL_NAME, "id": id}
        firelog.debug(LoggingStrings.BaseRepo.GET_BY_ID_ATTEMPT, extra=log_extra_get)

        obj: ModelType | None = db.get(self.model, id)
        if obj is None:
            firelog.warning(
                LoggingStrings.BaseRepo.GET_BY_ID_NOT_FOUND, extra=log_extra_get
            )
            raise NoResultFound(
                LoggingStrings.BaseRepo.ENTITY_NOT_FOUND_BY_ID_TEMPLATE % log_extra_get
            )
        firelog.debug(LoggingStrings.BaseRepo.GET_BY_ID_SUCCESS, extra=log_extra_get)
        return obj

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        log_extra_multi_attempt = {
            "model_name": self._MODEL_NAME,
            "skip": skip,
            "limit": limit,
        }
        firelog.debug(
            LoggingStrings.BaseRepo.GET_MULTI_ATTEMPT, extra=log_extra_multi_attempt
        )
        try:
            # Attempt to use 'id' for ordering
            order_by_attr = getattr(self.model, "id", None)
            if order_by_attr is not None:
                statement = (
                    select(self.model).order_by(order_by_attr).offset(skip).limit(limit)
                )
            else:  # Fallback if no 'id' attribute
                statement = select(self.model).offset(skip).limit(limit)
                firelog.debug(
                    LoggingStrings.BaseRepo.MODEL_MISSING_ID_FOR_ORDERING,
                    extra={"model_name": self._MODEL_NAME},
                )
        except AttributeError:
            statement = select(self.model).offset(skip).limit(limit)
            firelog.warning(
                LoggingStrings.BaseRepo.MODEL_MISSING_ID_FOR_ORDERING,
                extra={"model_name": self._MODEL_NAME},
            )

        results = db.execute(statement).scalars().all()
        log_extra_multi_success = {
            "count": len(results),
            "model_name": self._MODEL_NAME,
        }
        firelog.debug(
            LoggingStrings.BaseRepo.GET_MULTI_SUCCESS, extra=log_extra_multi_success
        )
        return results

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        _method_name = self.create.__name__
        obj_in_data = obj_in.model_dump()
        data_preview = {
            k: str(v)[:50] + "..." if len(str(v)) > 50 else str(v)
            for k, v in list(obj_in_data.items())[:3]
        }

        log_extra_create_attempt = {
            "model_name": self._MODEL_NAME,
            "data_preview": data_preview,
        }
        firelog.info(
            LoggingStrings.BaseRepo.CREATE_ATTEMPT_WITH_PREVIEW,
            extra=log_extra_create_attempt,
        )

        db_obj = self.model(**obj_in_data)

        def _success_log(created_obj: ModelType) -> None:
            log_extra_create_success = {
                "model_name": self._MODEL_NAME,
                "record_id": self._get_record_id(created_obj),
            }
            firelog.info(
                LoggingStrings.BaseRepo.CREATE_SUCCESS_LOG,
                extra=log_extra_create_success,
            )

        return self._execute_commit_refresh_log(
            db=db,
            db_object=db_obj,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="creation",
        )

    def update(
        self,
        db: Session,
        *,
        db_obj_to_update: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        _method_name = self.update.__name__
        record_id = self._get_record_id(db_obj_to_update)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        data_preview = {
            k: str(v)[:50] + "..." if len(str(v)) > 50 else str(v)
            for k, v in list(update_data.items())[:3]
        }
        log_extra_update_attempt = {
            "model_name": self._MODEL_NAME,
            "record_id": record_id,
            "data_preview": data_preview,
        }
        firelog.info(
            LoggingStrings.BaseRepo.UPDATE_ATTEMPT_WITH_PREVIEW,
            extra=log_extra_update_attempt,
        )

        for field, value in update_data.items():
            if hasattr(db_obj_to_update, field):
                setattr(db_obj_to_update, field, value)
            else:
                log_extra_field_not_found = {
                    "field": field,
                    "model_name": self._MODEL_NAME,
                    "record_id": record_id,
                }
                firelog.warning(
                    LoggingStrings.BaseRepo.UPDATE_FIELD_NOT_FOUND,
                    extra=log_extra_field_not_found,
                )

        def _success_log(updated_obj: ModelType) -> None:
            log_extra_update_success = {
                "model_name": self._MODEL_NAME,
                "record_id": self._get_record_id(updated_obj),
            }
            firelog.info(
                LoggingStrings.BaseRepo.UPDATE_SUCCESS_LOG,
                extra=log_extra_update_success,
            )

        return self._execute_commit_refresh_log(
            db=db,
            db_object=db_obj_to_update,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="update",
        )

    def delete(self, db: Session, *, id: Any) -> ModelType:  # noqa: ANN401
        _method_name = self.delete.__name__
        log_extra_delete_attempt = {"model_name": self._MODEL_NAME, "record_id": id}
        firelog.info(
            LoggingStrings.BaseRepo.DELETE_ATTEMPT, extra=log_extra_delete_attempt
        )

        obj_to_delete = self.get(db=db, id=id)

        def _success_log(deleted_obj: ModelType) -> None:
            log_extra_delete_success = {
                "model_name": self._MODEL_NAME,
                "record_id": self._get_record_id(deleted_obj),
            }
            firelog.info(
                LoggingStrings.BaseRepo.DELETE_SUCCESS_LOG,
                extra=log_extra_delete_success,
            )

        return self._execute_commit_log_for_delete(
            db=db,
            db_object_to_delete=obj_to_delete,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="deletion",
        )

    def count(self, db: Session) -> int:
        log_extra_model_name = {"model_name": self._MODEL_NAME}
        firelog.debug(LoggingStrings.BaseRepo.COUNT_ATTEMPT, extra=log_extra_model_name)
        try:
            # Try to use 'id' for counting, common case
            count_col = getattr(self.model, "id", None)
            if count_col is not None:
                count_statement = select(func.count(count_col))
            else:  # Fallback if no 'id' attribute
                firelog.debug(
                    LoggingStrings.BaseRepo.MODEL_MISSING_ID_FOR_COUNT,
                    extra=log_extra_model_name,
                )
                count_statement = select(func.count()).select_from(self.model)
        except AttributeError:
            firelog.warning(
                LoggingStrings.BaseRepo.MODEL_MISSING_ID_FOR_COUNT,
                extra=log_extra_model_name,
            )
            count_statement = select(func.count()).select_from(self.model)

        result = db.execute(count_statement).scalar_one()
        log_extra_count_success = {
            "model_name": self._MODEL_NAME,
            "count": result,
        }
        firelog.debug(
            LoggingStrings.BaseRepo.COUNT_SUCCESS, extra=log_extra_count_success
        )
        return result
