# app/services/user_service.py

from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.user import User, UserCreate, UserOut, UserUpdate, UsersOut
from app.crud import crud_user


class UserService:
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return crud_user.get_user(db=db, user_id=user_id)

    def get_users(
        self, db: Session, skip: int, limit: int
    ) -> UsersOut:
        users = crud_user.get_users_multi(db=db, skip=skip, limit=limit)
        count = crud_user.count_users(db=db)
        return UsersOut(data=[UserOut.model_validate(user) for user in users], count=count)

    def create_new_user(self, db: Session, user_in: UserCreate) -> User:
        existing_user = crud_user.get_user_by_email(db=db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )
        user_create_validated = UserCreate.model_validate(user_in)
        new_user = crud_user.create_user(db=db, user_in=user_in)
        return new_user

    def update_existing_user(
        self, db: Session, user_id: int, user_in: UserUpdate
    ) -> Optional[User]:
        db_user = crud_user.get_user(db=db, user_id=user_id)
        if not db_user:
            return None

        if user_in.email:
            existing_user_with_email = crud_user.get_user_by_email(db=db, email=user_in.email)
            if existing_user_with_email and existing_user_with_email.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists."
                )
        
        updated_user = crud_user.update_user(db=db, db_user=db_user, user_in=user_in)
        return updated_user

    # JD TODO: Revisit this use case
    def remove_user(
        self, db: Session, user_id: int, current_user: User
    ) -> bool: # Returns True if deleted, False if not found
        user_to_delete = crud_user.get_user(db=db, user_id=user_id)
        if not user_to_delete:
            return False

        # Authorization logic:
        # JD TODO: Add check for superuser deleting self - this is complex, superuser should probably not delete self easily.
        # This authorization could also be more granular in a dedicated authorization service or policy.
        if user_to_delete.id != current_user.id and not current_user.is_superuser: # Assuming is_superuser field
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges to delete this user."
            )
        
        # Prevent users (even superusers for safety) from deleting themselves via this generic endpoint
        # A separate mechanism for account deletion by the user themselves might be needed.
        if user_to_delete.id == current_user.id and not current_user.is_superuser : # Normal user deleting self
             # Allow self deletion for normal users, but superuser self-delete needs more thought
             pass
        elif user_to_delete.id == current_user.id and current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superusers cannot delete themselves through this endpoint for safety. Use a dedicated admin tool or procedure."
            )

        deleted_user = crud_user.delete_user(db=db, user_id=user_id)
        return deleted_user is not None