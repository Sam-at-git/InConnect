"""
Ticket API endpoints
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.ticket import ticket as ticket_crud
from app.crud.ticket_timeline import ticket_timeline as timeline_crud
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
    TicketAssignRequest,
    TicketStatusUpdateRequest,
)
from app.schemas.ticket_timeline import TicketTimelineResponse
from app.schemas.common import APIResponse, PaginatedData
from app.core.auth import get_current_user_id
from app.dependencies import DBSession
from app.core.exceptions import NotFoundError, ValidationError
from app.models.ticket import TicketStatus
from app.services.routing_service import routing_service

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedData[TicketResponse]])
async def list_tickets(
    db: DBSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    hotel_id: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
) -> APIResponse[PaginatedData[TicketResponse]]:
    """
    List tickets with pagination and filters

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum records per page
        hotel_id: Filter by hotel ID
        status: Filter by status
        priority: Filter by priority
        category: Filter by category

    Returns:
        Paginated list of tickets
    """
    # Get tickets based on filters
    if hotel_id:
        tickets = await ticket_crud.get_by_hotel(db, hotel_id, skip, limit)
        # Count would need to be added
        total = len(tickets)  # Simplified for MVP
    elif status:
        tickets = await ticket_crud.get_by_status(db, status, skip, limit)
        total = len(tickets)
    else:
        tickets = await ticket_crud.get_multi(db, skip, limit)
        total = await ticket_crud.count(db)

    # Create paginated response
    page = skip // limit + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 0
    paginated_data = PaginatedData.create(
        items=[TicketResponse.model_validate(t) for t in tickets],
        total=total,
        page=page,
        page_size=limit,
    )

    return APIResponse(data=paginated_data)


@router.get("/open", response_model=APIResponse[list[TicketResponse]])
async def get_open_tickets(
    db: DBSession,
    hotel_id: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> APIResponse[list[TicketResponse]]:
    """
    Get open (not resolved/closed) tickets

    Args:
        db: Database session
        hotel_id: Filter by hotel ID
        limit: Maximum records to return

    Returns:
        List of open tickets
    """
    tickets = await ticket_crud.get_open_tickets(db, hotel_id, limit)
    return APIResponse(data=[TicketResponse.model_validate(t) for t in tickets])


@router.get("/{ticket_id}", response_model=APIResponse[TicketResponse])
async def get_ticket(
    ticket_id: str,
    db: DBSession,
) -> APIResponse[TicketResponse]:
    """
    Get ticket by ID with relations

    Args:
        ticket_id: Ticket ID
        db: Database session

    Returns:
        Ticket details
    """
    ticket = await ticket_crud.get_with_relations(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket not found")

    return APIResponse(data=TicketResponse.model_validate(ticket))


@router.get("/{ticket_id}/timeline", response_model=APIResponse[list[TicketTimelineResponse]])
async def get_ticket_timeline(
    ticket_id: str,
    db: DBSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> APIResponse[list[TicketTimelineResponse]]:
    """
    Get ticket timeline entries

    Args:
        ticket_id: Ticket ID
        db: Database session
        limit: Maximum records to return

    Returns:
        List of timeline entries
    """
    ticket = await ticket_crud.get(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket not found")

    timelines = await timeline_crud.get_by_ticket(db, ticket_id, limit)
    return APIResponse(data=[
        TicketTimelineResponse.model_validate(t) for t in timelines
    ])


@router.post("", response_model=APIResponse[TicketResponse])
async def create_ticket(
    ticket_in: TicketCreate,
    db: DBSession,
    user_id: str = Depends(get_current_user_id),
) -> APIResponse[TicketResponse]:
    """
    Create new ticket

    Args:
        ticket_in: Ticket creation data
        db: Database session
        user_id: Current user ID (from JWT)

    Returns:
        Created ticket
    """
    ticket = await ticket_crud.create(db, ticket_in)

    # Auto-assign if requested
    if ticket_in.auto_assign:
        assigned = await routing_service.auto_assign_ticket(db, ticket)
        if assigned:
            # Create timeline entry for auto-assignment
            await timeline_crud.create_timeline_entry(
                db,
                ticket.id,
                "assigned",
                None,
                new_value=ticket.assigned_to,
                comment="Automatically assigned based on routing rules",
            )

    # Create timeline entry
    await timeline_crud.create_timeline_entry(
        db,
        ticket.id,
        "created",
        user_id,
        new_value=ticket.title,
        comment=f"Ticket created: {ticket.title}",
    )

    return APIResponse(
        message="Ticket created successfully",
        data=TicketResponse.model_validate(ticket),
    )


@router.put("/{ticket_id}", response_model=APIResponse[TicketResponse])
async def update_ticket(
    ticket_id: str,
    ticket_in: TicketUpdate,
    db: DBSession,
    user_id: str = Depends(get_current_user_id),
) -> APIResponse[TicketResponse]:
    """
    Update ticket

    Args:
        ticket_id: Ticket ID
        ticket_in: Ticket update data
        db: Database session
        user_id: Current user ID (from JWT)

    Returns:
        Updated ticket
    """
    ticket = await ticket_crud.get(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket not found")

    updated_ticket = await ticket_crud.update(db, ticket, ticket_in)
    return APIResponse(
        message="Ticket updated successfully",
        data=TicketResponse.model_validate(updated_ticket),
    )


@router.post("/{ticket_id}/assign", response_model=APIResponse[TicketResponse])
async def assign_ticket(
    ticket_id: str,
    assign_in: TicketAssignRequest,
    db: DBSession,
    user_id: str = Depends(get_current_user_id),
) -> APIResponse[TicketResponse]:
    """
    Assign ticket to staff member

    Args:
        ticket_id: Ticket ID
        assign_in: Assignment request
        db: Database session
        user_id: Current user ID (from JWT)

    Returns:
        Updated ticket
    """
    ticket = await ticket_crud.get(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket not found")

    old_status = ticket.status
    old_assignee = ticket.assigned_to

    # Update ticket
    updated_ticket = await ticket_crud.update(
        db,
        ticket,
        {"assigned_to": assign_in.staff_id, "status": TicketStatus.ASSIGNED.value},
    )

    # Create timeline entries
    if old_assignee != assign_in.staff_id:
        await timeline_crud.create_timeline_entry(
            db,
            ticket_id,
            "assigned",
            user_id,
            old_value=old_assignee or "unassigned",
            new_value=assign_in.staff_id,
            comment=assign_in.comment,
        )

    if old_status != TicketStatus.ASSIGNED.value:
        await timeline_crud.create_timeline_entry(
            db,
            ticket_id,
            "status_changed",
            user_id,
            old_value=old_status,
            new_value=TicketStatus.ASSIGNED.value,
            comment="Ticket status changed to assigned",
        )

    return APIResponse(
        message="Ticket assigned successfully",
        data=TicketResponse.model_validate(updated_ticket),
    )


@router.post("/{ticket_id}/status", response_model=APIResponse[TicketResponse])
async def update_ticket_status(
    ticket_id: str,
    status_in: TicketStatusUpdateRequest,
    db: DBSession,
    user_id: str = Depends(get_current_user_id),
) -> APIResponse[TicketResponse]:
    """
    Update ticket status

    Args:
        ticket_id: Ticket ID
        status_in: Status update request
        db: Database session
        user_id: Current user ID (from JWT)

    Returns:
        Updated ticket
    """
    ticket = await ticket_crud.get(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket not found")

    old_status = ticket.status

    # Validate status transition
    if not _is_valid_status_transition(old_status, status_in.status):
        raise ValidationError(
            f"Invalid status transition from {old_status} to {status_in.status}"
        )

    # Update ticket status
    update_data = {"status": status_in.status}

    # Set timestamps based on status
    if status_in.status == TicketStatus.RESOLVED.value:
        update_data["resolved_at"] = datetime.utcnow()
    elif status_in.status == TicketStatus.CLOSED.value:
        update_data["closed_at"] = datetime.utcnow()

    updated_ticket = await ticket_crud.update(db, ticket, update_data)

    # Create timeline entry
    await timeline_crud.create_timeline_entry(
        db,
        ticket_id,
        "status_changed",
        user_id,
        old_value=old_status,
        new_value=status_in.status,
        comment=status_in.comment,
    )

    # Create specific timeline entry based on status
    if status_in.status == TicketStatus.RESOLVED.value:
        await timeline_crud.create_timeline_entry(
            db,
            ticket_id,
            "resolved",
            user_id,
            comment=status_in.comment,
        )
    elif status_in.status == TicketStatus.CLOSED.value:
        await timeline_crud.create_timeline_entry(
            db,
            ticket_id,
            "closed",
            user_id,
            comment=status_in.comment,
        )

    return APIResponse(
        message=f"Ticket status updated to {status_in.status}",
        data=TicketResponse.model_validate(updated_ticket),
    )


@router.delete("/{ticket_id}", response_model=APIResponse)
async def delete_ticket(
    ticket_id: str,
    db: DBSession,
    user_id: str = Depends(get_current_user_id),
) -> APIResponse:
    """
    Delete ticket (soft delete by closing)

    Args:
        ticket_id: Ticket ID
        db: Database session
        user_id: Current user ID (from JWT)

    Returns:
        Success response
    """
    ticket = await ticket_crud.get(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket not found")

    deleted = await ticket_crud.delete(db, ticket_id)
    if not deleted:
        raise ValidationError("Failed to delete ticket")

    return APIResponse(message="Ticket deleted successfully")


def _is_valid_status_transition(old_status: str, new_status: str) -> bool:
    """
    Validate ticket status transition

    Args:
        old_status: Current status
        new_status: Desired new status

    Returns:
        True if transition is valid
    """
    # Define valid transitions
    valid_transitions = {
        TicketStatus.PENDING.value: [
            TicketStatus.ASSIGNED.value,
            TicketStatus.CLOSED.value,
        ],
        TicketStatus.ASSIGNED.value: [
            TicketStatus.IN_PROGRESS.value,
            TicketStatus.CLOSED.value,
        ],
        TicketStatus.IN_PROGRESS.value: [
            TicketStatus.RESOLVED.value,
            TicketStatus.CLOSED.value,
        ],
        TicketStatus.RESOLVED.value: [
            TicketStatus.CLOSED.value,
            TicketStatus.REOPENED.value,
        ],
        TicketStatus.CLOSED.value: [
            TicketStatus.REOPENED.value,
        ],
        TicketStatus.REOPENED.value: [
            TicketStatus.ASSIGNED.value,
            TicketStatus.IN_PROGRESS.value,
            TicketStatus.CLOSED.value,
        ],
    }

    return new_status in valid_transitions.get(old_status, [])
