from sqlmodel import Field, SQLModel


# Users
## Shared user properties
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None

## Required user properties on creation
class UserCreate(UserBase):
    email: str
    password: str
    full_name: str | None = None

## Optional user properties on patch
class UserUpdate(UserBase):
    email: str | None = None
    password: str | None = None

#----------------------------
# User table
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

#----------------------------
# User out models

## User out model
class UserOut(UserBase):
    id: int

## Collection user out model
class UsersOut(SQLModel):
    data: list[UserOut]
    count: int