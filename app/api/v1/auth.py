"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserCreate, UserPublic
from app.services.auth_service import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account and return authentication tokens"
)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Register a new user.

    - **email**: Valid email address
    - **password**: Password (min 8 characters)
    - **full_name**: Optional full name
    """
    user_create = UserCreate(**user_data.model_dump())
    return await auth_service.register_user(db, user_create)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login",
    description="Authenticate with email and password"
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Login with email and password.

    - **email**: User email
    - **password**: User password
    """
    return await auth_service.login(db, login_data.email, login_data.password)


@router.post(
    "/refresh",
    response_model=dict,
    summary="Refresh access token",
    description="Get a new access token using refresh token"
)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Refresh access token.

    - **refresh_token**: Valid refresh token
    """
    access_token = await auth_service.refresh_access_token(
        db,
        token_data.refresh_token
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get current user",
    description="Get authenticated user information"
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserPublic:
    """
    Get current authenticated user.
    """
    return UserPublic.model_validate(current_user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
    description="Logout current user (client-side token removal)"
)
async def logout(
    current_user: User = Depends(get_current_user)
) -> MessageResponse:
    """
    Logout user.

    Note: Since we're using stateless JWT, actual logout happens on client side
    by removing the tokens. This endpoint is provided for consistency.
    """
    return MessageResponse(
        message="Successfully logged out",
        success=True
    )
