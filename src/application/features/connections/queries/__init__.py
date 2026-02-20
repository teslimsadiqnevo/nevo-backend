"""Connection queries."""

from src.application.features.connections.queries.get_student_connections import (
    GetStudentConnectionsQuery,
)
from src.application.features.connections.queries.get_teacher_requests import (
    GetTeacherConnectionRequestsQuery,
)

__all__ = [
    "GetStudentConnectionsQuery",
    "GetTeacherConnectionRequestsQuery",
]
