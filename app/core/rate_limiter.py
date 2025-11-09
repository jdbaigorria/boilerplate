"""
Rate limiting implementation using Redis.
Supports per-IP and per-user rate limiting with sliding window algorithm.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple

import redis.asyncio as redis

from app.config import settings
from app.core.exceptions import RateLimitException
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Rate limiter using Redis and sliding window algorithm.
    """

    def __init__(self) -> None:
        """Initialize rate limiter with Redis connection."""
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.ENABLE_RATE_LIMITING

    async def connect(self) -> None:
        """Connect to Redis."""
        if not self.enabled:
            return

        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Rate limiter connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis for rate limiting: {e}")
            self.enabled = False

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Rate limiter disconnected from Redis")

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, int]:
        """
        Check if rate limit is exceeded using sliding window algorithm.

        Args:
            key: Unique identifier for the rate limit (e.g., user_id, ip_address)
            limit: Maximum number of requests allowed
            window: Time window in seconds

        Returns:
            Tuple of (is_allowed, remaining, reset_time)
        """
        if not self.enabled or not self.redis_client:
            return True, limit, 0

        try:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window)

            # Redis key for this rate limit
            redis_key = f"rate_limit:{key}"

            # Remove old entries outside the window
            await self.redis_client.zremrangebyscore(
                redis_key,
                0,
                window_start.timestamp()
            )

            # Count requests in the current window
            request_count = await self.redis_client.zcard(redis_key)

            if request_count >= limit:
                # Rate limit exceeded
                # Get the oldest request timestamp to calculate reset time
                oldest = await self.redis_client.zrange(redis_key, 0, 0, withscores=True)
                if oldest:
                    oldest_timestamp = oldest[0][1]
                    reset_time = int(oldest_timestamp + window)
                else:
                    reset_time = int((now + timedelta(seconds=window)).timestamp())

                return False, 0, reset_time

            # Add current request
            await self.redis_client.zadd(
                redis_key,
                {str(now.timestamp()): now.timestamp()}
            )

            # Set expiration on the key
            await self.redis_client.expire(redis_key, window)

            remaining = limit - request_count - 1
            reset_time = int((now + timedelta(seconds=window)).timestamp())

            return True, remaining, reset_time

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Fail open - allow request if Redis is down
            return True, limit, 0

    async def check_rate_limit_or_raise(
        self,
        key: str,
        limit: int,
        window: int
    ) -> Tuple[int, int]:
        """
        Check rate limit and raise exception if exceeded.

        Args:
            key: Unique identifier for the rate limit
            limit: Maximum number of requests allowed
            window: Time window in seconds

        Returns:
            Tuple of (remaining, reset_time)

        Raises:
            RateLimitException: If rate limit is exceeded
        """
        is_allowed, remaining, reset_time = await self.check_rate_limit(key, limit, window)

        if not is_allowed:
            retry_after = reset_time - int(datetime.utcnow().timestamp())
            raise RateLimitException(
                message="Rate limit exceeded. Please try again later.",
                retry_after=retry_after,
                details={
                    "limit": limit,
                    "window": window,
                    "reset_at": reset_time
                }
            )

        return remaining, reset_time

    async def reset_rate_limit(self, key: str) -> None:
        """
        Reset rate limit for a specific key.

        Args:
            key: Unique identifier for the rate limit
        """
        if not self.enabled or not self.redis_client:
            return

        try:
            redis_key = f"rate_limit:{key}"
            await self.redis_client.delete(redis_key)
            logger.info(f"Rate limit reset for key: {key}")
        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")

    async def get_rate_limit_info(
        self,
        key: str,
        limit: int,
        window: int
    ) -> dict:
        """
        Get current rate limit information.

        Args:
            key: Unique identifier for the rate limit
            limit: Maximum number of requests allowed
            window: Time window in seconds

        Returns:
            Dictionary with rate limit information
        """
        if not self.enabled or not self.redis_client:
            return {
                "limit": limit,
                "remaining": limit,
                "reset": 0,
                "used": 0
            }

        try:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window)
            redis_key = f"rate_limit:{key}"

            # Remove old entries
            await self.redis_client.zremrangebyscore(
                redis_key,
                0,
                window_start.timestamp()
            )

            # Count current requests
            used = await self.redis_client.zcard(redis_key)
            remaining = max(0, limit - used)

            # Calculate reset time
            oldest = await self.redis_client.zrange(redis_key, 0, 0, withscores=True)
            if oldest:
                reset = int(oldest[0][1] + window)
            else:
                reset = int((now + timedelta(seconds=window)).timestamp())

            return {
                "limit": limit,
                "remaining": remaining,
                "reset": reset,
                "used": used
            }

        except Exception as e:
            logger.error(f"Failed to get rate limit info: {e}")
            return {
                "limit": limit,
                "remaining": limit,
                "reset": 0,
                "used": 0
            }


# Global rate limiter instance
rate_limiter = RateLimiter()


# Helper functions for common rate limiting patterns

async def check_ip_rate_limit(ip_address: str) -> Tuple[int, int]:
    """
    Check rate limit for an IP address.

    Args:
        ip_address: Client IP address

    Returns:
        Tuple of (remaining, reset_time)
    """
    return await rate_limiter.check_rate_limit_or_raise(
        key=f"ip:{ip_address}",
        limit=settings.RATE_LIMIT_PER_MINUTE,
        window=60
    )


async def check_user_rate_limit(user_id: str, limit: int, window: int) -> Tuple[int, int]:
    """
    Check rate limit for a user.

    Args:
        user_id: User ID
        limit: Maximum number of requests
        window: Time window in seconds

    Returns:
        Tuple of (remaining, reset_time)
    """
    return await rate_limiter.check_rate_limit_or_raise(
        key=f"user:{user_id}",
        limit=limit,
        window=window
    )


async def check_endpoint_rate_limit(
    identifier: str,
    endpoint: str,
    limit: int,
    window: int
) -> Tuple[int, int]:
    """
    Check rate limit for a specific endpoint.

    Args:
        identifier: User ID or IP address
        endpoint: Endpoint path
        limit: Maximum number of requests
        window: Time window in seconds

    Returns:
        Tuple of (remaining, reset_time)
    """
    return await rate_limiter.check_rate_limit_or_raise(
        key=f"endpoint:{identifier}:{endpoint}",
        limit=limit,
        window=window
    )
