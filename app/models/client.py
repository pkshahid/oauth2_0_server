import uuid
from sqlalchemy import Column, String, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class OAuthClient(Base):
    __tablename__ = "oauth_clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(String(64), unique=True, nullable=False, index=True)
    client_secret_hash = Column(String, nullable=True)

    redirect_uris = Column(ARRAY(String), nullable=False)
    allowed_grant_types = Column(ARRAY(String), nullable=False)
    allowed_scopes = Column(ARRAY(String), nullable=False)

    is_confidential = Column(Boolean, default=True)