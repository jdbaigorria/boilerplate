"""
API v1 router that combines all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1 import auth, health

api_router = APIRouter()

# Include routers
api_router.include_router(
    health.router,
    tags=["health"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# Add more routers as needed:
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
# api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
