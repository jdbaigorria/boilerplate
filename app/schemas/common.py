"""
Common Pydantic schemas used across the application.
"""

from datetime import datetime
from typing import Generic, List, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

# TypeVar for generic pagination
T = TypeVar("T")


class TimestampSchema(BaseModel):
    """Base schema with timestamps."""

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IDSchema(BaseModel):
    """Base schema with ID."""

    id: UUID

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of records to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        skip: int,
        limit: int
    ) -> "PaginatedResponse[T]":
        """Create paginated response."""
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total
        )


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    details: dict = Field(default_factory=dict)
    status_code: int
