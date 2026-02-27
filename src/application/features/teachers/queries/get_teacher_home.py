"""Get teacher home dashboard query."""

from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.teachers.dtos import TeacherHomeOutput
from src.core.config.constants import ConnectionStatus, LessonStatus
from src.core.exceptions import EntityNotFoundError


class GetTeacherHomeQuery:
    """Query to get teacher home dashboard data."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, teacher_id: UUID) -> TeacherHomeOutput:
        async with self.uow:
            teacher = await self.uow.users.get_by_id(teacher_id)
            if not teacher:
                raise EntityNotFoundError("Teacher", str(teacher_id))

            # Count connected students (accepted connections)
            connections = await self.uow.connections.list_by_teacher(
                teacher_id, status=ConnectionStatus.ACCEPTED
            )
            total_students = len(connections)

            # Count lessons
            total_lessons = await self.uow.lessons.count_by_teacher(teacher_id)
            published_lessons = await self.uow.lessons.count_by_teacher_and_status(
                teacher_id, LessonStatus.PUBLISHED
            )
            draft_lessons = await self.uow.lessons.count_by_teacher_and_status(
                teacher_id, LessonStatus.DRAFT
            )

            # Count total assignments
            total_assignments = await self.uow.lesson_assignments.count_by_teacher(
                teacher_id
            )

            # Students needing help: students with no progress or incomplete assignments
            # For now, count students who have 0 completed assignments
            students_needing_help = 0
            for conn in connections:
                student_assignments = await self.uow.lesson_assignments.list_by_student(
                    conn.student_id
                )
                # Filter to this teacher's assignments
                teacher_assignments = [
                    a for a in student_assignments if a.teacher_id == teacher_id
                ]
                if teacher_assignments:
                    completed = sum(
                        1 for a in teacher_assignments if a.status.value == "completed"
                    )
                    if completed == 0:
                        students_needing_help += 1

            return TeacherHomeOutput(
                teacher_name=teacher.full_name,
                total_classes=1,  # Each teacher has one class for now
                total_lessons_assigned=total_assignments,
                students_needing_help=students_needing_help,
                total_students=total_students,
                total_lessons=total_lessons,
                published_lessons=published_lessons,
                draft_lessons=draft_lessons,
            )
