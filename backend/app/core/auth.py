"""
Authentication dependencies for FastAPI
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedError

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """
    Get current user ID from JWT token

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        User ID from token

    Raises:
        UnauthorizedError: If token is invalid or missing
    """
    if credentials is None:
        raise UnauthorizedError("Missing authentication token")

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise UnauthorizedError("Invalid or expired token")

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Invalid token payload")

    return user_id


async def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str | None:
    """
    Get current user ID from JWT token (optional)

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        User ID from token or None if not authenticated
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        return None

    return payload.get("sub")


# Type alias for dependency injection
CurrentUserId = str | None
OptionalUserId = str | None
RequiredUserId = str
