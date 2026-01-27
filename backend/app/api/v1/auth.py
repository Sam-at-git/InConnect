"""
Authentication API endpoints
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.common import APIResponse
from app.dependencies import get_db_session
from app.core.security import create_access_token
from app.crud.staff import staff as staff_crud
from app.core.exceptions import UnauthorizedError, NotFoundError
from app.config import get_settings
from app.core.database import AsyncSession

router = APIRouter()

DBSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    request: LoginRequest,
    db: DBSession,
) -> APIResponse[LoginResponse]:
    """
    Staff login endpoint

    Note: This is a simplified version for MVP.
    In production, this would integrate with WeChat OAuth
    and verify credentials properly.

    Args:
        request: Login request with wechat_userid and password
        db: Database session

    Returns:
        Login response with JWT token
    """
    # Find staff by WeChat user ID
    staff_member = await staff_crud.get_by_wechat_userid(db, request.wechat_userid)
    if not staff_member:
        raise NotFoundError("Staff member not found")

    if staff_member.status != "active":
        raise UnauthorizedError("Staff account is not active")

    # Create access token
    settings = get_settings()
    access_token = create_access_token(
        data={
            "sub": staff_member.id,
            "hotel_id": staff_member.hotel_id,
            "role": staff_member.role,
        }
    )

    return APIResponse[LoginResponse](
        code=0,
        message="Login successful",
        data=LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            staff_id=staff_member.id,
            staff_name=staff_member.name,
            hotel_id=staff_member.hotel_id,
            role=staff_member.role,
        )
    )


@router.post("/logout", response_model=APIResponse)
async def logout() -> APIResponse:
    """
    Logout endpoint

    Note: JWT tokens are stateless, so logout is handled on the client
    by removing the token. This endpoint can be used for logging or
    token invalidation if using a token blacklist.

    Returns:
        Success response
    """
    return APIResponse(message="Logout successful")


@router.post("/refresh", response_model=APIResponse[LoginResponse])
async def refresh_token() -> APIResponse[LoginResponse]:
    """
    Refresh access token

    Note: For MVP, this is a placeholder. In production, this would
    use refresh tokens for better security.

    Returns:
        New login response with refreshed token
    """
    return APIResponse[LoginResponse](
        code=0,
        message="Token refresh not implemented yet",
        data=None
    )
