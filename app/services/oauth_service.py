import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.models.client import OAuthClient
from app.models.token import AuthorizationCode, RefreshToken
from app.models.session import UserSession
from app.core.jwt import create_access_token
from app.core.config import settings
from app.utils.password import verify_password
from app.utils.pkce import verify_pkce
from app.core.redis import redis_client


class OAuthService:

    def __init__(self, db: Session):
        self.db = db

    # ------------------------
    # Authorization Code Flow
    # ------------------------

    def create_authorization_code(self,response_type: str,client_id: str,redirect_uri: str,scope: str,user_id,code_challenge:Optional[str],code_challenge_method: Optional[str]) -> str:

        if response_type != "code":
            raise HTTPException(status_code=400, detail="Invalid response_type")

        client = self._get_client(client_id)

        if redirect_uri not in client.redirect_uris:
            raise HTTPException(status_code=400, detail="Invalid redirect_uri")

        code = secrets.token_urlsafe(32)

        auth_code = AuthorizationCode(
            code=code,
            client_id=client.id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )

        self.db.add(auth_code)
        self.db.commit()

        return code


    def exchange_authorization_code(
        self,
        client_id: str,
        client_secret: Optional[str],
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str],
    ):
        # Authenticate client
        client = self._authenticate_client(client_id, client_secret)

        # Load auth code
        auth_code = (
            self.db.query(AuthorizationCode)
            .filter(AuthorizationCode.code == code)
            .first()
        )
        if not auth_code:
            raise HTTPException(status_code=400, detail="Invalid authorization code")

        # Expiry check
        if auth_code.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Authorization code expired")

        # Redirect URI validation (OAuth REQUIRED)
        if auth_code.redirect_uri != redirect_uri:
            raise HTTPException(status_code=400, detail="Redirect URI mismatch")

        # PKCE verification (if used)
        if auth_code.code_challenge:
            if not code_verifier or not verify_pkce(
                code_verifier, auth_code.code_challenge
            ):
                raise HTTPException(status_code=400, detail="PKCE verification failed")

        session = (
            self.db.query(UserSession)
            .filter(UserSession.user_id == auth_code.user_id, UserSession.is_active==True)
            .first()
        )

        if not session:
            raise HTTPException(status_code=400, detail="Active session not exists")

        # Issue access token
        access_token = create_access_token(
            subject=str(auth_code.user_id),
            scope=auth_code.scope,
            client_id=client.client_id,
            session_id=str(session.id),  # or session_id if you store it
        )

        # Issue refresh token
        refresh_token_value = secrets.token_urlsafe(48)

        refresh_token = RefreshToken(
            token=refresh_token_value,
            client_id=client.id,
            user_id=auth_code.user_id,
            session_id=session.id,
            scope=auth_code.scope,
            expires_at=datetime.utcnow() + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS),
        )

        self.db.add(refresh_token)

        # Invalidate auth code (single-use)
        self.db.delete(auth_code)

        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_value,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            "scope": auth_code.scope,
        }

    # ------------------------
    # Refresh Token Flow
    # ------------------------

    def refresh_access_token(self, client_id: str, refresh_token: str):
        token = self.db.query(RefreshToken).filter_by(token=refresh_token, is_revoked=False).first()
        if not token:
            raise HTTPException(status_code=400, detail="Invalid refresh token")

        session_id = token.session_id

        # Redis active session must exist
        if redis_client:
            if not redis_client.get(f"oauth:session:active:{session_id}"):
                raise HTTPException(status_code=401, detail="Session expired")

        # Redis revoked session must NOT exist
        if redis_client.get(f"oauth:session:revoked:{session_id}"):
            raise HTTPException(status_code=401, detail="Session revoked")


        access_token = create_access_token(
            subject=str(token.user_id),
            client_id=client_id,
            session_id=session_id,
            scope=token.scope,
        )

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 900,
            "scope": token.scope,
        }

    # ------------------------
    # Client Credentials Flow
    # ------------------------

    def client_credentials_token(self, client_id: str, client_secret: str, scope: str):
        client = self._authenticate_client(client_id, client_secret)

        access_token = create_access_token(
            subject=client.client_id,
            client_id=client.client_id,
            scope=scope,
        )

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 900,
            "scope": scope,
        }

    # ------------------------
    # Helpers
    # ------------------------

    def _get_client(self, client_id: str) -> OAuthClient:
        client = self.db.query(OAuthClient).filter_by(client_id=client_id).first()
        if not client:
            raise HTTPException(status_code=400, detail="Invalid client")
        return client

    def _authenticate_client(self, client_id: str, client_secret: str) -> OAuthClient:
        client = self._get_client(client_id)

        if client.is_confidential:
            if not client_secret or not verify_password(client_secret, client.client_secret_hash):
                raise HTTPException(status_code=401, detail="Invalid client credentials")

        return client
