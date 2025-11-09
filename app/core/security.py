"""
Security utilities for authentication and authorization.
Includes password hashing, JWT token generation/validation, and secure token generation.
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.core.exceptions import InvalidTokenException, TokenExpiredException
from app.core.logging import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        data: Dictionary of data to encode in the token

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode
        token_type: Expected token type ('access' or 'refresh')

    Returns:
        Decoded token payload

    Raises:
        InvalidTokenException: If token is invalid
        TokenExpiredException: If token has expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Verify token type
        if payload.get("type") != token_type:
            raise InvalidTokenException(token_type=token_type)

        return payload

    except jwt.ExpiredSignatureError:
        raise TokenExpiredException(token_type=token_type)
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise InvalidTokenException(token_type=token_type)


def create_password_reset_token(user_id: str) -> str:
    """
    Create a password reset token.

    Args:
        user_id: User ID

    Returns:
        Encoded JWT token
    """
    data = {"sub": user_id, "type": "password_reset"}
    expire = datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)

    to_encode = data.copy()
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return user ID.

    Args:
        token: Password reset token

    Returns:
        User ID if token is valid, None otherwise

    Raises:
        TokenExpiredException: If token has expired
        InvalidTokenException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "password_reset":
            raise InvalidTokenException(token_type="password_reset")

        user_id: str = payload.get("sub")
        return user_id

    except jwt.ExpiredSignatureError:
        raise TokenExpiredException(token_type="password_reset")
    except JWTError:
        raise InvalidTokenException(token_type="password_reset")


def create_email_verification_token(user_id: str, email: str) -> str:
    """
    Create an email verification token.

    Args:
        user_id: User ID
        email: Email address to verify

    Returns:
        Encoded JWT token
    """
    data = {
        "sub": user_id,
        "email": email,
        "type": "email_verification"
    }
    expire = datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)

    to_encode = data.copy()
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verify_email_verification_token(token: str) -> Optional[Dict[str, str]]:
    """
    Verify an email verification token.

    Args:
        token: Email verification token

    Returns:
        Dictionary with user_id and email if valid

    Raises:
        TokenExpiredException: If token has expired
        InvalidTokenException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "email_verification":
            raise InvalidTokenException(token_type="email_verification")

        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email")
        }

    except jwt.ExpiredSignatureError:
        raise TokenExpiredException(token_type="email_verification")
    except JWTError:
        raise InvalidTokenException(token_type="email_verification")


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    Useful for invitation tokens, API keys, etc.

    Args:
        length: Length of the token (default: 32 bytes)

    Returns:
        URL-safe random token
    """
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """
    Generate a secure API key.

    Returns:
        API key string
    """
    return f"sk_{generate_secure_token(32)}"


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.

    Args:
        api_key: API key to hash

    Returns:
        Hashed API key
    """
    return get_password_hash(api_key)


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """
    Verify an API key against its hash.

    Args:
        plain_api_key: Plain text API key
        hashed_api_key: Hashed API key

    Returns:
        True if API key matches, False otherwise
    """
    return verify_password(plain_api_key, hashed_api_key)


class PasswordValidator:
    """
    Password strength validator.
    """

    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True

    @classmethod
    def validate(cls, password: str) -> tuple[bool, list[str]]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters long")

        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")

        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")

        if cls.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")

        if cls.REQUIRE_SPECIAL:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                errors.append("Password must contain at least one special character")

        return len(errors) == 0, errors


def validate_password_strength(password: str) -> None:
    """
    Validate password strength and raise exception if invalid.

    Args:
        password: Password to validate

    Raises:
        ValidationException: If password doesn't meet requirements
    """
    from app.core.exceptions import ValidationException

    is_valid, errors = PasswordValidator.validate(password)

    if not is_valid:
        raise ValidationException(
            message="Password does not meet strength requirements",
            details={"errors": errors}
        )
