"""
Authentication schemas for login, registration, and tokens.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserPublic


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # User ID
    exp: int  # Expiration time
    type: str  # Token type (access/refresh)


class LoginRequest(BaseModel):
    """Login request with email and password."""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class AuthResponse(BaseModel):
    """Complete authentication response."""

    user: UserPublic
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request."""

    token: str
    new_password: str = Field(..., min_length=8)


class VerifyEmailRequest(BaseModel):
    """Email verification request."""

    token: str


class OAuthLoginRequest(BaseModel):
    """OAuth login request."""

    token: str  # Google/GitHub token
    provider: str = Field(..., pattern="^(google|github)$")
