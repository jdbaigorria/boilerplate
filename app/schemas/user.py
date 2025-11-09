"""
User schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import IDSchema, TimestampSchema


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserUpdatePassword(BaseModel):
    """Schema for updating user password."""

    current_password: str
    new_password: str = Field(..., min_length=8)


class UserInDB(UserBase, IDSchema, TimestampSchema):
    """User schema as stored in database."""

    hashed_password: str
    is_active: bool
    is_superuser: bool
    email_verified: bool
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    google_id: Optional[str] = None
    github_id: Optional[str] = None

    class Config:
        from_attributes = True


class UserPublic(UserBase, IDSchema, TimestampSchema):
    """Public user schema (no sensitive data)."""

    is_active: bool
    is_superuser: bool
    email_verified: bool
    last_login_at: Optional[datetime] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfile(UserPublic):
    """Extended user profile."""

    pass
