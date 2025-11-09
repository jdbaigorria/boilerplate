"""
User model for authentication and user management.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import OrganizationMember
    from app.models.role import UserRole


class User(Base):
    """User model with authentication and profile information."""

    __tablename__ = "users"

    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile fields
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)

    # Timestamps
    last_login_at = Column(DateTime, nullable=True)
    email_verified_at = Column(DateTime, nullable=True)

    # OAuth fields (optional)
    google_id = Column(String(255), nullable=True, unique=True, index=True)
    github_id = Column(String(255), nullable=True, unique=True, index=True)

    # Relationships
    roles: "list[UserRole]" = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    organization_memberships: "list[OrganizationMember]" = relationship(
        "OrganizationMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User {self.email}>"

    @property
    def is_verified(self) -> bool:
        """Check if user's email is verified."""
        return self.email_verified

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login_at = datetime.utcnow()
