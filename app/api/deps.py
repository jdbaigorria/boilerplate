"""
API dependencies for FastAPI routes.
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import auth_service

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False
)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        token: JWT access token
        db: Database session

    Returns:
        Current user

    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    if not token:
        raise UnauthorizedException(message="Not authenticated")

    try:
        user = await auth_service.get_current_user(db, token)
        if not user:
            raise UnauthorizedException(message="User not found")
        return user
    except Exception as e:
        raise UnauthorizedException(message=str(e))


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current user if active

    Raises:
        ForbiddenException: If user is not active
    """
    if not current_user.is_active:
        raise ForbiddenException(message="Inactive user")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current superuser.

    Args:
        current_user: Current user from get_current_active_user

    Returns:
        Current user if superuser

    Raises:
        ForbiddenException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise ForbiddenException(message="Not enough permissions")
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current verified user (email verified).

    Args:
        current_user: Current user from get_current_active_user

    Returns:
        Current user if email is verified

    Raises:
        ForbiddenException: If email is not verified
    """
    if settings.ENABLE_EMAIL and not current_user.email_verified:
        raise ForbiddenException(message="Email not verified")
    return current_user


# Optional: Get current user without raising exception
async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise None.

    Args:
        token: JWT access token (optional)
        db: Database session

    Returns:
        Current user or None
    """
    if not token:
        return None

    try:
        return await auth_service.get_current_user(db, token)
    except Exception:
        return None


# Multi-tenancy dependencies (if enabled)
if settings.ENABLE_MULTI_TENANCY:
    async def get_current_organization_id(
        x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID")
    ) -> Optional[UUID]:
        """
        Get current organization ID from header.

        Args:
            x_organization_id: Organization ID from header

        Returns:
            Organization UUID or None
        """
        if not x_organization_id:
            return None

        try:
            return UUID(x_organization_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization ID format"
            )


# Rate limiting dependencies
if settings.ENABLE_RATE_LIMITING:
    from app.core.rate_limiter import check_ip_rate_limit

    async def rate_limit_dependency(
        request: "Request"  # type: ignore
    ) -> None:
        """
        Apply rate limiting to endpoints.

        Args:
            request: FastAPI request

        Raises:
            RateLimitException: If rate limit exceeded
        """
        client_ip = request.client.host if request.client else "unknown"
        await check_ip_rate_limit(client_ip)
