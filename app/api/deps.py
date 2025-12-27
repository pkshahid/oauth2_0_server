from fastapi import Depends, HTTPException, Security, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.config import settings
from app.core.jwt import decode_token
from app.core.redis import redis_client
from app.models.session import UserSession

security = HTTPBearer()


def get_current_token(credentials=Security(security)):
    token = credentials.credentials

    payload = decode_token(token)

    # Session revocation check (global logout)
    sid = payload.get("sid")
    if not sid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token (no session)",
        )

    # Redis active session must exist
    if redis_client:
        if not redis_client.get(f"oauth:session:active:{sid}"):
            raise HTTPException(status_code=401, detail="Session expired")

    # Redis revoked session must NOT exist
    if redis_client.get(f"oauth:session:revoked:{sid}"):
        raise HTTPException(status_code=401, detail="Session revoked")


    return payload


def require_scope(required_scope: str):
    def checker(payload=Depends(get_current_token)):
        sid = payload.get("sid",None)
        if sid:
            # Redis revoked session must NOT exist
            if redis_client.get(f"oauth:session:revoked:{sid}"):
                raise HTTPException(status_code=401, detail="Session revoked")

            # Redis active session must exist
            if redis_client:
                if not redis_client.get(f"oauth:session:active:{sid}"):
                    raise HTTPException(status_code=401, detail="Session expired")


        scopes = payload.get("scope", "").split()
        if required_scope not in scopes:
            raise HTTPException(status_code=403, detail="Insufficient scope")
    return checker

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session_id_from_cookie(request: Request) -> str:
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session cookie missing",
        )

    return session_id

def get_current_user_from_cookie(
    request: Request,
    db: Session,
):
    session_id = get_session_id_from_cookie(request)
    session = (
        db.query(UserSession)
        .filter_by(id=session_id, is_active=True)
        .first()
    )
    if not session:
        raise HTTPException(status_code=401)
    user = (
        db.query(User)
        .filter_by(id=session.user_id, is_active=True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=401)

    return user, session
