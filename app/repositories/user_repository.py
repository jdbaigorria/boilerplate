"""
User repository with user-specific data access methods.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository with custom methods."""

    def __init__(self) -> None:
        """Initialize user repository."""
        super().__init__(User)

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """
        Get user by email address.

        Args:
            db: Database session
            email: Email address

        Returns:
            User instance or None
        """
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_google_id(
        self,
        db: AsyncSession,
        google_id: str
    ) -> Optional[User]:
        """
        Get user by Google ID.

        Args:
            db: Database session
            google_id: Google ID

        Returns:
            User instance or None
        """
        result = await db.execute(
            select(User).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none()

    async def get_by_github_id(
        self,
        db: AsyncSession,
        github_id: str
    ) -> Optional[User]:
        """
        Get user by GitHub ID.

        Args:
            db: Database session
            github_id: GitHub ID

        Returns:
            User instance or None
        """
        result = await db.execute(
            select(User).where(User.github_id == github_id)
        )
        return result.scalar_one_or_none()

    async def update_last_login(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[User]:
        """
        Update user's last login timestamp.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Updated user instance or None
        """
        user = await self.get(db, user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            await db.flush()
            await db.refresh(user)
        return user

    async def verify_email(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[User]:
        """
        Mark user's email as verified.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Updated user instance or None
        """
        user = await self.get(db, user_id)
        if user:
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()
            await db.flush()
            await db.refresh(user)
        return user

    async def deactivate(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[User]:
        """
        Deactivate user account.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Updated user instance or None
        """
        user = await self.get(db, user_id)
        if user:
            user.is_active = False
            await db.flush()
            await db.refresh(user)
        return user

    async def activate(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[User]:
        """
        Activate user account.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Updated user instance or None
        """
        user = await self.get(db, user_id)
        if user:
            user.is_active = True
            await db.flush()
            await db.refresh(user)
        return user

    async def update_password(
        self,
        db: AsyncSession,
        user_id: UUID,
        hashed_password: str
    ) -> Optional[User]:
        """
        Update user's password.

        Args:
            db: Database session
            user_id: User ID
            hashed_password: New hashed password

        Returns:
            Updated user instance or None
        """
        user = await self.get(db, user_id)
        if user:
            user.hashed_password = hashed_password
            await db.flush()
            await db.refresh(user)
        return user

    async def email_exists(
        self,
        db: AsyncSession,
        email: str
    ) -> bool:
        """
        Check if email already exists.

        Args:
            db: Database session
            email: Email address

        Returns:
            True if email exists
        """
        result = await db.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None


# Global instance
user_repository = UserRepository()
