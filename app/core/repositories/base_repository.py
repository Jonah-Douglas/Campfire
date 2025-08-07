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
        try:
            db.add(db_object)
            db.commit()
            firelog.info(
                LoggingStrings.BaseRepoLogMessages.DB_COMMIT_SUCCESS_TEMPLATE.format(
                    model_name=self._MODEL_NAME,
                    record_id=record_id,
                    method_name=calling_method_name,
                )
            )
            db.refresh(db_object)
            firelog.info(
                LoggingStrings.BaseRepoLogMessages.DB_REFRESH_SUCCESS_TEMPLATE.format(
                    model_name=self._MODEL_NAME,
                    record_id=record_id,
                    method_name=calling_method_name,
                )
            )
            success_log_callback(db_object)
            return db_object
        except SQLAlchemyError as e:
            firelog.error(
                LoggingStrings.BaseRepoLogMessages.DB_OPERATION_ERROR_TEMPLATE.format(
                    operation_verb=operation_verb,
                    model_name=self._MODEL_NAME,
                    class_name=self._CLASS_NAME,
                    method_name=calling_method_name,
                    error=str(e),
                ),
                exc_info=True,
            )
            try:
                db.rollback()
                firelog.warning(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_INVOKED_TEMPLATE.format(
                        method_name=calling_method_name, model_name=self._MODEL_NAME
                    )
                )
            except Exception as rb_exc:
                firelog.critical(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_FAILURE_TEMPLATE.format(
                        class_name=self._CLASS_NAME,
                        method_name=calling_method_name,
                        model_name=self._MODEL_NAME,
                        rollback_error=str(rb_exc),
                    ),
                    exc_info=True,
                )
            raise
        except Exception as e:
            firelog.error(
                LoggingStrings.BaseRepo.UNEXPECTED_ERROR_DURING_OPERATION.format(
                    operation_verb=operation_verb,
                    class_name=self._CLASS_NAME,
                    method_name=calling_method_name,
                    model_name=self._MODEL_NAME,
                    error=str(e),
                ),
                exc_info=True,
            )
            try:
                if db.is_active:
                    db.rollback()
                    firelog.warning(
                        LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_INVOKED_TEMPLATE.format(
                            method_name=calling_method_name, model_name=self._MODEL_NAME
                        )
                    )
            except Exception as rb_exc:
                firelog.critical(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_FAILURE_TEMPLATE.format(
                        class_name=self._CLASS_NAME,
                        method_name=calling_method_name,
                        model_name=self._MODEL_NAME,
                        rollback_error=str(rb_exc),
                    ),
                    exc_info=True,
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
        try:
            db.delete(db_object_to_delete)
            db.commit()
            firelog.info(
                LoggingStrings.BaseRepoLogMessages.DB_COMMIT_SUCCESS_TEMPLATE.format(
                    model_name=self._MODEL_NAME,
                    record_id=record_id,
                    method_name=calling_method_name,
                )
            )
            success_log_callback(db_object_to_delete)
            return db_object_to_delete
        except SQLAlchemyError as e:
            firelog.error(
                LoggingStrings.BaseRepoLogMessages.DB_OPERATION_ERROR_TEMPLATE.format(
                    operation_verb=operation_verb,
                    model_name=self._MODEL_NAME,
                    class_name=self._CLASS_NAME,
                    method_name=calling_method_name,
                    error=str(e),
                ),
                exc_info=True,
            )
            try:
                db.rollback()
                firelog.warning(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_INVOKED_TEMPLATE.format(
                        method_name=calling_method_name, model_name=self._MODEL_NAME
                    )
                )
            except Exception as rb_exc:
                firelog.critical(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_FAILURE_TEMPLATE.format(
                        class_name=self._CLASS_NAME,
                        method_name=calling_method_name,
                        model_name=self._MODEL_NAME,
                        rollback_error=str(rb_exc),
                    ),
                    exc_info=True,
                )
            raise
        except Exception as e:
            firelog.error(
                LoggingStrings.BaseRepo.UNEXPECTED_ERROR_DURING_OPERATION.format(
                    operation_verb=operation_verb,
                    class_name=self._CLASS_NAME,
                    method_name=calling_method_name,
                    model_name=self._MODEL_NAME,
                    error=str(e),
                ),
                exc_info=True,
            )
            try:
                if db.is_active:
                    db.rollback()
                    firelog.warning(
                        LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_INVOKED_TEMPLATE.format(
                            method_name=calling_method_name, model_name=self._MODEL_NAME
                        )
                    )
            except Exception as rb_exc:
                firelog.critical(
                    LoggingStrings.BaseRepoLogMessages.DB_ROLLBACK_FAILURE_TEMPLATE.format(
                        class_name=self._CLASS_NAME,
                        method_name=calling_method_name,
                        model_name=self._MODEL_NAME,
                        rollback_error=str(rb_exc),
                    ),
                    exc_info=True,
                )
            raise

    def get(self, db: Session, id: Any) -> ModelType:  # noqa: ANN401
        firelog.debug(
            LoggingStrings.BaseRepo.GET_BY_ID_ATTEMPT.format(
                model_name=self._MODEL_NAME, id=id
            )
        )
        obj: ModelType | None = db.get(self.model, id)
        if obj is None:
            firelog.warning(
                LoggingStrings.BaseRepo.GET_BY_ID_NOT_FOUND.format(
                    model_name=self._MODEL_NAME, id=id
                )
            )
            raise NoResultFound(
                LoggingStrings.BaseRepo.ENTITY_NOT_FOUND_BY_ID_TEMPLATE.format(
                    model_name=self._MODEL_NAME, id=id
                )
            )
        firelog.debug(
            LoggingStrings.BaseRepo.GET_BY_ID_SUCCESS.format(
                model_name=self._MODEL_NAME, id=id
            )
        )
        return obj

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        firelog.debug(
            LoggingStrings.BaseRepo.GET_MULTI_ATTEMPT.format(
                model_name=self._MODEL_NAME, skip=skip, limit=limit
            )
        )
        try:
            order_by_attr = self.model.id
            statement = (
                select(self.model).order_by(order_by_attr).offset(skip).limit(limit)
            )
        except AttributeError:
            statement = select(self.model).offset(skip).limit(limit)
            firelog.debug(
                LoggingStrings.BaseRepo.MODEL_MISSING_ID_FOR_ORDERING.format(
                    model_name=self._MODEL_NAME
                )
            )

        results = db.execute(statement).scalars().all()
        firelog.debug(
            LoggingStrings.BaseRepo.GET_MULTI_SUCCESS.format(
                count=len(results), model_name=self._MODEL_NAME
            )
        )
        return results

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        _method_name = self.create.__name__
        obj_in_data = obj_in.model_dump()
        data_preview = {k: v for k, v in list(obj_in_data.items())[:3]}
        firelog.info(
            LoggingStrings.BaseRepo.CREATE_ATTEMPT_WITH_PREVIEW.format(
                model_name=self._MODEL_NAME, data_preview=data_preview
            )
        )
        db_obj = self.model(**obj_in_data)

        def _success_log(created_obj: ModelType) -> None:
            firelog.info(
                LoggingStrings.BaseRepo.CREATE_SUCCESS_LOG.format(
                    model_name=self._MODEL_NAME,
                    record_id=self._get_record_id(created_obj),
                )
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

        data_preview = {k: v for k, v in list(update_data.items())[:3]}
        firelog.info(
            LoggingStrings.BaseRepo.UPDATE_ATTEMPT_WITH_PREVIEW.format(
                model_name=self._MODEL_NAME,
                record_id=record_id,
                data_preview=data_preview,
            )
        )

        for field, value in update_data.items():
            if hasattr(db_obj_to_update, field):
                setattr(db_obj_to_update, field, value)
            else:
                firelog.warning(
                    LoggingStrings.BaseRepo.UPDATE_FIELD_NOT_FOUND.format(
                        field=field, model_name=self._MODEL_NAME, record_id=record_id
                    )
                )

        def _success_log(updated_obj: ModelType) -> None:
            firelog.info(
                LoggingStrings.BaseRepo.UPDATE_SUCCESS_LOG.format(
                    model_name=self._MODEL_NAME,
                    record_id=self._get_record_id(updated_obj),
                )
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
        firelog.info(
            LoggingStrings.BaseRepo.DELETE_ATTEMPT.format(
                model_name=self._MODEL_NAME, record_id=id
            )
        )

        obj_to_delete = self.get(db=db, id=id)

        def _success_log(deleted_obj: ModelType) -> None:
            firelog.info(
                LoggingStrings.BaseRepo.DELETE_SUCCESS_LOG.format(
                    model_name=self._MODEL_NAME,
                    record_id=self._get_record_id(deleted_obj),
                )
            )

        return self._execute_commit_log_for_delete(
            db=db,
            db_object_to_delete=obj_to_delete,
            calling_method_name=_method_name,
            success_log_callback=_success_log,
            operation_verb="deletion",
        )

    def count(self, db: Session) -> int:
        firelog.debug(
            LoggingStrings.BaseRepo.COUNT_ATTEMPT.format(model_name=self._MODEL_NAME)
        )
        try:
            count_col = self.model.id
            count_statement = select(func.count(count_col))
        except AttributeError:
            firelog.debug(
                LoggingStrings.BaseRepo.MODEL_MISSING_ID_FOR_COUNT.format(
                    model_name=self._MODEL_NAME
                )
            )
            count_statement = select(func.count()).select_from(self.model)

        result = db.execute(count_statement).scalar_one()
        firelog.debug(
            LoggingStrings.BaseRepo.COUNT_SUCCESS.format(
                model_name=self._MODEL_NAME, count=result
            )
        )
        return result
