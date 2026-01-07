"""Base exception classes for the application."""

from typing import Any, Dict, Optional


class NevoException(Exception):
    """Base exception for all Nevo application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class EntityNotFoundError(NevoException):
    """Raised when a requested entity is not found."""

    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        message: Optional[str] = None,
    ):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(
            message=message or f"{entity_type} with id '{entity_id}' not found",
            code="NOT_FOUND",
            details={"entity_type": entity_type, "entity_id": str(entity_id)},
        )


class ValidationError(NevoException):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field, **(details or {})},
        )


class AuthenticationError(NevoException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(NevoException):
    """Raised when user lacks permission for an action."""

    def __init__(
        self,
        message: str = "You don't have permission to perform this action",
        required_role: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            details={"required_role": required_role, **(details or {})},
        )


class ConflictError(NevoException):
    """Raised when there's a conflict (e.g., duplicate entry)."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="CONFLICT",
            details={"field": field, **(details or {})},
        )


class ExternalServiceError(NevoException):
    """Raised when an external service fails."""

    def __init__(
        self,
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=f"{service_name} service error: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service_name, **(details or {})},
        )


class AIServiceError(ExternalServiceError):
    """Raised when AI service (Gemini/OpenAI) fails."""

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            service_name="AI",
            message=message,
            details={"model": model, **(details or {})},
        )


class StorageError(ExternalServiceError):
    """Raised when storage service (S3/GCS) fails."""

    def __init__(
        self,
        message: str,
        bucket: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            service_name="Storage",
            message=message,
            details={"bucket": bucket, **(details or {})},
        )


class RateLimitError(NevoException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after, **(details or {})},
        )
