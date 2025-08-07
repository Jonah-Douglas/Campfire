from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError

from app.auth.repositories.pending_otps_repository import PendingOTPRepository
from app.auth.repositories.user_sessions_repository import UserSessionRepository
from app.auth.schemas.token_schema import AccessTokenPayload
from app.auth.services.auth_service import AuthService
from app.core.config import settings
from app.core.constants.security import SecurityConstants
from app.core.dependencies import CurrentSMSService
from app.core.logging.logger_wrapper import firelog
from app.db.session import SessionDependency
from app.users.models.user_model import User
from app.users.repositories.user_repository import UserRepository

# --- OAuth2 Scheme & Token Dependency ---
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V_STR}/auth/login")
TokenDependency = Annotated[str, Depends(reusable_oauth2)]


# --- Current User Dependency ---
def get_current_user(session: SessionDependency, token: TokenDependency) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.ACCESS_TOKEN_SECRET_KEY,
            algorithms=[SecurityConstants.JWT_ALGORITHM],
        )
        token_data = AccessTokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: Invalid or expired token. ({str(e).capitalize()})",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except ValidationError as e:
        firelog.warning(f"Malformed token payload: {e.errors()}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not validate credentials: Malformed token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        firelog.error(f"Unexpected error during token processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing credentials.",
        ) from e

    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive."
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# --- Auth Service Dependency ---
@lru_cache
def get_auth_service_instance(
    sms_service: CurrentSMSService,
    user_repository: Annotated[UserRepository, Depends(UserRepository)],
    otp_repository: Annotated[PendingOTPRepository, Depends(PendingOTPRepository)],
    session_repository: Annotated[
        UserSessionRepository, Depends(UserSessionRepository)
    ],
) -> AuthService:
    return AuthService(
        sms_service=sms_service,
        user_repository=user_repository,
        otp_repository=otp_repository,
        session_repository=session_repository,
    )


CurrentAuthService = Annotated[AuthService, Depends(get_auth_service_instance)]
