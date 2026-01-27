"""
Health check endpoint
"""

from fastapi import APIRouter

from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/health", response_model=APIResponse)
async def health_check() -> APIResponse:
    """
    Health check endpoint

    Returns:
        APIResponse with status information
    """
    return APIResponse(data={"status": "healthy"})


@router.get("/ping", response_model=APIResponse)
async def ping() -> APIResponse:
    """
    Simple ping endpoint

    Returns:
        APIResponse with pong
    """
    return APIResponse(data={"message": "pong"})
