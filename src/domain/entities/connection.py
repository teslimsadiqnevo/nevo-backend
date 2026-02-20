"""Connection entity - Student-teacher connections."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.core.config.constants import ConnectionStatus


@dataclass
class Connection:
    """
    Connection entity for student-teacher relationships.

    Students send connection requests to teachers via class codes.
    Teachers can accept or reject requests.
    """

    student_id: UUID
    teacher_id: UUID
    status: ConnectionStatus = ConnectionStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
