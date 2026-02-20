"""Get student connections query."""

from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.connections.dtos import (
    StudentConnectionsOutput,
    ConnectionTeacherInfo,
)
from src.core.config.constants import ConnectionStatus
from src.core.exceptions import EntityNotFoundError


class GetStudentConnectionsQuery:
    """Query to get a student's connections (pending + accepted)."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, student_id: UUID) -> StudentConnectionsOutput:
        """Fetch student's connections with teacher details."""
        async with self.uow:
            student = await self.uow.users.get_by_id(student_id)
            if not student:
                raise EntityNotFoundError("User", student_id)

            connections = await self.uow.connections.list_by_student(student_id)

            pending = []
            connected = []

            for conn in connections:
                if conn.status == ConnectionStatus.REJECTED:
                    continue

                teacher = await self.uow.users.get_by_id(conn.teacher_id)
                if not teacher:
                    continue

                # Get teacher's primary subject from their most recent published lesson
                subject = await self._get_teacher_subject(conn.teacher_id)

                info = ConnectionTeacherInfo(
                    connection_id=conn.id,
                    teacher_name=teacher.full_name,
                    subject=subject,
                    created_at=conn.created_at,
                )

                if conn.status == ConnectionStatus.PENDING:
                    pending.append(info)
                elif conn.status == ConnectionStatus.ACCEPTED:
                    connected.append(info)

            return StudentConnectionsOutput(
                nevo_id=student.nevo_id,
                pending=pending,
                connected=connected,
            )

    async def _get_teacher_subject(self, teacher_id: UUID) -> str:
        """Get the teacher's primary subject from their lessons."""
        from src.domain.value_objects.pagination import PaginationParams

        result = await self.uow.lessons.list_by_teacher(
            teacher_id=teacher_id,
            pagination=PaginationParams(page=1, page_size=1),
        )
        if result.items and result.items[0].subject:
            return result.items[0].subject
        return ""
