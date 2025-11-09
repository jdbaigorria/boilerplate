"""
Organization model for multi-tenancy support.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.subscription import Subscription
    from app.models.user import User


class Organization(Base):
    """Organization model for multi-tenant SaaS."""

    __tablename__ = "organizations"

    # Basic information
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)

    # Owner
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Settings (JSON field for flexible configuration)
    settings = Column(JSON, default={}, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    owner: "User" = relationship("User", foreign_keys=[owner_id])

    members: "list[OrganizationMember]" = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan"
    )

    subscription: "Subscription" = relationship(
        "Subscription",
        back_populates="organization",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Organization."""
        return f"<Organization {self.name} ({self.slug})>"

    @property
    def member_count(self) -> int:
        """Get number of members in the organization."""
        return len(self.members) if self.members else 0


class OrganizationMember(Base):
    """
    Association table for Organization-User many-to-many relationship.
    Includes role information for each member.
    """

    __tablename__ = "organization_members"

    # Foreign keys
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    organization: "Organization" = relationship(
        "Organization",
        back_populates="members"
    )

    user: "User" = relationship(
        "User",
        back_populates="organization_memberships"
    )

    role: "Role" = relationship("Role")

    def __repr__(self) -> str:
        """String representation of OrganizationMember."""
        return f"<OrganizationMember org={self.organization_id} user={self.user_id}>"


# Import Role model to resolve forward references
from app.models.role import Role  # noqa: E402, F401
