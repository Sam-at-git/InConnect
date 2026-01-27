"""
Batch operation schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class BatchAssignRequest(BaseModel):
    """Request for batch assigning tickets"""

    ticket_ids: List[str] = Field(..., min_items=1, max_items=100)
    staff_id: str
    comment: Optional[str] = None


class BatchStatusUpdateRequest(BaseModel):
    """Request for batch updating ticket status"""

    ticket_ids: List[str] = Field(..., min_items=1, max_items=100)
    status: str
    comment: Optional[str] = None


class BatchOperationResult(BaseModel):
    """Result of batch operation"""

    success_count: int
    failed_count: int
    failed_ids: List[str]
    errors: List[str]


class TicketExportRequest(BaseModel):
    """Request for exporting tickets"""

    hotel_id: str
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    format: str = Field(default="csv", pattern="^(csv|excel)$")
