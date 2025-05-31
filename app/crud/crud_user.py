from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session, func, select
from app.core.security import get_password_hash
from app.models.user import User, UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Get a single user by ID.
    """
    return db.get(User, user_id)

def get_user_by_email(db: Session, *, email: str) -> Optional[User]:
    """
    Get a single user by email.
    """
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()

def get_users_multi(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[User]:
    """
    Get multiple users with pagination.
    """
    statement = select(User).offset(skip).limit(limit)
    return db.exec(statement).all()

def count_users(db: Session) -> int:
    """
    Count the total number of users.
    """
    count_statement = select(func.count(User.id)).select_from(User) # More specific count
    return db.exec(count_statement).one()

def create_user(db: Session, *, user_in: UserCreate) -> User:
    """
    Create a new user.
    """
    hashed_password = get_password_hash(user_in.password)
    db_user = User.model_validate(
        user_in,
        update={"hashed_password": hashed_password} # Replace plain password with hash
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session, *, db_user: User, user_in: UserUpdate
) -> User:
    """
    Update an existing user.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in user_data and user_data["password"]: # If password is being updated
        hashed_password = get_password_hash(user_data["password"])
        db_user.hashed_password = hashed_password
        del user_data["password"] # Remove plain password from update data

    # Update other fields
    for field, value in user_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, *, user_id: int) -> Optional[User]:
    """
    Delete a user by ID.
    Returns the deleted user or None if not found.
    """
    user = db.get(User, user_id)
    if user:
        db.delete(user)
        db.commit()
        return user
    return None

def update_last_login(db: Session, *, user: User) -> User:
    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user