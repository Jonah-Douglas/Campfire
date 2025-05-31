from datetime import datetime, timezone
from sqlmodel import Session, select
from app.models.usersession import UserSession


def create_user_session(
    db: Session, *, user_id: int, refresh_token_jti: str, 
    user_agent: str | None, ip_address: str | None, expires_at: datetime
) -> UserSession:
    db_session = UserSession(
        user_id=user_id,
        refresh_token_jti=refresh_token_jti,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at,
        is_active=True
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_active_session_by_jti_and_user(
    db: Session, *, refresh_token_jti: str, user_id: int
) -> UserSession | None:
    statement = (
        select(UserSession)
        .where(UserSession.refresh_token_jti == refresh_token_jti)
        .where(UserSession.user_id == user_id)
        .where(UserSession.is_active == True)
    )
    return db.exec(statement).first()

def invalidate_session(db: Session, *, user_session: UserSession) -> UserSession:
    user_session.is_active = False
    user_session.expires_at = datetime.now(timezone.utc)
    db.add(user_session)
    db.commit()
    db.refresh(user_session)
    return user_session