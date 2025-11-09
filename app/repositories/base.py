"""
Base repository with generic CRUD operations.
Implements the Repository pattern for data access.
"""

from typing import Any, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository with CRUD operations.

    Example:
        user_repo = BaseRepository[User, UserCreate, UserUpdate](User)
        user = await user_repo.get(db, user_id)
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository with model class.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_field(
        self,
        db: AsyncSession,
        field: str,
        value: Any
    ) -> Optional[ModelType]:
        """
        Get a single record by field value.

        Args:
            db: Database session
            field: Field name
            value: Field value

        Returns:
            Model instance or None if not found
        """
        result = await db.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        **filters: Any
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filters.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Field filters

        Returns:
            List of model instances
        """
        query = select(self.model)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def count(self, db: AsyncSession, **filters: Any) -> int:
        """
        Count records with optional filters.

        Args:
            db: Database session
            **filters: Field filters

        Returns:
            Number of records
        """
        from sqlalchemy import func

        query = select(func.count()).select_from(self.model)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)

        result = await db.execute(query)
        return result.scalar_one()

    async def create(
        self,
        db: AsyncSession,
        obj_in: CreateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_in: Pydantic schema or dictionary with data

        Returns:
            Created model instance
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)

        db_obj = self.model(**create_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        id: UUID,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Update an existing record.

        Args:
            db: Database session
            id: Record ID
            obj_in: Pydantic schema or dictionary with update data

        Returns:
            Updated model instance or None if not found
        """
        db_obj = await self.get(db, id)
        if not db_obj:
            return None

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: UUID) -> bool:
        """
        Delete a record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        db_obj = await self.get(db, id)
        if not db_obj:
            return False

        await db.delete(db_obj)
        await db.flush()
        return True

    async def exists(self, db: AsyncSession, id: UUID) -> bool:
        """
        Check if a record exists.

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if exists, False otherwise
        """
        result = await db.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None
