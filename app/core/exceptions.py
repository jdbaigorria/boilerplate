"""
Custom exceptions for the application.
All business logic exceptions should inherit from AppException.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class UnauthorizedException(AppException):
    """Exception raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code=401, details=details)


class ForbiddenException(AppException):
    """Exception raised when user lacks required permissions."""

    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code=403, details=details)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code=404, details=details)


class ConflictException(AppException):
    """Exception raised when there's a conflict (e.g., duplicate resource)."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code=409, details=details)


class ValidationException(AppException):
    """Exception raised when validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code=422, details=details)


class RateLimitException(AppException):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.retry_after = retry_after
        if retry_after and details:
            details["retry_after"] = retry_after
        super().__init__(message, status_code=429, details=details)


class BadRequestException(AppException):
    """Exception raised for malformed requests."""

    def __init__(
        self,
        message: str = "Bad request",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code=400, details=details)


class InternalServerException(AppException):
    """Exception raised for internal server errors."""

    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code=500, details=details)


class ServiceUnavailableException(AppException):
    """Exception raised when a service is temporarily unavailable."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code=503, details=details)


# Domain-specific exceptions

class UserAlreadyExistsException(ConflictException):
    """Exception raised when trying to create a user that already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"User with email '{email}' already exists",
            details={"email": email}
        )


class InvalidCredentialsException(UnauthorizedException):
    """Exception raised when login credentials are invalid."""

    def __init__(self) -> None:
        super().__init__(message="Invalid email or password")


class TokenExpiredException(UnauthorizedException):
    """Exception raised when a token has expired."""

    def __init__(self, token_type: str = "token") -> None:
        super().__init__(
            message=f"{token_type.capitalize()} has expired",
            details={"token_type": token_type}
        )


class InvalidTokenException(UnauthorizedException):
    """Exception raised when a token is invalid."""

    def __init__(self, token_type: str = "token") -> None:
        super().__init__(
            message=f"Invalid {token_type}",
            details={"token_type": token_type}
        )


class UserNotActiveException(ForbiddenException):
    """Exception raised when a user account is not active."""

    def __init__(self) -> None:
        super().__init__(message="User account is not active")


class EmailNotVerifiedException(ForbiddenException):
    """Exception raised when email verification is required."""

    def __init__(self) -> None:
        super().__init__(message="Email verification required")


class OrganizationNotFoundException(NotFoundException):
    """Exception raised when an organization is not found."""

    def __init__(self, org_id: str) -> None:
        super().__init__(
            message=f"Organization '{org_id}' not found",
            details={"organization_id": org_id}
        )


class SubscriptionNotFoundException(NotFoundException):
    """Exception raised when a subscription is not found."""

    def __init__(self, subscription_id: str) -> None:
        super().__init__(
            message=f"Subscription '{subscription_id}' not found",
            details={"subscription_id": subscription_id}
        )


class SubscriptionLimitException(ForbiddenException):
    """Exception raised when a subscription limit is reached."""

    def __init__(self, limit_type: str, limit: int) -> None:
        super().__init__(
            message=f"Subscription limit reached: {limit_type} (max: {limit})",
            details={"limit_type": limit_type, "limit": limit}
        )


class FeatureNotAvailableException(ForbiddenException):
    """Exception raised when a feature is not available in the current plan."""

    def __init__(self, feature: str) -> None:
        super().__init__(
            message=f"Feature '{feature}' is not available in your current plan",
            details={"feature": feature}
        )


class InvitationNotFoundException(NotFoundException):
    """Exception raised when an invitation is not found."""

    def __init__(self, invitation_id: str) -> None:
        super().__init__(
            message=f"Invitation '{invitation_id}' not found",
            details={"invitation_id": invitation_id}
        )


class InvitationExpiredException(BadRequestException):
    """Exception raised when an invitation has expired."""

    def __init__(self) -> None:
        super().__init__(message="Invitation has expired")


class InvitationAlreadyAcceptedException(BadRequestException):
    """Exception raised when an invitation has already been accepted."""

    def __init__(self) -> None:
        super().__init__(message="Invitation has already been accepted")


class NotOrganizationMemberException(ForbiddenException):
    """Exception raised when a user is not a member of an organization."""

    def __init__(self, org_id: str) -> None:
        super().__init__(
            message=f"You are not a member of organization '{org_id}'",
            details={"organization_id": org_id}
        )


class InsufficientPermissionsException(ForbiddenException):
    """Exception raised when a user lacks specific permissions."""

    def __init__(self, required_permission: str) -> None:
        super().__init__(
            message=f"Insufficient permissions. Required: {required_permission}",
            details={"required_permission": required_permission}
        )
