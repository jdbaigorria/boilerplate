"""
Logging configuration for the application.
Supports both JSON and pretty formatting based on environment.
"""

import logging
import sys
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

from app.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["app"] = settings.APP_NAME
        log_record["environment"] = settings.ENVIRONMENT

        # Add exception info if present
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)


class PrettyFormatter(logging.Formatter):
    """Pretty formatter for development with colors."""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # Format the message
        record.levelname = f"{color}{record.levelname:8s}{reset}"
        record.name = f"{color}{record.name}{reset}"

        return super().format(record)


def setup_logging() -> None:
    """
    Setup application logging based on configuration.
    Uses JSON logging for production and pretty logging for development.
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Set formatter based on environment
    if settings.LOG_FORMAT == "json" or settings.is_production:
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "name": "logger"},
            datefmt="%Y-%m-%dT%H:%M:%S"
        )
    else:
        formatter = PrettyFormatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if configured
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(logging.INFO)

        # Always use JSON format for file logs
        json_formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S"
        )
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aioredis").setLevel(logging.WARNING)

    logger.info(
        "Logging configured",
        extra={
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT,
            "environment": settings.ENVIRONMENT
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Name of the logger (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Context manager for adding context to logs
class LogContext:
    """Context manager for adding contextual information to logs."""

    def __init__(self, logger: logging.Logger, **kwargs: Any) -> None:
        self.logger = logger
        self.context = kwargs
        self.old_factory = logging.getLogRecordFactory()

    def __enter__(self) -> "LogContext":
        """Add context to log records."""
        def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, *args: Any) -> None:
        """Restore original log record factory."""
        logging.setLogRecordFactory(self.old_factory)


# Example usage:
# logger = get_logger(__name__)
# with LogContext(logger, user_id="123", request_id="abc"):
#     logger.info("User action performed")
