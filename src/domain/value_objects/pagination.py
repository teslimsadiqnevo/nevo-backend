"""Pagination value objects."""

from dataclasses import dataclass
from typing import Generic, List, TypeVar

from src.core.config.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


@dataclass(frozen=True)
class PaginationParams:
    """Pagination parameters value object."""

    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE

    def __post_init__(self):
        # Validate and normalize
        object.__setattr__(self, "page", max(1, self.page))
        object.__setattr__(
            self, "page_size", max(1, min(self.page_size, MAX_PAGE_SIZE))
        )

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database queries."""
        return self.page_size


@dataclass
class PaginatedResult(Generic[T]):
    """Paginated result container."""

    items: List[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "items": self.items,
            "pagination": {
                "total": self.total,
                "page": self.page,
                "page_size": self.page_size,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_previous": self.has_previous,
            },
        }
