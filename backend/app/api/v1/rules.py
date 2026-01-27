"""
Routing Rules Management API endpoints
"""

from typing import Annotated, List
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.models.routing_rule import RoutingRule
from app.crud.routing_rule import routing_rule as rule_crud
from app.schemas.common import APIResponse
from app.dependencies import DBSession
from app.core.exceptions import NotFoundError
from app.services.rule_test_service import rule_test_service

router = APIRouter()


# Schemas
class RuleTestRequest(BaseModel):
    """Request for testing a routing rule"""

    message_content: str = Field(..., description="Message content to test")
    category: str | None = Field(None, description="Optional ticket category")
    priority: str | None = Field(None, description="Optional ticket priority")


class RuleCreateRequest(BaseModel):
    """Request for creating a routing rule"""

    name: str = Field(..., max_length=100, description="Rule name")
    rule_type: str = Field(..., description="Rule type: keyword, category, priority, round_robin, manual")
    keywords: List[str] = Field(default_factory=list, description="Keywords for keyword matching")
    category: str | None = Field(None, description="Category for category matching")
    priority: str | None = Field(None, description="Priority for priority matching")
    target_staff_ids: List[str] = Field(..., description="Target staff IDs for assignment")
    rule_priority: int = Field(default=0, description="Rule priority (higher = more priority)")
    is_active: bool = Field(default=True, description="Whether the rule is active")


class RuleUpdateRequest(BaseModel):
    """Request for updating a routing rule"""

    name: str | None = None
    keywords: List[str] | None = None
    target_staff_ids: List[str] | None = None
    rule_priority: int | None = None
    is_active: bool | None = None


@router.post("/test", response_model=APIResponse[dict])
def test_routing_rule(
    hotel_id: Annotated[str, Query(description="Hotel ID")] = ...,
    request: RuleTestRequest = ...,
    db: Session = Depends(DBSession),
) -> APIResponse[dict]:
    """
    Test which rule would match a message

    Args:
        hotel_id: Hotel ID
        request: Test request with message content and optional filters
        db: Database session

    Returns:
        Test result with matched rule and assigned staff
    """
    result = rule_test_service.test_message(
        db,
        hotel_id,
        request.message_content,
        request.category,
        request.priority,
    )
    return APIResponse(data=result)


@router.get("/summary", response_model=APIResponse[List[dict]])
def get_rules_summary(
    hotel_id: Annotated[str, Query(description="Hotel ID")] = ...,
    db: Session = Depends(DBSession),
) -> APIResponse[List[dict]]:
    """
    Get summary of all routing rules for a hotel

    Args:
        hotel_id: Hotel ID
        db: Database session

    Returns:
        List of rule summaries
    """
    rules = rule_test_service.get_rule_summary(db, hotel_id)
    return APIResponse(data=rules)


@router.post("", response_model=APIResponse)
def create_routing_rule(
    hotel_id: Annotated[str, Query(description="Hotel ID")] = ...,
    request: RuleCreateRequest = ...,
    db: Session = Depends(DBSession),
) -> APIResponse:
    """
    Create a new routing rule

    Args:
        hotel_id: Hotel ID
        request: Rule creation request
        db: Database session

    Returns:
        Created rule
    """
    import json

    rule_data = {
        "hotel_id": hotel_id,
        "name": request.name,
        "rule_type": request.rule_type,
        "keywords": json.dumps(request.keywords) if request.keywords else None,
        "category": request.category,
        "priority": request.priority,
        "target_staff_ids": json.dumps(request.target_staff_ids),
        "priority_level": request.rule_priority,
        "is_active": request.is_active,
    }

    rule = rule_crud.create(db, rule_data)
    return APIResponse(data={"id": rule.id, "name": rule.name})


@router.put("/{rule_id}", response_model=APIResponse)
def update_routing_rule(
    rule_id: str,
    request: RuleUpdateRequest,
    db: Session = Depends(DBSession),
) -> APIResponse:
    """
    Update a routing rule

    Args:
        rule_id: Rule ID
        request: Update request
        db: Database session

    Returns:
        Updated rule
    """
    import json

    rule = rule_crud.get(db, rule_id)
    if not rule:
        raise NotFoundError("Rule not found")

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.keywords is not None:
        update_data["keywords"] = json.dumps(request.keywords)
    if request.target_staff_ids is not None:
        update_data["target_staff_ids"] = json.dumps(request.target_staff_ids)
    if request.rule_priority is not None:
        update_data["priority_level"] = request.rule_priority
    if request.is_active is not None:
        update_data["is_active"] = request.is_active

    updated = rule_crud.update(db, rule, update_data)
    return APIResponse(data={"id": updated.id, "name": updated.name})


@router.delete("/{rule_id}", response_model=APIResponse)
def delete_routing_rule(
    rule_id: str,
    db: Session = Depends(DBSession),
) -> APIResponse:
    """
    Delete a routing rule

    Args:
        rule_id: Rule ID
        db: Database session

    Returns:
        Success response
    """
    rule = rule_crud.delete(db, rule_id)
    if not rule:
        raise NotFoundError("Rule not found")

    return APIResponse(message="Rule deleted successfully")


@router.post("/{rule_id}/reorder", response_model=APIResponse)
def reorder_rule(
    rule_id: str,
    new_priority: Annotated[int, Body(description="New priority level")] = ...,
    db: Session = Depends(DBSession),
) -> APIResponse:
    """
    Reorder a rule by changing its priority

    Args:
        rule_id: Rule ID
        new_priority: New priority level
        db: Database session

    Returns:
        Updated rule
    """
    rule = rule_crud.get(db, rule_id)
    if not rule:
        raise NotFoundError("Rule not found")

    updated = rule_crud.update(db, rule, {"priority_level": new_priority})
    return APIResponse(data={"id": updated.id, "priority_level": updated.priority_level})
