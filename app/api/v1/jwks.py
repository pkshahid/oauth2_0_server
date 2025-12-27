import json
from fastapi import APIRouter

router = APIRouter()

with open("keys/public.pem", "r") as f:
    PUBLIC_KEY = f.read()


@router.get("/jwks.json")
def jwks():
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": "auth-server-key",
                "pem": PUBLIC_KEY,
            }
        ]
    }