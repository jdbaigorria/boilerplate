"""
Health check API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.monitoring import HealthCheck
from app.db.session import get_db

router = APIRouter()


@router.get(
    "/health",
    summary="Basic health check",
    description="Simple health check to verify service is running"
)
async def health_check() -> dict:
    """
    Basic health check endpoint.

    Returns a simple OK response to verify the service is running.
    """
    return HealthCheck.check_liveness()


@router.get(
    "/health/ready",
    summary="Readiness check",
    description="Comprehensive readiness check including database connectivity"
)
async def readiness_check(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Readiness check endpoint.

    Checks if the application is ready to serve traffic by verifying:
    - Database connectivity
    - Redis connectivity (if enabled)
    - MongoDB connectivity (if enabled)
    """
    return await HealthCheck.check_readiness(db)


@router.get(
    "/health/live",
    summary="Liveness check",
    description="Liveness check to verify application is alive"
)
async def liveness_check() -> dict:
    """
    Liveness check endpoint.

    Returns application status and version information.
    """
    return HealthCheck.check_liveness()
