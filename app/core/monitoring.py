"""
Health checks and monitoring functionality.
Provides readiness and liveness probes for the application.
"""

from datetime import datetime
from typing import Any, Dict

import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class HealthCheck:
    """Health check manager for the application."""

    @staticmethod
    async def check_database(db: AsyncSession) -> Dict[str, Any]:
        """
        Check database connectivity.

        Args:
            db: Database session

        Returns:
            Dictionary with check status
        """
        try:
            # Simple query to check database connectivity
            await db.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "message": "Database is reachable",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database is unreachable: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    async def check_redis() -> Dict[str, Any]:
        """
        Check Redis connectivity.

        Returns:
            Dictionary with check status
        """
        if not settings.ENABLE_RATE_LIMITING and not settings.ENABLE_BACKGROUND_TASKS:
            return {
                "status": "disabled",
                "message": "Redis is not enabled",
                "timestamp": datetime.utcnow().isoformat()
            }

        redis_client = None
        try:
            redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await redis_client.ping()
            return {
                "status": "healthy",
                "message": "Redis is reachable",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Redis is unreachable: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            if redis_client:
                await redis_client.close()

    @staticmethod
    async def check_mongodb() -> Dict[str, Any]:
        """
        Check MongoDB connectivity.

        Returns:
            Dictionary with check status
        """
        if not settings.USE_MONGODB:
            return {
                "status": "disabled",
                "message": "MongoDB is not enabled",
                "timestamp": datetime.utcnow().isoformat()
            }

        try:
            from motor.motor_asyncio import AsyncIOMotorClient

            client = AsyncIOMotorClient(settings.MONGODB_URL)
            # Ping MongoDB
            await client.admin.command("ping")
            client.close()

            return {
                "status": "healthy",
                "message": "MongoDB is reachable",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"MongoDB is unreachable: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    def check_liveness() -> Dict[str, Any]:
        """
        Liveness probe - check if application is running.

        Returns:
            Dictionary with check status
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }

    @staticmethod
    async def check_readiness(db: AsyncSession) -> Dict[str, Any]:
        """
        Readiness probe - check if application is ready to serve traffic.

        Args:
            db: Database session

        Returns:
            Dictionary with check status and details
        """
        checks = {
            "database": {"status": "unknown"},
            "redis": {"status": "unknown"},
            "mongodb": {"status": "unknown"}
        }

        overall_status = "ready"

        # Check database if enabled
        if settings.USE_POSTGRES:
            db_check = await HealthCheck.check_database(db)
            checks["database"] = db_check
            if db_check["status"] == "unhealthy":
                overall_status = "not_ready"

        # Check Redis if enabled
        if settings.ENABLE_RATE_LIMITING or settings.ENABLE_BACKGROUND_TASKS:
            redis_check = await HealthCheck.check_redis()
            checks["redis"] = redis_check
            if redis_check["status"] == "unhealthy":
                overall_status = "not_ready"

        # Check MongoDB if enabled
        if settings.USE_MONGODB:
            mongo_check = await HealthCheck.check_mongodb()
            checks["mongodb"] = mongo_check
            if mongo_check["status"] == "unhealthy":
                overall_status = "not_ready"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }


class Metrics:
    """
    Application metrics collection.
    Can be extended to integrate with Prometheus or other monitoring systems.
    """

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.request_count: int = 0
        self.error_count: int = 0
        self.active_requests: int = 0

    def increment_request_count(self) -> None:
        """Increment total request count."""
        self.request_count += 1

    def increment_error_count(self) -> None:
        """Increment error count."""
        self.error_count += 1

    def increment_active_requests(self) -> None:
        """Increment active requests counter."""
        self.active_requests += 1

    def decrement_active_requests(self) -> None:
        """Decrement active requests counter."""
        self.active_requests = max(0, self.active_requests - 1)

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.

        Returns:
            Dictionary with current metrics
        """
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "active_requests": self.active_requests,
            "timestamp": datetime.utcnow().isoformat()
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.request_count = 0
        self.error_count = 0
        self.active_requests = 0


# Global metrics instance
metrics = Metrics()


# Prometheus integration (if enabled)
if settings.ENABLE_PROMETHEUS:
    try:
        from prometheus_client import Counter, Gauge, Histogram

        # Define Prometheus metrics
        request_counter = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"]
        )

        request_duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration",
            ["method", "endpoint"]
        )

        active_requests_gauge = Gauge(
            "http_requests_active",
            "Active HTTP requests"
        )

        error_counter = Counter(
            "http_errors_total",
            "Total HTTP errors",
            ["method", "endpoint", "status"]
        )

        logger.info("Prometheus metrics enabled")
    except ImportError:
        logger.warning("prometheus_client not installed, metrics disabled")
        settings.ENABLE_PROMETHEUS = False
