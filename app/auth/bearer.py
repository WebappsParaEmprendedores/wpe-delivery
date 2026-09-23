import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

ABT = settings.ACCESS_BEARER_TOKEN

if not ABT:
    raise RuntimeError("ACCESS_BEARER_TOKEN is not configured")

bearer_scheme = HTTPBearer()


def verify_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not secrets.compare_digest(
        credentials.credentials,
        ABT,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials
