"""Domain value objects - Immutable objects representing concepts."""

from src.domain.value_objects.email import Email
from src.domain.value_objects.pagination import PaginationParams, PaginatedResult

__all__ = [
    "Email",
    "PaginationParams",
    "PaginatedResult",
]
