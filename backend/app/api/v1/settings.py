"""
System Settings API endpoints
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.crud.system_config import system_config
from app.schemas.system_config import (
    SystemConfigCreate,
    SystemConfigUpdate,
    SystemConfigResponse,
    TicketCategoryConfig,
    PriorityConfig,
)
from app.schemas.common import APIResponse
from app.dependencies import DBSession
from app.core.exceptions import NotFoundError

router = APIRouter()


# Default configurations
DEFAULT_TICKET_CATEGORIES = [
    {"key": "maintenance", "label": "维修", "color": "red", "sla_hours": 4},
    {"key": "housekeeping", "label": "客房", "color": "blue", "sla_hours": 2},
    {"key": "service", "label": "服务", "color": "green", "sla_hours": 1},
    {"key": "complaint", "label": "投诉", "color": "orange", "sla_hours": 1},
    {"key": "inquiry", "label": "咨询", "color": "cyan", "sla_hours": 2},
    {"key": "other", "label": "其他", "color": "default", "sla_hours": 4},
]

DEFAULT_PRIORITIES = [
    {"key": "P1", "label": "紧急", "color": "red", "urgency_hours": 1},
    {"key": "P2", "label": "高", "color": "orange", "urgency_hours": 2},
    {"key": "P3", "label": "中", "color": "blue", "urgency_hours": 4},
    {"key": "P4", "label": "低", "color": "default", "urgency_hours": 8},
]


@router.get("/configs", response_model=APIResponse[List[SystemConfigResponse]])
def list_configs(
    db: Session = Depends(DBSession),
    category: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> APIResponse[List[SystemConfigResponse]]:
    """List system configurations"""
    if category:
        configs = system_config.get_by_category(db, category, skip, limit)
    else:
        configs = system_config.get_multi(db, skip, limit)

    return APIResponse(data=[SystemConfigResponse.model_validate(c) for c in configs])


@router.get("/configs/{config_id}", response_model=APIResponse[SystemConfigResponse])
def get_config(
    config_id: str,
    db: Session = Depends(DBSession),
) -> APIResponse[SystemConfigResponse]:
    """Get configuration by ID"""
    config = system_config.get(db, config_id)
    if not config:
        raise NotFoundError("Configuration not found")

    return APIResponse(data=SystemConfigResponse.model_validate(config))


@router.post("/configs", response_model=APIResponse[SystemConfigResponse])
def create_config(
    config_in: SystemConfigCreate,
    db: Session = Depends(DBSession),
) -> APIResponse[SystemConfigResponse]:
    """Create new configuration"""
    # Check if key already exists
    existing = system_config.get_by_key(db, config_in.key)
    if existing:
        raise HTTPException(status_code=400, detail="Configuration key already exists")

    config = system_config.create(db, config_in)
    return APIResponse(data=SystemConfigResponse.model_validate(config))


@router.put("/configs/{config_id}", response_model=APIResponse[SystemConfigResponse])
def update_config(
    config_id: str,
    config_in: SystemConfigUpdate,
    db: Session = Depends(DBSession),
) -> APIResponse[SystemConfigResponse]:
    """Update configuration"""
    config = system_config.get(db, config_id)
    if not config:
        raise NotFoundError("Configuration not found")

    updated = system_config.update(db, config, config_in)
    return APIResponse(data=SystemConfigResponse.model_validate(updated))


@router.delete("/configs/{config_id}", response_model=APIResponse)
def delete_config(
    config_id: str,
    db: Session = Depends(DBSession),
) -> APIResponse:
    """Delete configuration"""
    config = system_config.delete(db, config_id)
    if not config:
        raise NotFoundError("Configuration not found")

    return APIResponse(message="Configuration deleted successfully")


# Ticket Categories
@router.get("/categories", response_model=APIResponse[List[TicketCategoryConfig]])
def get_ticket_categories(
    db: Session = Depends(DBSession),
) -> APIResponse[List[TicketCategoryConfig]]:
    """Get ticket categories configuration"""
    config = system_config.get_by_key(db, "ticket_categories")
    if config and config.value:
        return APIResponse(data=config.value)

    # Return defaults if not configured
    return APIResponse(data=DEFAULT_TICKET_CATEGORIES)


@router.put("/categories", response_model=APIResponse[List[TicketCategoryConfig]])
def update_ticket_categories(
    categories: List[TicketCategoryConfig],
    db: Session = Depends(DBSession),
) -> APIResponse[List[TicketCategoryConfig]]:
    """Update ticket categories configuration"""
    system_config.upsert(
        db,
        "ticket_categories",
        [c.model_dump() for c in categories],
        category="ticket",
        description="Ticket categories configuration",
    )

    return APIResponse(data=categories)


# Priorities
@router.get("/priorities", response_model=APIResponse[List[PriorityConfig]])
def get_priorities(
    db: Session = Depends(DBSession),
) -> APIResponse[List[PriorityConfig]]:
    """Get priority levels configuration"""
    config = system_config.get_by_key(db, "priority_levels")
    if config and config.value:
        return APIResponse(data=config.value)

    # Return defaults if not configured
    return APIResponse(data=DEFAULT_PRIORITIES)


@router.put("/priorities", response_model=APIResponse[List[PriorityConfig]])
def update_priorities(
    priorities: List[PriorityConfig],
    db: Session = Depends(DBSession),
) -> APIResponse[List[PriorityConfig]]:
    """Update priority levels configuration"""
    system_config.upsert(
        db,
        "priority_levels",
        [p.model_dump() for p in priorities],
        category="ticket",
        description="Priority levels configuration",
    )

    return APIResponse(data=priorities)


# System Info
@router.get("/info", response_model=APIResponse[dict])
def get_system_info(
    db: Session = Depends(DBSession),
) -> APIResponse[dict]:
    """Get system information"""
    from app.models.ticket import Ticket
    from app.models.staff import Staff
    from app.models.conversation import Conversation
    from app.models.message import Message

    # Count records
    ticket_count = db.query(Ticket).count()
    staff_count = db.query(Staff).count()
    conversation_count = db.query(Conversation).count()
    message_count = db.query(Message).count()

    return APIResponse(data={
        "version": "0.1.0",
        "name": "迎客通 InConnect",
        "stats": {
            "tickets": ticket_count,
            "staff": staff_count,
            "conversations": conversation_count,
            "messages": message_count,
        },
    })
