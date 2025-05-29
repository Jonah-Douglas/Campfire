from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.dependencies import SessionDependency
from models.token import Token
from core.config import settings
from core import security
import api.routes.utils as utils


router = APIRouter()


@router.post("/auth/login")
def login_access_token(
    session: SessionDependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get access and refresh tokens for future requests.
    """
    user = utils.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = security.create_access_token(user.id, expires_delta=access_token_expires)
    refresh_token = security.create_refresh_token(user.id, expires_delta=refresh_token_expires)

    return Token(access_token=access_token, refresh_token=refresh_token)