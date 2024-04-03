# JD TODO: Create guest account logic
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import func, select
from api.dependencies import (
    CurrentUser,
    get_current_user,
    SessionDependency,
)
from models import (
    User,
    UserCreate,
    UserOut,
    UsersOut
)
from api.routes import utils


router = APIRouter()

# JD TODO: Lock this behind superuser privilege
@router.get("/", 
            dependencies=[Depends(get_current_user)],
            response_model=UsersOut
)
def read_users(session: SessionDependency, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersOut(data=users, count=count)


@router.get("/me", response_model=UserOut)
def read_user_me(session: SessionDependency, current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/",
             response_model=UserOut, 
)
def create_user(*, session: SessionDependency, user_in: UserCreate) -> Any:
    """
    Create new user from guest account.
    """

    user = utils.get_user_by_email(session=session, email = user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    user_create = UserCreate.model_validate(user_in)
    user = utils.create_user(session=session, user_create=user_create)
    return user