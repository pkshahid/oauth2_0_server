from fastapi import APIRouter, Depends, Response, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.db.session import SessionLocal
from app.models.user import User
from app.models.session import UserSession
from app.utils.password import verify_password
from app.core.config import settings
from app.core.redis import redis_client


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    next: Optional[str] = None,
    db: Session = Depends(get_db),
):
    # Authenticate user
    user = db.query(User).filter_by(email=email, is_active=True).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create DB session (source of truth)
    expires_at = datetime.utcnow() + timedelta(days=7)

    session = UserSession(
        user_id=user.id,
        is_active=True,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    # Store session presence in Redis (fast-path)
    if redis_client:
        redis_client.setex(
            f"oauth:session:active:{session.id}",
            int((expires_at - datetime.utcnow()).total_seconds()),
            str(user.id),
        )

    # Redirect with cookie
    response = RedirectResponse(
        url=next or "/",
        status_code=307,
    )

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=str(session.id),
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
    )

    return response
