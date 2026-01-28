"""
Routing Rules Management API endpoints
"""

from typing import List
from pydantic import BaseModel, Field

from fastapi import APIRouter, Query

from app.schemas.common import APIResponse

router = APIRouter()


# Schemas
class RuleTestRequest(BaseModel):
    """Request for testing a routing rule"""
    message_content: str = Field(..., description="Message content to test")
    category: str | None = Field(None, description="Optional ticket category")
    priority: str | None = Field(None, description="Optional ticket priority")


class RuleSummary(BaseModel):
    """Rule summary for display"""
    id: str
    name: str
    type: str
    keywords: List[str] | None = None
    category: str | None = None
    priority: str | None = None
    target_staff_count: int = 0
    rule_priority: int = 0
    is_active: bool = True


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


# In-memory storage for MVP (would be database in production)
_rules: List[dict] = [
    {
        "id": "rule-001",
        "name": "维修关键词匹配",
        "type": "keyword",
        "keywords": ["维修", "坏了", "不工作", "漏水"],
        "category": None,
        "priority": None,
        "target_staff_count": 2,
        "rule_priority": 10,
        "is_active": True,
    },
    {
        "id": "rule-002",
        "name": "投诉优先处理",
        "type": "category",
        "keywords": None,
        "category": "complaint",
        "priority": None,
        "target_staff_count": 1,
        "rule_priority": 20,
        "is_active": True,
    },
]


@router.get("/summary", response_model=APIResponse[List[RuleSummary]])
async def get_rules_summary(
    hotel_id: str = Query(..., description="Hotel ID"),
) -> APIResponse[List[RuleSummary]]:
    """
    Get summary of all routing rules for a hotel
    """
    return APIResponse(data=_rules)


@router.post("/test", response_model=APIResponse[dict])
async def test_routing_rule(
    hotel_id: str = Query(..., description="Hotel ID"),
    request: RuleTestRequest = ...,
) -> APIResponse[dict]:
    """
    Test which rule would match a message
    """
    # Simple keyword matching for MVP
    matched_rule = None
    for rule in _rules:
        if rule["type"] == "keyword" and rule["keywords"]:
            for keyword in rule["keywords"]:
                if keyword in request.message_content:
                    matched_rule = rule
                    break
        if matched_rule:
            break

    if not matched_rule and _rules:
        matched_rule = _rules[0]

    return APIResponse(data={
        "matched_rule": matched_rule,
        "assigned_staff": [
            {"id": "staff-001", "name": "测试员工"},
        ] if matched_rule else [],
    })


@router.post("", response_model=APIResponse[dict])
async def create_routing_rule(
    hotel_id: str = Query(..., description="Hotel ID"),
    request: RuleCreateRequest = ...,
) -> APIResponse[dict]:
    """
    Create a new routing rule
    """
    import uuid
    new_rule = {
        "id": f"rule-{uuid.uuid4().hex[:6]}",
        "name": request.name,
        "type": request.rule_type,
        "keywords": request.keywords,
        "category": request.category,
        "priority": request.priority,
        "target_staff_count": len(request.target_staff_ids),
        "rule_priority": request.rule_priority,
        "is_active": request.is_active,
    }
    _rules.append(new_rule)
    return APIResponse(data=new_rule)


@router.put("/{rule_id}", response_model=APIResponse[dict])
async def update_routing_rule(
    rule_id: str,
    request: RuleCreateRequest,
) -> APIResponse[dict]:
    """
    Update a routing rule
    """
    for rule in _rules:
        if rule["id"] == rule_id:
            rule.update({
                "name": request.name,
                "keywords": request.keywords,
                "rule_priority": request.rule_priority,
                "is_active": request.is_active,
            })
            return APIResponse(data=rule)

    return APIResponse(code=404, message="Rule not found")


@router.delete("/{rule_id}", response_model=APIResponse)
async def delete_routing_rule(
    rule_id: str,
) -> APIResponse:
    """
    Delete a routing rule
    """
    global _rules
    _rules = [r for r in _rules if r["id"] != rule_id]
    return APIResponse(message="Rule deleted successfully")


@router.post("/{rule_id}/reorder", response_model=APIResponse[dict])
async def reorder_rule(
    rule_id: str,
    new_priority: int,
) -> APIResponse[dict]:
    """
    Reorder a rule by changing its priority
    """
    for rule in _rules:
        if rule["id"] == rule_id:
            rule["rule_priority"] = new_priority
            return APIResponse(data=rule)

    return APIResponse(code=404, message="Rule not found")
