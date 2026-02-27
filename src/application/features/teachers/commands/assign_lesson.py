"""Assign lesson command."""

from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.teachers.dtos import AssignLessonInput, AssignLessonOutput
from src.core.config.constants import AssignmentTarget, ConnectionStatus, LessonStatus
from src.core.exceptions import AuthorizationError, EntityNotFoundError, ValidationError
from src.domain.entities.lesson_assignment import LessonAssignment


class AssignLessonCommand:
    """Command to assign a lesson to students."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: AssignLessonInput) -> AssignLessonOutput:
        async with self.uow:
            # Validate lesson exists and belongs to teacher
            lesson = await self.uow.lessons.get_by_id(input_dto.lesson_id)
            if not lesson:
                raise EntityNotFoundError("Lesson", str(input_dto.lesson_id))

            if lesson.teacher_id != input_dto.teacher_id:
                raise AuthorizationError("You can only assign your own lessons")

            if lesson.status != LessonStatus.PUBLISHED:
                raise ValidationError("Only published lessons can be assigned")

            # Determine target students
            if input_dto.target == "class":
                # Assign to all connected students
                connections = await self.uow.connections.list_by_teacher(
                    input_dto.teacher_id, status=ConnectionStatus.ACCEPTED
                )
                student_ids = [conn.student_id for conn in connections]
                assignment_type = AssignmentTarget.CLASS
            else:
                # Assign to specific students
                if not input_dto.student_ids:
                    raise ValidationError(
                        "student_ids required for individual assignment"
                    )
                student_ids = input_dto.student_ids
                assignment_type = AssignmentTarget.INDIVIDUAL

            if not student_ids:
                raise ValidationError("No students to assign the lesson to")

            # Create assignments, skip duplicates
            assigned_count = 0
            skipped_count = 0

            for student_id in student_ids:
                existing = await self.uow.lesson_assignments.get_by_lesson_and_student(
                    input_dto.lesson_id, student_id
                )
                if existing:
                    skipped_count += 1
                    continue

                assignment = LessonAssignment(
                    lesson_id=input_dto.lesson_id,
                    student_id=student_id,
                    teacher_id=input_dto.teacher_id,
                    assignment_type=assignment_type,
                )
                await self.uow.lesson_assignments.create(assignment)
                assigned_count += 1

            await self.uow.commit()

            return AssignLessonOutput(
                lesson_id=input_dto.lesson_id,
                assigned_count=assigned_count,
                skipped_count=skipped_count,
                message=f"Lesson assigned to {assigned_count} student(s)"
                + (
                    f", {skipped_count} already assigned"
                    if skipped_count > 0
                    else ""
                ),
            )
