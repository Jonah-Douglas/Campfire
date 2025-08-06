# In a dependencies.py or similar
from typing import Annotated

from fastapi import Depends

from app.users.repositories.user_repository import UserRepository


def get_user_repository() -> UserRepository:
    return UserRepository()


UserRepoDependency = Annotated[UserRepository, Depends(get_user_repository)]
