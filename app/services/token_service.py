from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.jwt import decode_token
from app.core.redis import redis_client
from app.models.token import RefreshToken
from app.core.config import settings


class TokenService:
    def __init__(self, db: Session):
        self.db = db

    # =========================
    # Token Introspection
    # =========================
    def introspect_token(self, token: str) -> dict:
        try:
            payload = decode_token(token)
        except Exception:
            return {"active": False}

        session_id = payload.get("sid")
        if not session_id:
            return {"active": False}

        # Session revoked?
        if redis_client:
            if redis_client.get(f"oauth:session:revoked:{session_id}"):
                return {"active": False}

        return {
            "active": True,
            "sub": payload.get("sub"),
            "scope": payload.get("scope"),
            "client_id": payload.get("aud"),
            "iss": payload.get("iss"),
            "iat": payload.get("iat"),
            "exp": payload.get("exp"),
        }

    # =========================
    # Token Revocation (OAuth)
    # =========================
    def revoke_token(self, token: str):
        """
        OAuth token revocation:
        - revoke refresh token
        - revoke session (thus invalidating access tokens)
        """
        try:
            payload = decode_token(token)
        except Exception:
            # Per RFC 7009: revocation is idempotent
            return

        session_id = payload.get("sid")

        # Revoke session (kills all access tokens)
        if session_id and redis_client:
            redis_client.setex(
                f"oauth:session:revoked:{session_id}",
                settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                "1",
            )

            redis_client.delete(f"oauth:session:active:{session_id}")

        # Revoke refresh token if exists
        rt = (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False,
            )
            .first()
        )

        if rt:
            rt.is_revoked = True
            self.db.commit()
