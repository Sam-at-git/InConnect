"""
Dependency injection for FastAPI
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends

from app.core.database import AsyncSession, get_db


# Database session dependency
async def get_db_session() -> AsyncSession:
    """
    Get database session for dependency injection

    Yields:
        AsyncSession: Database session
    """
    async for session in get_db():
        yield session


# Type alias for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db_session)]
