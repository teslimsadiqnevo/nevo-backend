"""Connection Data Transfer Objects."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass(frozen=True)
class SendConnectionRequestInput:
    """Input for sending a connection request."""

    student_id: UUID
    class_code: str


@dataclass
class SendConnectionRequestOutput:
    """Output after sending a connection request."""

    connection_id: UUID
    teacher_name: str
    status: str


@dataclass(frozen=True)
class RespondToRequestInput:
    """Input for responding to a connection request."""

    teacher_id: UUID
    connection_id: UUID
    action: str  # "accept" or "reject"


@dataclass
class RespondToRequestOutput:
    """Output after responding to a request."""

    connection_id: UUID
    status: str


@dataclass
class ConnectionTeacherInfo:
    """Teacher info for a student's connection."""

    connection_id: UUID
    teacher_name: str
    subject: Optional[str]
    created_at: datetime


@dataclass
class StudentConnectionsOutput:
    """Output for student's connections list."""

    nevo_id: Optional[str]
    pending: List[ConnectionTeacherInfo] = field(default_factory=list)
    connected: List[ConnectionTeacherInfo] = field(default_factory=list)


@dataclass
class ConnectionStudentInfo:
    """Student info for a teacher's connection request."""

    connection_id: UUID
    student_name: str
    created_at: datetime


@dataclass
class TeacherRequestsOutput:
    """Output for teacher's pending connection requests."""

    requests: List[ConnectionStudentInfo] = field(default_factory=list)


@dataclass(frozen=True)
class RemoveConnectionInput:
    """Input for removing a connection."""

    student_id: UUID
    connection_id: UUID


@dataclass
class ClassCodeOutput:
    """Output for teacher's class code."""

    class_code: str
