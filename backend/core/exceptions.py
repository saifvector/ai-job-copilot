from typing import Any, Dict, Optional


class AppException(Exception):
    """
    Base domain exception for all AI Job Copilot custom errors.
    Standardized with error categories:
    - Validation
    - Authentication
    - Database
    - AI Provider
    - External Provider
    """

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        code: str = "INTERNAL_ERROR",
        category: str = "General",
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.category = category
        self.status_code = status_code
        self.details = details or {}


class NotFoundException(AppException):
    def __init__(self, resource: str, identifier: Optional[Any] = None, details: Optional[Any] = None):
        if identifier is not None:
            message = f"{resource} with identifier '{identifier}' was not found."
        else:
            message = resource
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            category="Validation",
            status_code=404,
            details=details,
        )


class BadRequestException(AppException):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            category="Validation",
            status_code=400,
            details=details,
        )


class ValidationException(AppException):
    def __init__(self, message: str = "Data validation error.", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            category="Validation",
            status_code=422,
            details=details,
        )


class ConflictException(AppException):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="CONFLICT",
            category="Validation",
            status_code=409,
            details=details,
        )


class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication failed.", code: str = "AUTH_FAILED", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code=code,
            category="Authentication",
            status_code=401,
            details=details,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication is required to access this resource."):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            category="Authentication",
            status_code=401,
        )


class TokenExpiredException(AuthenticationException):
    def __init__(self, message: str = "Authentication token has expired."):
        super().__init__(
            message=message,
            code="TOKEN_EXPIRED",
        )


class TokenRevokedException(AuthenticationException):
    def __init__(self, message: str = "Authentication token has been revoked or session terminated."):
        super().__init__(
            message=message,
            code="TOKEN_REVOKED",
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            category="Authentication",
            status_code=403,
        )


class DatabaseException(AppException):
    def __init__(self, message: str = "Database operation failed.", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            category="Database",
            status_code=503,
            details=details,
        )


class AIServiceException(AppException):
    def __init__(self, message: str = "AI inference service error.", details: Optional[Any] = None, status_code: int = 502):
        super().__init__(
            message=message,
            code="AI_PROVIDER_ERROR",
            category="AI Provider",
            status_code=status_code,
            details=details,
        )


class AIQuotaExceededException(AppException):
    def __init__(self, message: str = "AI consumption budget limit reached for current billing cycle.", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="AI_BUDGET_EXCEEDED",
            category="AI Provider",
            status_code=429,
            details=details,
        )


class ExternalProviderException(AppException):
    def __init__(self, provider: str, message: str = "External provider communication failed.", details: Optional[Any] = None):
        super().__init__(
            message=f"[{provider}] {message}",
            code="EXTERNAL_PROVIDER_ERROR",
            category="External Provider",
            status_code=502,
            details=details,
        )


class RateLimitException(AppException):
    def __init__(self, message: str = "Too many requests. Please slow down.", retry_after: int = 60):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            category="Authentication",
            status_code=429,
            details={"retry_after_seconds": retry_after},
        )


# Convenience aliases for standard Pythonic naming
AuthenticationError = AuthenticationException
AuthorizationError = ForbiddenException
RateLimitExceededError = RateLimitException
DatabaseError = DatabaseException
ValidationError = ValidationException
