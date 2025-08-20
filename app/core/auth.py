import json

import jwt
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.algorithms import RSAAlgorithm

from app.core.config import settings

security = HTTPBearer()


def get_jwks() -> dict:
    """
    Fetch the JSON Web Key Set (JWKS) from the Clerk API.
    """
    try:
        response = requests.get(settings.CLERK_JWKS_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch JWKS: {str(e)}",
        ) from e


def get_public_key(kid: str) -> str:
    """
    Retrieve the public key from the JWKS.
    """
    jwks = get_jwks()
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return RSAAlgorithm.from_jwk(json.dumps(key))
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Public key not found for the provided token",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Decode the JWT token using the public key.
    """
    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]
        public_key = get_public_key(kid)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=[settings.CLERK_AUDIENCE],
            issuer=settings.CLERK_ISSUER,
        )

        user_id = payload["sub"]
        return user_id
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error decoding token: {str(e)}"
        ) from e
