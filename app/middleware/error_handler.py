"""
Global error handler middleware.
"""

import traceback
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger(__name__)


async def error_handler_middleware(
    request: Request,
    call_next: Callable
) -> Response:
    """
    Global error handler middleware.

    Catches all exceptions and returns appropriate JSON responses.

    Args:
        request: FastAPI request
        call_next: Next middleware/route handler

    Returns:
        Response
    """
    try:
        return await call_next(request)

    except AppException as exc:
        # Handle custom application exceptions
        logger.warning(
            f"Application exception: {exc.message}",
            extra={
                "status_code": exc.status_code,
                "details": exc.details,
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "details": exc.details if not settings.is_production else {},
                "status_code": exc.status_code
            }
        )

    except Exception as exc:
        # Handle unexpected exceptions
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc()
            }
        )

        # Don't expose internal error details in production
        error_detail = str(exc) if settings.DEBUG else "Internal server error"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": error_detail,
                "status_code": 500
            }
        )
