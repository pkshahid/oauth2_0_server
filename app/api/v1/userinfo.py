from fastapi import APIRouter, Depends
from app.api.deps import get_current_token

router = APIRouter()


@router.get("/me")
def userinfo(payload=Depends(get_current_token)):
    return {
        "sub": payload["sub"],
        "scope": payload.get("scope"),
        "iss": payload.get("iss"),
    }