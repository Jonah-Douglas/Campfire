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
    Message,
    User,
    UserCreate,
    UserOut,
    UsersOut,
    UserUpdate,
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


@router.get("/{user_id}", response_model=UserOut)
def read_user_by_id(
    user_id: int, session: SessionDependency, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges.",
        )
    return user


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


@router.patch("/{user_id}", response_model=UserOut,)
def update_user(
    *,
    session: SessionDependency,
    user_id: int,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="The user with this id does not exist.",
        )
    if user_in.email:
        existing_user = utils.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists."
            )
    
    user = utils.update_user(session=session, user=user, user_in=user_in)
    return user


@router.delete("/{user_id}")
def delete_user(
    session: SessionDependency,
    current_user: CurrentUser,
    user_id: int,
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    elif user != current_user and not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges."
        )
    # JD TODO: add check for superuser deleting self once this is added

    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully.")