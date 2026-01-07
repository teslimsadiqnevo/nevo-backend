"""Custom exceptions for the application."""

from src.core.exceptions.base import (
    NevoException,
    EntityNotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ExternalServiceError,
    AIServiceError,
    StorageError,
    RateLimitError,
)

__all__ = [
    "NevoException",
    "EntityNotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "ExternalServiceError",
    "AIServiceError",
    "StorageError",
    "RateLimitError",
]
