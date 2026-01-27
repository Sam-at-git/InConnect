"""
Performance monitoring middleware
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger("app.performance")


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track request performance"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and track performance"""
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log slow requests (> 1 second)
        if duration_ms > 1000:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} took {duration_ms:.2f}ms",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )

        # Add performance header
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}"

        return response


class QueryCounterMiddleware(BaseHTTPMiddleware):
    """Middleware to count database queries (for development)"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and count queries"""
        from app.config import get_settings

        settings = get_settings()

        # Only enable in development
        if settings.app_env != "development":
            return await call_next(request)

        # Import here to avoid issues
        from sqlalchemy import event
        from app.core.database import async_engine

        query_count = [0]

        def before_cursor_execute(*args, **kwargs):
            query_count[0] += 1

        # Setup listener
        event.listen(async_engine.sync_engine, "before_cursor_execute", before_cursor_execute)

        # Process request
        response = await call_next(request)

        # Remove listener
        event.remove(async_engine.sync_engine, "before_cursor_execute", before_cursor_execute)

        # Add query count header
        response.headers["X-DB-Queries"] = str(query_count[0])

        return response
