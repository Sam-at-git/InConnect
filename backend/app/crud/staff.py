"""
CRUD operations for Staff model
"""

from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate


class CRUDStaff(CRUDBase[Staff, StaffCreate, StaffUpdate]):
    """CRUD operations for Staff"""

    async def get_by_wechat_userid(
        self, db: AsyncSession, wechat_userid: str
    ) -> Staff | None:
        """
        Get staff by WeChat user ID

        Args:
            db: Database session
            wechat_userid: WeChat user ID

        Returns:
            Staff instance or None
        """
        result = await db.execute(
            select(Staff).filter(Staff.wechat_userid == wechat_userid)
        )
        return result.scalar_one_or_none()

    async def get_by_hotel(
        self,
        db: AsyncSession,
        hotel_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Staff]:
        """
        Get staff by hotel ID

        Args:
            db: Database session
            hotel_id: Hotel ID
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of staff members
        """
        result = await db.execute(
            select(Staff)
            .filter(Staff.hotel_id == hotel_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_available(
        self,
        db: AsyncSession,
        hotel_id: str | None = None,
        role: str | None = None,
        limit: int = 100,
    ) -> list[Staff]:
        """
        Get available staff for assignment

        Args:
            db: Database session
            hotel_id: Filter by hotel ID
            role: Filter by role
            limit: Maximum records to return

        Returns:
            List of available staff
        """
        conditions = [
            Staff.status == "active",
            Staff.is_available == True,  # noqa: E712
        ]

        if hotel_id:
            conditions.append(Staff.hotel_id == hotel_id)
        if role:
            conditions.append(Staff.role == role)

        result = await db.execute(
            select(Staff)
            .filter(and_(*conditions))
            .limit(limit)
        )
        return list(result.scalars().all())


# Create singleton instance
staff = CRUDStaff(Staff)
