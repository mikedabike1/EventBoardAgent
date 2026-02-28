"""Auth0 JWT validation and FastAPI dependency functions."""

import os
from functools import lru_cache

import jwt
from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

load_dotenv()

_AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")
_AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "")
_ADMIN_SECRET = os.getenv("ADMIN_SECRET", "")

ROLES_CLAIM = "https://eventboard/roles"

bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _get_jwks_client() -> PyJWKClient:
    return PyJWKClient(f"https://{_AUTH0_DOMAIN}/.well-known/jwks.json")


def decode_token(token: str) -> dict:
    """Validate and decode an Auth0 JWT. Returns the payload dict."""
    jwks_client = _get_jwks_client()
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=_AUTH0_AUDIENCE,
        issuer=f"https://{_AUTH0_DOMAIN}/",
    )
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer),
) -> dict:
    """Dependency: returns decoded JWT payload or raises 401."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return decode_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def require_user(payload: dict = Depends(get_current_user)) -> dict:
    """Dependency: any authenticated user."""
    return payload


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer),
    x_admin_secret: str | None = Header(None),
) -> dict:
    """Dependency: admin role via JWT, OR X-Admin-Secret header fallback."""
    # Service-key fallback for cron jobs / CLI scripts
    if _ADMIN_SECRET and x_admin_secret == _ADMIN_SECRET:
        return {"sub": "service", ROLES_CLAIM: ["admin"]}

    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    roles = payload.get(ROLES_CLAIM, [])
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin role required")

    return payload
