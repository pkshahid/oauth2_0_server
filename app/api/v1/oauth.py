from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi import Request
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import SessionLocal
from app.services.oauth_service import OAuthService
from app.api.deps import get_current_user_from_cookie

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/authorize")
def authorize(
    request: Request,
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        user,session = get_current_user_from_cookie(request, db)
    except HTTPException:
        # redirect to login with return URL
        login_url = (
            f"/api/v1/sso/login"
            f"?next={request.url}"
        )
        return RedirectResponse(login_url)

    service = OAuthService(db)

    auth_code = service.create_authorization_code(
        response_type=response_type,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        user_id=user.id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    redirect_url = f"{redirect_uri}?code={auth_code}"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(url=redirect_url)


@router.post("/token")
def token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: Optional[str] = Form(None),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    scope: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    OAuth Token Endpoint
    """
    service = OAuthService(db)

    if grant_type == "authorization_code":
        return service.exchange_authorization_code(
            client_id=client_id,
            client_secret=client_secret,
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )

    if grant_type == "refresh_token":
        return service.refresh_access_token(
            client_id=client_id,
            refresh_token=refresh_token,
        )

    if grant_type == "client_credentials":
        return service.client_credentials_token(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
        )

    raise HTTPException(status_code=400, detail="Unsupported grant_type")