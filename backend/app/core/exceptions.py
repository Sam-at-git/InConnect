"""
Custom business exceptions
"""

from typing import Any


# Business error codes
ERROR_CODES: dict[str, tuple[int, str]] = {
    # Common errors (1000-1999)
    "INVALID_PARAMS": (1001, "Invalid parameters"),
    "NOT_FOUND": (1002, "Resource not found"),
    "ALREADY_EXISTS": (1003, "Resource already exists"),
    "PERMISSION_DENIED": (1004, "Permission denied"),
    "UNAUTHORIZED": (1005, "Unauthorized access"),
    "RATE_LIMIT": (1006, "Rate limit exceeded"),
    # Ticket errors (2000-2999)
    "TICKET_NOT_FOUND": (2001, "Ticket not found"),
    "TICKET_STATUS_ERROR": (2002, "Invalid ticket status transition"),
    "TICKET_ASSIGNED": (2003, "Ticket already assigned"),
    "TICKET_CLOSED": (2004, "Ticket is closed"),
    # Message errors (3000-3999)
    "MESSAGE_SEND_FAILED": (3001, "Failed to send message"),
    "MESSAGE_NOT_FOUND": (3002, "Message not found"),
    # Conversation errors (4000-4999)
    "CONVERSATION_NOT_FOUND": (4001, "Conversation not found"),
    "CONVERSATION_CLOSED": (4002, "Conversation is closed"),
    # Staff errors (5000-5999)
    "STAFF_NOT_FOUND": (5001, "Staff not found"),
    "STAFF_UNAVAILABLE": (5002, "Staff is unavailable"),
    # Hotel errors (6000-6999)
    "HOTEL_NOT_FOUND": (6001, "Hotel not found"),
    "HOTEL_INACTIVE": (6002, "Hotel is inactive"),
}


class BusinessException(Exception):
    """
    Custom business exception

    Attributes:
        code: Error code
        message: Error message
        details: Additional error details
    """

    def __init__(
        self,
        code: int,
        message: str,
        details: Any | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


def get_error(error_key: str) -> tuple[int, str]:
    """
    Get error code and message by key

    Args:
        error_key: Error key from ERROR_CODES

    Returns:
        Tuple of (code, message)
    """
    return ERROR_CODES.get(error_key, (9999, "Unknown error"))


class ValidationError(BusinessException):
    """Validation error exception"""

    def __init__(self, message: str = "Validation failed", details: Any | None = None) -> None:
        code, _ = get_error("INVALID_PARAMS")
        super().__init__(code, message, details)


class NotFoundError(BusinessException):
    """Resource not found exception"""

    def __init__(self, message: str = "Resource not found", details: Any | None = None) -> None:
        code, _ = get_error("NOT_FOUND")
        super().__init__(code, message, details)


class PermissionDeniedError(BusinessException):
    """Permission denied exception"""

    def __init__(self, message: str = "Permission denied", details: Any | None = None) -> None:
        code, _ = get_error("PERMISSION_DENIED")
        super().__init__(code, message, details)


class UnauthorizedError(BusinessException):
    """Unauthorized access exception"""

    def __init__(self, message: str = "Unauthorized access", details: Any | None = None) -> None:
        code, _ = get_error("UNAUTHORIZED")
        super().__init__(code, message, details)
