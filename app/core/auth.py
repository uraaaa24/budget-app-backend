import threading
from dataclasses import dataclass

import jwt
import requests
from cachetools import TTLCache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWK

from app.core.config import settings


@dataclass(frozen=True)
class AuthContext:
    sub: str
    claims: dict[str, any]


BEARER = HTTPBearer(auto_error=False)

_JWKS_CACHE = TTLCache(maxsize=1, ttl=600)
_JWKS_LOCK = threading.Lock()


def _http_401(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
    )


def _http_503(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=detail,
    )


def _fetch_jwks() -> dict:
    try:
        response = requests.get(settings.CLERK_JWKS_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise _http_503(f"Failed to fetch JWKS: {e}") from e


def _get_jwks() -> dict:
    """Get JWKS from TTL cache; fetch if missing/expired."""
    with _JWKS_LOCK:
        jwks = _JWKS_CACHE.get("jwks")
        if jwks is None:
            jwks = _fetch_jwks()
            _JWKS_CACHE["jwks"] = jwks
        return jwks


def _refresh_jwks() -> dict:
    """Force refresh JWKS (used on kid miss)."""
    with _JWKS_LOCK:
        jwks = _fetch_jwks()
        _JWKS_CACHE["jwks"] = jwks
        return jwks


def _public_key_from_kid(kid: str):
    """
    Return RSA public key for the given kid.
    If not found, force-refresh JWKS once and retry.
    """

    def _search(jwks: dict):
        for k in jwks.get("keys", []):
            if k.get("kid") == kid:
                return PyJWK.from_dict(k).key
        return None

    jwks = _get_jwks()
    public_key = _search(jwks)
    if public_key is not None:
        return public_key

    jwks = _refresh_jwks()
    public_key = _search(jwks)
    if public_key is not None:
        return public_key

    raise _http_401(detail="Public key not found for the provided token")


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(BEARER),
) -> AuthContext:
    """
    Get the current user from the JWT token in the Authorization header
    """
    if not creds or (creds.scheme or "").lower() != "bearer":
        raise _http_401(detail="Invalid or missing authorization header")

    token = creds.credentials

    try:
        header = jwt.get_unverified_header(token)
    except jwt.InvalidTokenError as e:
        raise _http_401(f"Invalid token header: {e}") from e

    kid = header.get("kid")
    if not kid:
        raise _http_401("Missing kid in token header")

    # Retrieve the public key using the kid
    public_key = _public_key_from_kid(kid)

    # Decode the JWT token using the public key
    try:
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.CLERK_AUDIENCE,
            issuer=settings.CLERK_ISSUER,
        )
        return AuthContext(sub=claims["sub"], claims=claims)

    except jwt.ExpiredSignatureError as e:
        raise _http_401("Token has expired") from e
    except jwt.ImmatureSignatureError as e:
        raise _http_401("Token not yet valid (nbf)") from e
    except jwt.InvalidAudienceError as e:
        raise _http_401("Invalid audience") from e
    except jwt.InvalidIssuerError as e:
        raise _http_401("Invalid issuer") from e
    except jwt.InvalidTokenError as e:
        raise _http_401(f"Invalid token: {e}") from e
