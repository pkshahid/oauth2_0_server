
from fastapi import APIRouter
from app.api.v1 import oauth, introspect, revoke, jwks, logout, sso, userinfo
from app.api.examples import example

api_router = APIRouter()

api_router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
api_router.include_router(introspect.router, prefix="/oauth", tags=["introspect"])
api_router.include_router(revoke.router, prefix="/oauth", tags=["revoke"])
api_router.include_router(sso.router, prefix="/sso", tags=["sso"])
api_router.include_router(userinfo.router, prefix="/userinfo", tags=["userinfo"])
api_router.include_router(logout.router, prefix="/sso", tags=["logout"])

api_router.include_router(example.router, prefix="/test", tags=["test"])