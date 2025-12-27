from fastapi import APIRouter, Depends
from app.api.deps import require_scope

router = APIRouter()

@router.get("/admin/users", dependencies=[Depends(require_scope("read"))])
def admin_users():
    return {"status": "authorized"}