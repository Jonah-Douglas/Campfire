from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import CurrentUser, SessionDependency
from app.models.user import UserCreate, UserOut, UsersOut, UserUpdate
from app.services.user_service import UserService


router = APIRouter()

# JD TODO: Create guest account logic
# JD TODO: Lock this behind superuser privilege - This should be handled by a dependency or in the service.

@router.get("/", 
            response_model=UsersOut
)
def read_users(
    session: SessionDependency,
    current_user: CurrentUser,
    user_service: UserService = Depends(UserService), # Inject UserService
    skip: int = 0, 
    limit: int = 100
) -> UsersOut:
    """
    Retrieve users.
    Requires superuser privileges.
    """
    # Authorization check should be here or in the service layer
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )
    return user_service.get_users(db=session, skip=skip, limit=limit)


@router.get("/me", response_model=UserOut)
def read_user_me(
    current_user: CurrentUser
) -> UserOut:
    """
    Get current user.
    """

    return UserOut.model_validate(current_user)


@router.get("/{user_id}", response_model=UserOut)
def read_user_by_id(
    user_id: int,
    session: SessionDependency,
    current_user: CurrentUser,
    user_service: UserService = Depends(UserService) # Inject UserService
) -> UserOut:
    """
    Get a specific user by id.
    """
    # Authorization: current_user can see self, or if current_user is_superuser (or some other role)
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this user.",
        )

    user = user_service.get_user_by_id(db=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found."
        )
    return UserOut.model_validate(user)


@router.post("/", response_model=UserOut)
def create_user(
    user_in: UserCreate,
    session: SessionDependency,
    user_service: UserService = Depends(UserService) # Inject UserService
) -> UserOut:
    """
    Create new user.
    (Consider if this endpoint is for public registration or admin creation)
    """

    new_user = user_service.create_new_user(db=session, user_in=user_in)
    return UserOut.model_validate(new_user)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    session: SessionDependency,
    current_user: CurrentUser,
    user_service: UserService = Depends(UserService) # Inject UserService
) -> UserOut:
    """
    Update a user. Users can update themselves. Superusers can update others.
    """

    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this user."
        )

    updated_user = user_service.update_existing_user(
        db=session, user_id=user_id, user_in=user_in
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this id does not exist.",
        )
    
    return UserOut.model_validate(updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: SessionDependency,
    current_user: CurrentUser,
    user_service: UserService = Depends(UserService) # Inject UserService
) -> None:
    """
    Delete a user.
    Users can delete themselves. Superusers can delete others (except themselves via this endpoint).
    """

    deleted = user_service.remove_user(db=session, user_id=user_id, current_user=current_user)
    if not deleted:
        # This case means the user wasn't found, which the service handles by returning False.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or could not be deleted." 
        )
    return