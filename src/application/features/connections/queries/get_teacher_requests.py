"""Get teacher connection requests query."""

from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.connections.dtos import (
    TeacherRequestsOutput,
    ConnectionStudentInfo,
)
from src.core.config.constants import ConnectionStatus
from src.core.exceptions import EntityNotFoundError


class GetTeacherConnectionRequestsQuery:
    """Query to get pending connection requests for a teacher."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, teacher_id: UUID) -> TeacherRequestsOutput:
        """Fetch pending connection requests with student details."""
        async with self.uow:
            teacher = await self.uow.users.get_by_id(teacher_id)
            if not teacher:
                raise EntityNotFoundError("User", teacher_id)

            connections = await self.uow.connections.list_by_teacher(
                teacher_id=teacher_id,
                status=ConnectionStatus.PENDING,
            )

            requests = []
            for conn in connections:
                student = await self.uow.users.get_by_id(conn.student_id)
                if not student:
                    continue

                requests.append(
                    ConnectionStudentInfo(
                        connection_id=conn.id,
                        student_name=student.full_name,
                        created_at=conn.created_at,
                    )
                )

            return TeacherRequestsOutput(requests=requests)
