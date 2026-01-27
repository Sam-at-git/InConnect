"""
Staff API endpoints
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.staff import staff as staff_crud
from app.schemas.staff import (
    StaffCreate,
    StaffUpdate,
    StaffResponse,
    StaffListResponse,
)
from app.schemas.common import APIResponse, PaginatedData
from app.core.auth import get_current_user_id
from app.dependencies import DBSession
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedData[StaffResponse]])
async def list_staff(
    db: DBSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    hotel_id: str | None = None,
    role: str | None = None,
    status: str | None = None,
    is_available: bool | None = None,
) -> APIResponse[PaginatedData[StaffResponse]]:
    """
    List staff members with pagination and filters

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum records per page
        hotel_id: Filter by hotel ID
        role: Filter by role
        status: Filter by status
        is_available: Filter by availability

    Returns:
        Paginated list of staff
    """
    # Get staff
    staff_list = await staff_crud.get_multi(db, skip=skip, limit=limit)
    total = await staff_crud.count(db)

    # Create paginated response
    page = skip // limit + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 0
    paginated_data = PaginatedData.create(
        items=[StaffResponse.model_validate(s) for s in staff_list],
        total=total,
        page=page,
        page_size=limit,
    )

    return APIResponse(data=paginated_data)


@router.get("/{staff_id}", response_model=APIResponse[StaffResponse])
async def get_staff(
    staff_id: str,
    db: DBSession,
) -> APIResponse[StaffResponse]:
    """
    Get staff member by ID

    Args:
        staff_id: Staff ID
        db: Database session

    Returns:
        Staff details
    """
    staff_member = await staff_crud.get(db, staff_id)
    if not staff_member:
        raise NotFoundError("Staff not found")

    return APIResponse(data=StaffResponse.model_validate(staff_member))


@router.post("", response_model=APIResponse[StaffResponse])
async def create_staff(
    staff_in: StaffCreate,
    db: DBSession,
    _user_id: str = Depends(get_current_user_id),
) -> APIResponse[StaffResponse]:
    """
    Create new staff member

    Args:
        staff_in: Staff creation data
        db: Database session
        _user_id: Current user ID (from JWT)

    Returns:
        Created staff member
    """
    # Check if staff with same wechat_userid exists
    if staff_in.wechat_userid:
        existing = await staff_crud.get_by_wechat_userid(db, staff_in.wechat_userid)
        if existing:
            raise ValidationError("Staff with this WeChat user ID already exists")

    staff_member = await staff_crud.create(db, staff_in)
    return APIResponse(
        message="Staff created successfully",
        data=StaffResponse.model_validate(staff_member),
    )


@router.put("/{staff_id}", response_model=APIResponse[StaffResponse])
async def update_staff(
    staff_id: str,
    staff_in: StaffUpdate,
    db: DBSession,
    _user_id: str = Depends(get_current_user_id),
) -> APIResponse[StaffResponse]:
    """
    Update staff member

    Args:
        staff_id: Staff ID
        staff_in: Staff update data
        db: Database session
        _user_id: Current user ID (from JWT)

    Returns:
        Updated staff member
    """
    staff_member = await staff_crud.get(db, staff_id)
    if not staff_member:
        raise NotFoundError("Staff not found")

    updated_staff = await staff_crud.update(db, staff_member, staff_in)
    return APIResponse(
        message="Staff updated successfully",
        data=StaffResponse.model_validate(updated_staff),
    )


@router.delete("/{staff_id}", response_model=APIResponse)
async def delete_staff(
    staff_id: str,
    db: DBSession,
    _user_id: str = Depends(get_current_user_id),
) -> APIResponse:
    """
    Delete staff member

    Args:
        staff_id: Staff ID
        db: Database session
        _user_id: Current user ID (from JWT)

    Returns:
        Success response
    """
    staff_member = await staff_crud.get(db, staff_id)
    if not staff_member:
        raise NotFoundError("Staff not found")

    deleted = await staff_crud.delete(db, staff_id)
    if not deleted:
        raise ValidationError("Failed to delete staff")

    return APIResponse(message="Staff deleted successfully")


@router.post("/{staff_id}/toggle-availability", response_model=APIResponse[StaffResponse])
async def toggle_availability(
    staff_id: str,
    db: DBSession,
    _user_id: str = Depends(get_current_user_id),
) -> APIResponse[StaffResponse]:
    """
    Toggle staff availability

    Args:
        staff_id: Staff ID
        db: Database session
        _user_id: Current user ID (from JWT)

    Returns:
        Updated staff member
    """
    staff_member = await staff_crud.get(db, staff_id)
    if not staff_member:
        raise NotFoundError("Staff not found")

    updated_staff = await staff_crud.update(
        db,
        staff_member,
        {"is_available": not staff_member.is_available},
    )
    return APIResponse(
        message="Staff availability updated",
        data=StaffResponse.model_validate(updated_staff),
    )
