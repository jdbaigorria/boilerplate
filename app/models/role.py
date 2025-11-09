"""
Role and permission model for authorization.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class Role(Base):
    """
    Role model for role-based access control (RBAC).
    Can be global (organization_id=None) or organization-specific.
    """

    __tablename__ = "roles"

    # Basic information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Permissions stored as JSON array
    # Example: ["users:read", "users:write", "organizations:admin"]
    permissions = Column(JSON, default=[], nullable=False)

    # Organization (null for global roles)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Relationships
    organization: "Organization" = relationship("Organization", foreign_keys=[organization_id])

    user_roles: "list[UserRole]" = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Role."""
        scope = f"org={self.organization_id}" if self.organization_id else "global"
        return f"<Role {self.name} ({scope})>"

    def has_permission(self, permission: str) -> bool:
        """
        Check if role has a specific permission.

        Args:
            permission: Permission string (e.g., "users:write")

        Returns:
            True if role has the permission
        """
        if not self.permissions:
            return False

        # Check for exact match
        if permission in self.permissions:
            return True

        # Check for wildcard permissions (e.g., "users:*" grants "users:read")
        resource = permission.split(":")[0] if ":" in permission else permission
        wildcard = f"{resource}:*"
        if wildcard in self.permissions:
            return True

        # Check for admin permission (grants all)
        if "*:*" in self.permissions or "admin" in self.permissions:
            return True

        return False


class UserRole(Base):
    """
    Association table for User-Role many-to-many relationship.
    """

    __tablename__ = "user_roles"

    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Optional: organization context for the role
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Relationships
    user: "User" = relationship("User", back_populates="roles")
    role: "Role" = relationship("Role", back_populates="user_roles")
    organization: "Organization" = relationship("Organization")

    def __repr__(self) -> str:
        """String representation of UserRole."""
        return f"<UserRole user={self.user_id} role={self.role_id}>"


# Predefined permission constants
class Permissions:
    """Predefined permission constants."""

    # User permissions
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_DELETE = "users:delete"

    # Organization permissions
    ORGANIZATIONS_READ = "organizations:read"
    ORGANIZATIONS_WRITE = "organizations:write"
    ORGANIZATIONS_DELETE = "organizations:delete"
    ORGANIZATIONS_ADMIN = "organizations:admin"

    # Subscription permissions
    SUBSCRIPTIONS_READ = "subscriptions:read"
    SUBSCRIPTIONS_WRITE = "subscriptions:write"
    SUBSCRIPTIONS_MANAGE = "subscriptions:manage"

    # Invitation permissions
    INVITATIONS_SEND = "invitations:send"
    INVITATIONS_MANAGE = "invitations:manage"

    # Admin permissions
    ADMIN_ALL = "*:*"


# Predefined role names
class RoleNames:
    """Predefined role name constants."""

    SUPERUSER = "superuser"
    ORG_OWNER = "owner"
    ORG_ADMIN = "admin"
    ORG_MEMBER = "member"
    ORG_VIEWER = "viewer"
