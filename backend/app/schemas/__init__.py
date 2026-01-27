"""Pydantic schemas"""

from app.schemas.common import APIResponse, PaginatedData, PaginatedResponse
from app.schemas.hotel import (
    HotelBase,
    HotelCreate,
    HotelUpdate,
    HotelResponse,
    HotelListResponse,
)
from app.schemas.staff import (
    StaffBase,
    StaffCreate,
    StaffUpdate,
    StaffResponse,
    StaffListResponse,
)
from app.schemas.ticket import (
    TicketBase,
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
    TicketAssignRequest,
    TicketStatusUpdateRequest,
)
from app.schemas.ticket_timeline import (
    TicketTimelineBase,
    TicketTimelineCreate,
    TicketTimelineResponse,
)
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenPayload,
)

__all__ = [
    "APIResponse",
    "PaginatedData",
    "PaginatedResponse",
    "HotelBase",
    "HotelCreate",
    "HotelUpdate",
    "HotelResponse",
    "HotelListResponse",
    "StaffBase",
    "StaffCreate",
    "StaffUpdate",
    "StaffResponse",
    "StaffListResponse",
    "TicketBase",
    "TicketCreate",
    "TicketUpdate",
    "TicketResponse",
    "TicketListResponse",
    "TicketAssignRequest",
    "TicketStatusUpdateRequest",
    "TicketTimelineBase",
    "TicketTimelineCreate",
    "TicketTimelineResponse",
    "LoginRequest",
    "LoginResponse",
    "TokenPayload",
]
