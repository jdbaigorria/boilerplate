"""
PostgreSQL database connection and session management.
Uses SQLAlchemy async engine with connection pooling.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create async engine
engine = None
async_session_maker = None


def init_db() -> None:
    """Initialize database engine and session maker."""
    global engine, async_session_maker

    if not settings.USE_POSTGRES or not settings.database_url:
        logger.warning("PostgreSQL is not configured or disabled")
        return

    try:
        # Create async engine with connection pooling
        engine = create_async_engine(
            settings.database_url,
            echo=settings.DEBUG,
            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,
            pool_pre_ping=True,  # Enable connection health checks
            pool_recycle=3600,   # Recycle connections after 1 hour
        )

        # Create session maker
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        logger.info("PostgreSQL database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL database: {e}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Yields:
        AsyncSession instance

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    """
    if not async_session_maker:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """Close database connection."""
    global engine

    if engine:
        await engine.dispose()
        logger.info("PostgreSQL database connection closed")


# For testing - create engine with NullPool
def create_test_engine(database_url: str) -> None:
    """
    Create a test database engine.

    Args:
        database_url: Database URL for testing
    """
    global engine, async_session_maker

    engine = create_async_engine(
        database_url,
        echo=False,
        poolclass=NullPool,  # No connection pooling for tests
    )

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
