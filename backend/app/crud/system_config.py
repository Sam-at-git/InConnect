"""
System Config CRUD operations
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.system_config import SystemConfig
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate


class SystemConfigCRUD:
    """CRUD operations for system configurations"""

    def get(self, db: Session, id: str) -> Optional[SystemConfig]:
        """Get config by ID"""
        return db.query(SystemConfig).filter(SystemConfig.id == id).first()

    def get_by_key(self, db: Session, key: str) -> Optional[SystemConfig]:
        """Get config by key"""
        return db.query(SystemConfig).filter(SystemConfig.key == key).first()

    def get_by_category(self, db: Session, category: str, skip: int = 0, limit: int = 100):
        """Get configs by category"""
        return (
            db.query(SystemConfig)
            .filter(SystemConfig.category == category)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        """Get all configs"""
        return db.query(SystemConfig).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: SystemConfigCreate) -> SystemConfig:
        """Create new config"""
        db_obj = SystemConfig(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: SystemConfig, obj_in: SystemConfigUpdate | dict
    ) -> SystemConfig:
        """Update config"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: str) -> Optional[SystemConfig]:
        """Delete config"""
        obj = db.query(SystemConfig).filter(SystemConfig.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def upsert(
        self, db: Session, key: str, value: dict, category: str = "general", description: str | None = None
    ) -> SystemConfig:
        """Create or update config by key"""
        obj = self.get_by_key(db, key)
        if obj:
            obj.value = value
            if description is not None:
                obj.description = description
            db.commit()
            db.refresh(obj)
            return obj
        else:
            return self.create(
                db,
                SystemConfigCreate(key=key, value=value, category=category, description=description),
            )


system_config = SystemConfigCRUD()
