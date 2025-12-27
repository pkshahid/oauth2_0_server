# OAuth 2.0 & SSO Authentication Server

A production-grade OAuth 2.0 Authorization Server with SSO, built using FastAPI, PostgreSQL, and Redis.  
This project implements industry-standard authentication and authorization flows similar to Auth0 / Keycloak, with a strong focus on security, scalability, and correctness.

---

## Features

### Core Authentication
- Cookie-based SSO login
- Secure password hashing (bcrypt)
- Multi-session support (multi-device login)

### OAuth 2.0 (RFC 6749)
- Authorization Code Grant
- Refresh Token Grant
- Token Revocation (RFC 7009)
- Token Introspection (RFC 7662)
- PKCE support (optional)

### Token System
- RSA-signed JWT access tokens
- Refresh tokens stored securely in PostgreSQL
- Scope-based authorization (read, write, admin)
- Session-bound tokens (sid claim)

### Session Management
- PostgreSQL as source of truth
- Redis for fast session validation and revocation
- Global logout (invalidate all sessions)
- Instant token invalidation without DB hits

### Security
- Stateless JWTs with stateful revocation
- Redis-backed session blacklist
- Proper HTTP status codes (401 vs 403)
- Secure cookies (HttpOnly, SameSite, Secure)
- Replay-safe authorization codes

---

## Architecture Overview

```
Browser / Client
      |
      v
SSO Login (Cookie)
      |
      v
OAuth /authorize
      |
      v
Authorization Code
      |
      v
OAuth /token
      |
      v
JWT Access Token  ---> Protected APIs
      |
      v
Refresh Token
```

### Storage Layers

| Layer       | Purpose                                |
|------------|----------------------------------------|
| PostgreSQL | Users, sessions, refresh tokens, audit |
| Redis      | Session presence and revocation        |
| JWT        | Stateless access tokens                |

---

## Tech Stack

- Python 3.9+
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- PyJWT / python-jose
- Passlib (bcrypt)

---

## Project Structure

```
app/
├── api/
│   ├── deps.py
│   ├── router.py
│   └── v1/
│       ├── oauth.py
│       ├── sso.py
│       ├── logout.py
│       ├── introspect.py
│       ├── revoke.py
│       └── userinfo.py
│
├── core/
│   ├── config.py
│   ├── jwt.py
│   └── redis.py
│
├── db/
│   └── session.py
│
├── models/
│   ├── user.py
│   ├── session.py
│   ├── token.py
│   └── client.py
│
├── services/
│   ├── oauth_service.py
│   └── token_service.py
│
├── utils/
│   └── password.py
│
└── main.py
```

---

## Environment Variables

Create a `.env` file:

```
APP_NAME=OAuth Server
DEBUG=true

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
REDIS_URL=redis://localhost:6379/0

ISSUER=http://localhost:8000
SESSION_COOKIE_NAME=sso_session
SESSION_COOKIE_SECURE=false

JWT_ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_SECONDS=900
REFRESH_TOKEN_EXPIRE_DAYS=30
```

---

## Running with Docker

```
docker compose up -d
```

Services:
- PostgreSQL → localhost:5432
- Redis → localhost:6379
- Adminer → http://localhost:8080

---

## Running Locally

```
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI:
```
http://localhost:8000/docs
```

---

## Authentication Flow

### 1. SSO Login

```
POST /api/v1/sso/login
```

Sets secure session cookie:
```
sso_session=<session_id>
```

---

### 2. OAuth Authorization

```
GET /api/v1/oauth/authorize
```

Response:
```
302 Redirect -> redirect_uri?code=AUTH_CODE
```

---

### 3. Token Exchange

```
POST /api/v1/oauth/token
```

Response:
```
{
  "access_token": "JWT",
  "refresh_token": "TOKEN",
  "token_type": "Bearer",
  "expires_in": 900,
  "scope": "read write"
}
```

---

### 4. Protected API Call

```
Authorization: Bearer <access_token>
```

---

### 5. UserInfo (OIDC-style)

```
GET /api/v1/userinfo/me
```

Response:
```
{
  "sub": "user_id",
  "scope": "read write",
  "iss": "http://localhost:8000"
}
```

---

## Refresh Token Flow

```
POST /api/v1/oauth/token
grant_type=refresh_token
```

Returns a new access token.

---

## Logout and Revocation

### Global Logout

```
POST /api/v1/logout
```

Effect:
- All sessions revoked
- All refresh tokens revoked
- All access tokens invalidated via Redis

---

## Token Introspection

```
POST /api/v1/oauth/introspect
```

Response:
```
{
  "active": true,
  "sub": "user_id",
  "scope": "read write",
  "exp": 1766778652
}
```

---

## Security Guarantees

- Replay-safe authorization codes
- Single-use auth codes
- Proper 401 vs 403 semantics
- Secure cookie handling
- Stateless access tokens
- Stateful revocation

---

## Production Checklist

- HTTPS only
- Rotate RSA keys (JWKS)
- Rate limit /oauth/token
- Enforce audience per client
- Secure cookies enabled
- Redis persistence enabled

---

## Standards Compliance

- OAuth 2.0 (RFC 6749)
- Token Revocation (RFC 7009)
- Token Introspection (RFC 7662)
- OpenID Connect (partial)

---

## Status

- Production-ready
- Enterprise-grade
- Horizontally scalable

---

## Author

Built with a senior-level, security-first mindset.  
Designed to be extensible, auditable, and safe by default.
