from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone

from app.models.usersession import UserSession


# Users
## Shared user properties
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    full_name: str | None = Field(default=None)

## Required user properties on creation
class UserCreate(UserBase):
    password: str

## Optional user properties on patch
class UserUpdate(UserBase):
    email: str | None = Field(default=None)
    password: str | None = Field(default=None)
    full_name: str | None = Field(default=None)
    is_active: bool | None = Field(default=None)
    is_superuser: bool | None = Field(default=None)

## Model for updating a User's password
class UserUpdatePassword(SQLModel):
    current_password: str
    new_password: str


#----------------------------
# User table
class User(UserBase, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )
    last_login_at: Optional[datetime] = Field(default=None)

    # Relationship to UserSession
    sessions: List["UserSession"] = Relationship(back_populates="user")


#----------------------------
# User out models

## User out model
class UserOut(UserBase):
    id: int
    created_at: datetime
    last_login_at: Optional[datetime] = Field(default=None)


## Collection user out model
class UsersOut(SQLModel):
    data: List[UserOut]
    count: int