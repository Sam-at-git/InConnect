"""
Hotel API endpoints
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.hotel import hotel as hotel_crud
from app.schemas.hotel import (
    HotelCreate,
    HotelUpdate,
    HotelResponse,
    HotelListResponse,
)
from app.schemas.common import APIResponse, PaginatedData
from app.core.auth import get_current_user_id
from app.dependencies import DBSession
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedData[HotelResponse]])
async def list_hotels(
    db: DBSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    status: str | None = None,
) -> APIResponse[PaginatedData[HotelResponse]]:
    """
    List hotels with pagination

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum records per page
        status: Filter by status

    Returns:
        Paginated list of hotels
    """
    # Get hotels
    if status == "active":
        hotels = await hotel_crud.get_active(db, skip=skip, limit=limit)
        total = await hotel_crud.count_active(db)
    else:
        hotels = await hotel_crud.get_multi(db, skip=skip, limit=limit)
        total = await hotel_crud.count(db)

    # Create paginated response
    page = skip // limit + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 0
    paginated_data = PaginatedData.create(
        items=[HotelResponse.model_validate(h) for h in hotels],
        total=total,
        page=page,
        page_size=limit,
    )

    return APIResponse(data=paginated_data)


@router.get("/{hotel_id}", response_model=APIResponse[HotelResponse])
async def get_hotel(
    hotel_id: str,
    db: DBSession,
) -> APIResponse[HotelResponse]:
    """
    Get hotel by ID

    Args:
        hotel_id: Hotel ID
        db: Database session

    Returns:
        Hotel details
    """
    hotel = await hotel_crud.get(db, hotel_id)
    if not hotel:
        raise NotFoundError("Hotel not found")

    return APIResponse(data=HotelResponse.model_validate(hotel))


@router.post("", response_model=APIResponse[HotelResponse])
async def create_hotel(
    hotel_in: HotelCreate,
    db: DBSession,
    _user_id: str = Depends(get_current_user_id),
) -> APIResponse[HotelResponse]:
    """
    Create new hotel

    Args:
        hotel_in: Hotel creation data
        db: Database session
        _user_id: Current user ID (from JWT)

    Returns:
        Created hotel
    """
    # Check if hotel with same corp_id exists
    existing = await hotel_crud.get_by_corp_id(db, hotel_in.corp_id)
    if existing:
        raise ValidationError("Hotel with this corporate ID already exists")

    hotel = await hotel_crud.create(db, hotel_in)
    return APIResponse(
        message="Hotel created successfully",
        data=HotelResponse.model_validate(hotel),
    )


@router.put("/{hotel_id}", response_model=APIResponse[HotelResponse])
async def update_hotel(
    hotel_id: str,
    hotel_in: HotelUpdate,
    db: DBSession,
    _user_id: str = Depends(get_current_user_id),
) -> APIResponse[HotelResponse]:
    """
    Update hotel

    Args:
        hotel_id: Hotel ID
        hotel_in: Hotel update data
        db: Database session
        _user_id: Current user ID (from JWT)

    Returns:
        Updated hotel
    """
    hotel = await hotel_crud.get(db, hotel_id)
    if not hotel:
        raise NotFoundError("Hotel not found")

    updated_hotel = await hotel_crud.update(db, hotel, hotel_in)
    return APIResponse(
        message="Hotel updated successfully",
        data=HotelResponse.model_validate(updated_hotel),
    )


@router.delete("/{hotel_id}", response_model=APIResponse)
async def delete_hotel(
    hotel_id: str,
    db: DBSession,
    _user_id: str = Depends(get_current_user_id),
) -> APIResponse:
    """
    Delete hotel

    Args:
        hotel_id: Hotel ID
        db: Database session
        _user_id: Current user ID (from JWT)

    Returns:
        Success response
    """
    hotel = await hotel_crud.get(db, hotel_id)
    if not hotel:
        raise NotFoundError("Hotel not found")

    deleted = await hotel_crud.delete(db, hotel_id)
    if not deleted:
        raise ValidationError("Failed to delete hotel")

    return APIResponse(message="Hotel deleted successfully")
