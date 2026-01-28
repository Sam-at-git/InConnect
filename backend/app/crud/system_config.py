"""
System Config CRUD operations
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_config import SystemConfig
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate


class SystemConfigCRUD:
    """CRUD operations for system configurations"""

    async def get(self, db: AsyncSession, id: str) -> Optional[SystemConfig]:
        """Get config by ID"""
        result = await db.execute(select(SystemConfig).filter(SystemConfig.id == id))
        return result.scalar_one_or_none()

    async def get_by_key(self, db: AsyncSession, key: str) -> Optional[SystemConfig]:
        """Get config by key"""
        result = await db.execute(select(SystemConfig).filter(SystemConfig.key == key))
        return result.scalar_one_or_none()

    async def get_by_category(self, db: AsyncSession, category: str, skip: int = 0, limit: int = 100):
        """Get configs by category"""
        result = await db.execute(
            select(SystemConfig)
            .filter(SystemConfig.category == category)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        """Get all configs"""
        result = await db.execute(select(SystemConfig).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: SystemConfigCreate) -> SystemConfig:
        """Create new config"""
        db_obj = SystemConfig(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: SystemConfig, obj_in: SystemConfigUpdate | dict
    ) -> SystemConfig:
        """Update config"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> Optional[SystemConfig]:
        """Delete config"""
        result = await db.execute(select(SystemConfig).filter(SystemConfig.id == id))
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj

    async def upsert(
        self, db: AsyncSession, key: str, value: dict, category: str = "general", description: str | None = None
    ) -> SystemConfig:
        """Create or update config by key"""
        obj = await self.get_by_key(db, key)
        if obj:
            obj.value = value
            if description is not None:
                obj.description = description
            await db.flush()
            await db.refresh(obj)
            return obj
        else:
            return await self.create(
                db,
                SystemConfigCreate(key=key, value=value, category=category, description=description),
            )


system_config = SystemConfigCRUD()
