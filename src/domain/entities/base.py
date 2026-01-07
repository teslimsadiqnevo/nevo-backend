"""Base entity classes."""

from abc import ABC
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Entity(ABC):
    """Base class for all domain entities."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class AggregateRoot(Entity):
    """Base class for aggregate roots."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._domain_events: list = []

    def add_domain_event(self, event) -> None:
        """Add a domain event to be dispatched."""
        self._domain_events.append(event)

    def clear_domain_events(self) -> list:
        """Clear and return all domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
