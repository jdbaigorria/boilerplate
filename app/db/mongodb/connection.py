"""
MongoDB database connection management.
Uses Motor async driver for MongoDB.
"""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# MongoDB client and database
mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db: Optional[AsyncIOMotorDatabase] = None


async def init_mongodb() -> None:
    """Initialize MongoDB connection."""
    global mongo_client, mongo_db

    if not settings.USE_MONGODB or not settings.MONGODB_URL:
        logger.warning("MongoDB is not configured or disabled")
        return

    try:
        # Create MongoDB client
        mongo_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
        )

        # Get database
        mongo_db = mongo_client[settings.MONGODB_DB]

        # Ping to verify connection
        await mongo_client.admin.command("ping")

        logger.info("MongoDB connected successfully")

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongodb() -> None:
    """Close MongoDB connection."""
    global mongo_client

    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")


def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Get MongoDB database instance.

    Returns:
        AsyncIOMotorDatabase instance

    Raises:
        RuntimeError: If MongoDB is not initialized
    """
    if mongo_db is None:
        raise RuntimeError("MongoDB not initialized. Call init_mongodb() first.")
    return mongo_db


def get_collection(name: str):
    """
    Get a MongoDB collection.

    Args:
        name: Collection name

    Returns:
        AsyncIOMotorCollection instance
    """
    db = get_mongo_db()
    return db[name]


# Helper functions for common MongoDB operations

async def create_indexes() -> None:
    """Create indexes for MongoDB collections."""
    if not mongo_db:
        return

    try:
        # Example indexes - customize based on your needs
        # Users collection
        users = mongo_db["users"]
        await users.create_index("email", unique=True)
        await users.create_index("created_at")

        logger.info("MongoDB indexes created successfully")

    except Exception as e:
        logger.error(f"Failed to create MongoDB indexes: {e}")
