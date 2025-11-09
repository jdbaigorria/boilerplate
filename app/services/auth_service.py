"""
Authentication service for user registration, login, and token management.
"""

from datetime import timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotActiveException,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    validate_password_strength,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import AuthResponse
from app.schemas.user import UserCreate, UserPublic

logger = get_logger(__name__)


class AuthService:
    """Authentication service for handling user authentication."""

    @staticmethod
    async def register_user(
        db: AsyncSession,
        user_data: UserCreate
    ) -> AuthResponse:
        """
        Register a new user.

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            AuthResponse with user data and tokens

        Raises:
            UserAlreadyExistsException: If email already exists
            ValidationException: If password doesn't meet requirements
        """
        # Check if user already exists
        existing_user = await user_repository.get_by_email(db, user_data.email)
        if existing_user:
            raise UserAlreadyExistsException(user_data.email)

        # Validate password strength
        validate_password_strength(user_data.password)

        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user
        user = await user_repository.create(
            db,
            {
                "email": user_data.email,
                "full_name": user_data.full_name,
                "hashed_password": hashed_password,
                "is_active": True,
                "is_superuser": False,
                "email_verified": False if settings.ENABLE_EMAIL else True,
            }
        )

        await db.commit()

        logger.info(f"User registered: {user.email}")

        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return AuthResponse(
            user=UserPublic.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token
        )

    @staticmethod
    async def login(
        db: AsyncSession,
        email: str,
        password: str
    ) -> AuthResponse:
        """
        Authenticate user with email and password.

        Args:
            db: Database session
            email: User email
            password: User password

        Returns:
            AuthResponse with user data and tokens

        Raises:
            InvalidCredentialsException: If credentials are invalid
            UserNotActiveException: If user account is inactive
        """
        # Get user by email
        user = await user_repository.get_by_email(db, email)

        # Validate credentials
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        # Check if user is active
        if not user.is_active:
            raise UserNotActiveException()

        # Update last login
        await user_repository.update_last_login(db, user.id)
        await db.commit()

        logger.info(f"User logged in: {user.email}")

        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return AuthResponse(
            user=UserPublic.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token
        )

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str
    ) -> str:
        """
        Refresh access token using refresh token.

        Args:
            db: Database session
            refresh_token: Refresh token

        Returns:
            New access token

        Raises:
            InvalidTokenException: If token is invalid
            TokenExpiredException: If token has expired
        """
        # Decode and validate refresh token
        payload = decode_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")

        # Verify user still exists and is active
        user = await user_repository.get(db, user_id)
        if not user or not user.is_active:
            raise InvalidCredentialsException()

        # Generate new access token
        access_token = create_access_token({"sub": str(user.id)})

        return access_token

    @staticmethod
    async def get_current_user(
        db: AsyncSession,
        token: str
    ) -> Optional[User]:
        """
        Get current user from access token.

        Args:
            db: Database session
            token: Access token

        Returns:
            User instance or None

        Raises:
            InvalidTokenException: If token is invalid
            TokenExpiredException: If token has expired
        """
        # Decode token
        payload = decode_token(token, token_type="access")
        user_id = payload.get("sub")

        # Get user
        user = await user_repository.get(db, user_id)
        return user


# Global instance
auth_service = AuthService()
