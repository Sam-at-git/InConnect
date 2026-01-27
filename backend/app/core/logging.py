"""
Logging configuration
"""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from app.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure structured logging for the application"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.addHandler(handler)

    # SQLAlchemy logging
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

    # uvicorn logging
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


class Logger:
    """Structured logger wrapper"""

    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)

    def _log(
        self,
        level: str,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """
        Log message with context

        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            context: Additional context data
        """
        log_data = {"message": message}
        if context:
            log_data.update(context)
        getattr(self.logger, level)(log_data)

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message"""
        self._log("debug", message, context)

    def info(self, message: str, **context: Any) -> None:
        """Log info message"""
        self._log("info", message, context)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message"""
        self._log("warning", message, context)

    def error(self, message: str, **context: Any) -> None:
        """Log error message"""
        self._log("error", message, context)

    def critical(self, message: str, **context: Any) -> None:
        """Log critical message"""
        self._log("critical", message, context)


def get_logger(name: str) -> Logger:
    """Get logger instance"""
    return Logger(name)
