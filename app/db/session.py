"""
Database session management.
Provides unified interface for database operations.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def init_databases() -> None:
    """
    Initialize all enabled databases.
    Called on application startup.
    """
    # Initialize PostgreSQL if enabled
    if settings.USE_POSTGRES:
        from app.db.postgres.connection import init_db
        init_db()
        logger.info("PostgreSQL initialized")

    # Initialize MongoDB if enabled
    if settings.USE_MONGODB:
        from app.db.mongodb.connection import init_mongodb
        await init_mongodb()
        logger.info("MongoDB initialized")


async def close_databases() -> None:
    """
    Close all database connections.
    Called on application shutdown.
    """
    # Close PostgreSQL if enabled
    if settings.USE_POSTGRES:
        from app.db.postgres.connection import close_db
        await close_db()

    # Close MongoDB if enabled
    if settings.USE_MONGODB:
        from app.db.mongodb.connection import close_mongodb
        await close_mongodb()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session (PostgreSQL).
    Use this as a dependency in FastAPI routes.

    Yields:
        AsyncSession instance

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # Use db here
            pass
    """
    from app.db.postgres.connection import get_db as get_postgres_db
    async for session in get_postgres_db():
        yield session


def get_mongo_db():
    """
    Get MongoDB database instance.

    Returns:
        AsyncIOMotorDatabase instance
    """
    from app.db.mongodb.connection import get_mongo_db as get_mongo
    return get_mongo()
