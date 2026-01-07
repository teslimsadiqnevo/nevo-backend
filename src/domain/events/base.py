"""Base domain event class."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    """Base class for all domain events."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        """Get the event type name."""
        return self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "metadata": self.metadata,
        }
