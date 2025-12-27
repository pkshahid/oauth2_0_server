# scripts/create_client.py

import secrets
from app.db.session import SessionLocal
from app.models.client import OAuthClient
from app.utils.password import hash_password

db = SessionLocal()

client_secret = secrets.token_urlsafe(32)

client = OAuthClient(
    client_id="example_client",
    client_secret_hash=hash_password(client_secret),
    redirect_uris=["https://app.example.com/callback"],
    allowed_grant_types=["authorization_code", "refresh_token"],
    allowed_scopes=["read", "write", "admin"],
)

db.add(client)
db.commit()

print("CLIENT_ID:", client.client_id)
print("CLIENT_SECRET:", client_secret)