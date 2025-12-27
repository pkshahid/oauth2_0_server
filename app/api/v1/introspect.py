from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.token_service import TokenService

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/introspect")
def introspect(
    token: str = Form(...),
    db: Session = Depends(get_db),
):
    service = TokenService(db)
    return service.introspect_token(token)