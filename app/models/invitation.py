"""
Invitation model for inviting users to organizations.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.role import Role
    from app.models.user import User


class Invitation(Base):
    """
    Invitation model for inviting users to join organizations.
    """

    __tablename__ = "invitations"

    # Invitee email
    email = Column(String(255), nullable=False, index=True)

    # Organization
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Role to be assigned
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True
    )

    # Invitation token
    token = Column(String(255), unique=True, nullable=False, index=True)

    # Invited by
    invited_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Expiration
    expires_at = Column(DateTime, nullable=False)

    # Acceptance
    accepted_at = Column(DateTime, nullable=True)
    accepted_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    organization: "Organization" = relationship("Organization")
    role: "Role" = relationship("Role")
    invited_by: "User" = relationship("User", foreign_keys=[invited_by_id])
    accepted_by: "User" = relationship("User", foreign_keys=[accepted_by_id])

    def __repr__(self) -> str:
        """String representation of Invitation."""
        status = "accepted" if self.accepted_at else "pending"
        return f"<Invitation {self.email} to org={self.organization_id} ({status})>"

    @property
    def is_expired(self) -> bool:
        """Check if invitation has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_accepted(self) -> bool:
        """Check if invitation has been accepted."""
        return self.accepted_at is not None

    @property
    def is_valid(self) -> bool:
        """Check if invitation is still valid (not expired and not accepted)."""
        return not self.is_expired and not self.is_accepted

    def accept(self, user_id: UUID) -> None:
        """
        Mark invitation as accepted.

        Args:
            user_id: ID of the user accepting the invitation
        """
        self.accepted_at = datetime.utcnow()
        self.accepted_by_id = user_id
