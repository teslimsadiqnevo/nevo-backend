"""Get assignable students query."""

from typing import List
from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.teachers.dtos import AssignableStudentOutput
from src.core.config.constants import ConnectionStatus


class GetAssignableStudentsQuery:
    """Query to get students that a teacher can assign lessons to."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, teacher_id: UUID) -> List[AssignableStudentOutput]:
        async with self.uow:
            # Get accepted connections for this teacher
            connections = await self.uow.connections.list_by_teacher(
                teacher_id, status=ConnectionStatus.ACCEPTED
            )

            students = []
            for conn in connections:
                student = await self.uow.users.get_by_id(conn.student_id)
                if student and student.is_active:
                    students.append(
                        AssignableStudentOutput(
                            id=student.id,
                            first_name=student.first_name,
                            last_name=student.last_name,
                            email=student.email,
                        )
                    )

            return students
