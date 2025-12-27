from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_current_user_from_cookie,get_db
from app.models.session import UserSession
from app.models.token import RefreshToken
from app.core.redis import redis_client
from app.core.config import settings

router = APIRouter()


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    user, current_session = get_current_user_from_cookie(request, db)

    # Load all active sessions for user
    sessions = (
        db.query(UserSession)
        .filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True,
        )
        .all()
    )

    # Redis: revoke & deactivate all sessions
    if redis_client:
        for s in sessions:
            # Remove active session marker
            redis_client.delete(f"oauth:session:active:{s.id}")

            # Blacklist access tokens tied to this session
            redis_client.setex(
                f"oauth:session:revoked:{s.id}",
                settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                "1",
            )

    # DB: mark all sessions inactive
    (
        db.query(UserSession)
        .filter(UserSession.user_id == user.id)
        .update(
            {
                "is_active": False,
                "expires_at": datetime.utcnow(),
            }
        )
    )

    # Revoke all refresh tokens
    (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user.id)
        .update({"is_revoked": True})
    )

    db.commit()

    # Delete session cookie
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
    )

    return {"logout": "global"}
