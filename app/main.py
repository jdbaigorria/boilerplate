"""
FastAPI application entry point.
Configures the application with modular middleware and routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.core.logging import get_logger, setup_logging
from app.core.rate_limiter import rate_limiter
from app.db.session import close_databases, init_databases
from app.middleware.error_handler import error_handler_middleware

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize databases
    try:
        await init_databases()
        logger.info("Databases initialized")
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        if settings.is_production:
            raise

    # Initialize rate limiter
    if settings.ENABLE_RATE_LIMITING:
        try:
            await rate_limiter.connect()
            logger.info("Rate limiter initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize rate limiter: {e}")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")

    # Close databases
    await close_databases()

    # Disconnect rate limiter
    if settings.ENABLE_RATE_LIMITING:
        await rate_limiter.disconnect()

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan
)

# ==================== Middleware Configuration ====================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Trusted Host Middleware (for production)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with your actual domains
    )

# Error Handler Middleware
app.middleware("http")(error_handler_middleware)

# ==================== Router Configuration ====================

# Include API v1 router
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)

# ==================== Root Endpoint ====================


@app.get("/", tags=["root"])
async def root() -> dict:
    """
    Root endpoint with basic application information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": f"{settings.API_V1_PREFIX}/docs" if not settings.is_production else "disabled",
        "status": "running"
    }


# ==================== Feature Flags Info ====================

@app.get("/features", tags=["root"])
async def features() -> dict:
    """
    Get enabled features information.
    """
    return {
        "multi_tenancy": settings.ENABLE_MULTI_TENANCY,
        "subscriptions": settings.ENABLE_SUBSCRIPTIONS,
        "invitations": settings.ENABLE_INVITATIONS,
        "background_tasks": settings.ENABLE_BACKGROUND_TASKS,
        "rate_limiting": settings.ENABLE_RATE_LIMITING,
        "email": settings.ENABLE_EMAIL,
        "ai_service": settings.ENABLE_AI_SERVICE,
        "oauth_google": settings.ENABLE_OAUTH_GOOGLE,
        "oauth_github": settings.ENABLE_OAUTH_GITHUB,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
