from typing import Any

import inflection
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column


@as_declarative()
class Base:
    """
    Base class which provides automated table name
    and common columns for all inherited models.
    """

    __name__: str

    @declared_attr
    def __tablename__(cls) -> Any:  # noqa: N805, ANN401
        # Convert CamelCase class name to snake_case
        snake_case_name = inflection.underscore(cls.__name__)
        # Pluralize the snake_case name
        plural_snake_case_name = inflection.pluralize(snake_case_name)
        return plural_snake_case_name

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # JD TODO: Consider if I want these on all tables- not necessarily a bad idea
    # created_at: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True), server_default=sqlfunc.now(), nullable=False
    # )
    # updated_at: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True),
    #     server_default=sqlfunc.now(),
    #     onupdate=sqlfunc.now(), # Note: onupdate behavior is DB-dependent
    #     nullable=False
    # )
