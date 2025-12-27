from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class AuthorizationCode(Base):
    __tablename__ = "authorization_codes"

    code = Column(String(128), primary_key=True)
    client_id = Column(UUID, ForeignKey("oauth_clients.id"))
    user_id = Column(UUID, ForeignKey("users.id"))
    redirect_uri = Column(String)
    scope = Column(String)

    code_challenge = Column(String, nullable=True)
    code_challenge_method = Column(String, nullable=True)

    expires_at = Column(DateTime)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token = Column(String, primary_key=True)
    client_id = Column(UUID, ForeignKey("oauth_clients.id"))
    user_id = Column(UUID, ForeignKey("users.id"))
    session_id = Column(UUID, ForeignKey("user_sessions.id"))
    scope = Column(String)
    expires_at = Column(DateTime)
    is_revoked = Column(Boolean, default=False)