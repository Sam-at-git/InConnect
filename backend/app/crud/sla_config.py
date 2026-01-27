"""
CRUD operations for SLA Config model
"""

from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.sla_config import SLAConfig
from app.schemas.sla import SLAConfigCreate, SLAConfigUpdate


class CRUDSLAConfig(CRUDBase[SLAConfig, SLAConfigCreate, SLAConfigUpdate]):
    """CRUD operations for SLA Config"""

    async def get_by_hotel(
        self,
        db: AsyncSession,
        hotel_id: str,
        active_only: bool = True,
    ) -> list[SLAConfig]:
        """
        Get SLA configs by hotel ID

        Args:
            db: Database session
            hotel_id: Hotel ID
            active_only: Only return active configs

        Returns:
            List of SLA configs
        """
        conditions = [SLAConfig.hotel_id == hotel_id]
        if active_only:
            conditions.append(SLAConfig.is_active == True)

        result = await db.execute(
            select(SLAConfig)
            .filter(and_(*conditions))
            .order_by(SLAConfig.priority.asc())
        )
        return list(result.scalars().all())

    async def get_by_hotel_and_priority(
        self,
        db: AsyncSession,
        hotel_id: str | None,
        priority: str,
    ) -> SLAConfig | None:
        """
        Get SLA config by hotel ID and priority

        Args:
            db: Database session
            hotel_id: Hotel ID (None for default config)
            priority: Priority level

        Returns:
            SLA config or None
        """
        # First try to get hotel-specific config
        if hotel_id:
            result = await db.execute(
                select(SLAConfig)
                .filter(
                    and_(
                        SLAConfig.hotel_id == hotel_id,
                        SLAConfig.priority == priority,
                        SLAConfig.is_active == True,
                    )
                )
                .order_by(SLAConfig.created_at.desc())
                .limit(1)
            )
            config = result.scalar_one_or_none()
            if config:
                return config

        # Fall back to default config (hotel_id is None)
        result = await db.execute(
            select(SLAConfig)
            .filter(
                and_(
                    SLAConfig.hotel_id.is_(None),
                    SLAConfig.priority == priority,
                    SLAConfig.is_active == True,
                )
            )
            .order_by(SLAConfig.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all_active(
        self,
        db: AsyncSession,
    ) -> list[SLAConfig]:
        """
        Get all active SLA configs

        Args:
            db: Database session

        Returns:
            List of active SLA configs
        """
        result = await db.execute(
            select(SLAConfig)
            .filter(SLAConfig.is_active == True)
            .order_by(SLAConfig.hotel_id.asc(), SLAConfig.priority.asc())
        )
        return list(result.scalars().all())

    async def get_priorities_for_hotel(
        self,
        db: AsyncSession,
        hotel_id: str,
    ) -> dict[str, dict[str, int]]:
        """
        Get all SLA priorities for a hotel as a dictionary

        Args:
            db: Database session
            hotel_id: Hotel ID

        Returns:
            Dictionary mapping priority to {response_minutes, resolution_minutes}
        """
        configs = await self.get_by_hotel(db, hotel_id, active_only=True)
        result = {}

        for config in configs:
            # Also check if there's a default config for this priority
            default_config = await self.get_by_hotel_and_priority(db, None, config.priority)
            if default_config and default_config.id != config.id:
                # Use hotel-specific config
                result[config.priority] = {
                    "response_minutes": config.response_minutes,
                    "resolution_minutes": config.resolution_minutes,
                }
            else:
                # Use default config
                result[config.priority] = {
                    "response_minutes": config.response_minutes,
                    "resolution_minutes": config.resolution_minutes,
                }

        # Fill in missing priorities with defaults
        all_priorities = ["P1", "P2", "P3", "P4"]
        for priority in all_priorities:
            if priority not in result:
                default_config = await self.get_by_hotel_and_priority(db, None, priority)
                if default_config:
                    result[priority] = {
                        "response_minutes": default_config.response_minutes,
                        "resolution_minutes": default_config.resolution_minutes,
                    }

        return result


# Create singleton instance
sla_config = CRUDSLAConfig(SLAConfig)
