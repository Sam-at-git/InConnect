"""
CRUD operations for Hotel model
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.hotel import Hotel
from app.schemas.hotel import HotelCreate, HotelUpdate


class CRUDHotel(CRUDBase[Hotel, HotelCreate, HotelUpdate]):
    """CRUD operations for Hotel"""

    async def get_by_corp_id(self, db: AsyncSession, corp_id: str) -> Hotel | None:
        """
        Get hotel by WeChat corporate ID

        Args:
            db: Database session
            corp_id: WeChat corporate ID

        Returns:
            Hotel instance or None
        """
        result = await db.execute(
            select(Hotel).filter(Hotel.corp_id == corp_id)
        )
        return result.scalar_one_or_none()

    async def get_active(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Hotel]:
        """
        Get active hotels

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of active hotels
        """
        result = await db.execute(
            select(Hotel)
            .filter(Hotel.status == "active")
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_active(self, db: AsyncSession) -> int:
        """
        Count active hotels

        Args:
            db: Database session

        Returns:
            Count of active hotels
        """
        from sqlalchemy import func

        result = await db.execute(
            select(func.count()).select_from(Hotel).filter(Hotel.status == "active")
        )
        return result.scalar()


# Create singleton instance
hotel = CRUDHotel(Hotel)
