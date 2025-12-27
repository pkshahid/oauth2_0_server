import jwt
import time
from jose import JWTError, ExpiredSignatureError
from fastapi import HTTPException, status
from app.core.config import settings

with open("keys/private.pem", "rb") as f:
    PRIVATE_KEY = f.read()

with open("keys/public.pem", "rb") as f:
    PUBLIC_KEY = f.read()

def create_access_token(subject, client_id, scope, session_id):
    payload = {
        "sub": str(subject),
        "sid": str(session_id),   # 🔥 SESSION BINDING
        "aud": client_id,
        "scope": scope,
        "iss": settings.ISSUER,
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)



def decode_token(token: str):
    try:
        return jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.ISSUER,
            audience=None,  # we'll enforce client_id separately
            options={
                "verify_aud": False,  # OK for now
                "require": ["exp", "iat", "sub"],
            },
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
