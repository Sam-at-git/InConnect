"""
Common Pydantic schemas for API responses
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Unified API response format

    Attributes:
        code: Business status code (0 for success)
        message: Response message
        data: Response data
    """

    code: int = Field(default=0, description="Business status code, 0 for success")
    message: str = Field(default="success", description="Response message")
    data: T | None = Field(default=None, description="Response data")

    class Config:
        """Pydantic config"""

        arbitrary_types_allowed = True


class PaginatedData(BaseModel, Generic[T]):
    """
    Paginated data wrapper

    Attributes:
        items: List of items
        total: Total count
        page: Current page number
        page_size: Items per page
        pages: Total pages
    """

    items: list[T] = Field(default_factory=list, description="List of items")
    total: int = Field(default=0, description="Total count")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=20, description="Items per page")
    pages: int = Field(default=0, description="Total pages")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int = 1,
        page_size: int = 20,
    ) -> "PaginatedData[T]":
        """Create paginated data"""
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated API response format

    Attributes:
        code: Business status code
        message: Response message
        data: Paginated data
    """

    code: int = Field(default=0, description="Business status code")
    message: str = Field(default="success", description="Response message")
    data: PaginatedData[T] | None = Field(default=None, description="Paginated data")

    class Config:
        """Pydantic config"""

        arbitrary_types_allowed = True
