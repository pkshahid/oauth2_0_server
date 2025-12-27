from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    APP_NAME: str = "OAuth2 Server"
    DEBUG: bool = False
    # Environment
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str

    # Redis
    
    REDIS_URL: Optional[str] = None

    # Security
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 900          # 15 minutes
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 2592000     # 30 days

    # OAuth
    ISSUER: str = "https://auth.example.com"

    # Cookies (SSO)
    SESSION_COOKIE_NAME: str = "sso_session"
    SESSION_COOKIE_SECURE: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()