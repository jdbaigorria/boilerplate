"""
Base class for all SQLAlchemy models.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Base class for all database models.
    Provides common columns and functionality.
    """

    id: Any
    __name__: str

    # Generate __tablename__ automatically from class name
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()

    # Common columns for all models
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def dict(self) -> dict:
        """
        Convert model to dictionary.

        Returns:
            Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
