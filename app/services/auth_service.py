from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import jwt, JWTError

from app.models.user import User
from app.models.token import Token
from app.core.config import settings
from app.core.security import verify_password
from app.core import security
from app.crud import crud_user, crud_usersession
from sqlmodel import Session


class AuthService:
    def _authenticate_user(self, db: Session, email: str, password: str) -> User | None:
        """Helper to authenticate a user."""
        user = crud_user.get_user_by_email(db=db, email=email)
        if not user:
            return None
        if not user.is_active:
            # Consider what to do here. If the user exists but is inactive,
            # the login attempt should probably fail specifically due to inactivity.
            # Returning None here will lead to a generic "incorrect email/password".
            # It might be better for `login_user` to handle the `is_active` check.
            return None 
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def login_user(
        self, 
        db: Session, 
        email: str, 
        password: str, 
        request_headers: dict,
        client_host: str | None
    ) -> tuple[User, Token]:
        user = self._authenticate_user(db=db, email=email, password=password)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")

        updated_user = crud_user.update_last_login(db=db, user=user)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_duration = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token_str, refresh_token_jti = security.create_refresh_token_with_jti(
            subject=updated_user.id, expires_delta=refresh_token_duration
        )
        access_token_str = security.create_access_token(
            subject=updated_user.id, expires_delta=access_token_expires
        )

        # Create and store new user session - could be a crud_usersession function
        new_db_session = crud_usersession.create_user_session(
            db=db,
            user_id=updated_user.id,
            refresh_token_jti=refresh_token_jti,
            user_agent=request_headers.get("User-Agent"),
            ip_address=client_host,
            expires_at=datetime.now(timezone.utc) + refresh_token_duration,
        )

        return updated_user, Token(access_token=access_token_str, refresh_token=refresh_token_str)
    
    def logout_user(
        self,
        db: Session,
        current_user_id: int,
        refresh_token_to_invalidate: str,
    ) -> None: # Returns None for 204
        try:
            payload = jwt.decode(
                refresh_token_to_invalidate,
                settings.REFRESH_TOKEN_SECRET_KEY,
                algorithms=[security.ALGORITHM],
                options={"verify_aud": False},
            )
            refresh_token_jti: str | None = payload.get("jti")
            user_id_from_token: int | None = payload.get("sub")

            if not refresh_token_jti or user_id_from_token is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token format.")
            
            # Important: Convert user_id_from_token to int for comparison if it's not already
            if current_user_id != int(user_id_from_token):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Refresh token does not correspond to the authenticated user.",
                )

        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token provided.")

        user_session = crud_usersession.get_active_session_by_jti_and_user(
            db=db, refresh_token_jti=refresh_token_jti, user_id=int(user_id_from_token)
        )

        if not user_session:
            # silently fail, maybe record a log here for tracking bad requests
            return

        crud_usersession.invalidate_session(db=db, user_session=user_session)
        return