"""List teacher lessons with filtering query."""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.core.config.constants import LessonStatus
from src.domain.value_objects.pagination import PaginationParams


@dataclass(frozen=True)
class ListTeacherLessonsInput:
    """Input for listing teacher lessons."""

    teacher_id: UUID
    search: Optional[str] = None
    status: Optional[str] = None
    subject: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 20


@dataclass
class TeacherLessonItem:
    """A lesson item in the teacher's lesson list."""

    id: UUID
    title: str
    subject: Optional[str]
    topic: Optional[str]
    status: str
    target_grade_level: int
    estimated_duration_minutes: int
    created_at: str
    published_at: Optional[str]
    assignment_count: int


@dataclass
class TeacherLessonListOutput:
    """Output for teacher lesson list."""

    lessons: List[TeacherLessonItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class ListTeacherLessonsQuery:
    """Query to list teacher lessons with search, filter, and sort."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: ListTeacherLessonsInput) -> TeacherLessonListOutput:
        async with self.uow:
            # Map status string to enum
            status_filter = None
            if input_dto.status:
                try:
                    status_filter = LessonStatus(input_dto.status)
                except ValueError:
                    pass

            result = await self.uow.lessons.list_by_teacher_filtered(
                teacher_id=input_dto.teacher_id,
                search=input_dto.search,
                status_filter=status_filter,
                subject_filter=input_dto.subject,
                sort_by=input_dto.sort_by,
                sort_order=input_dto.sort_order,
                pagination=PaginationParams(
                    page=input_dto.page, page_size=input_dto.page_size
                ),
            )

            lessons = []
            for lesson in result.items:
                # Count assignments for this lesson
                assignments = await self.uow.lesson_assignments.list_by_lesson(
                    lesson.id
                )
                lessons.append(
                    TeacherLessonItem(
                        id=lesson.id,
                        title=lesson.title,
                        subject=lesson.subject,
                        topic=lesson.topic,
                        status=lesson.status.value if hasattr(lesson.status, 'value') else str(lesson.status),
                        target_grade_level=lesson.target_grade_level,
                        estimated_duration_minutes=lesson.estimated_duration_minutes,
                        created_at=lesson.created_at.isoformat() if lesson.created_at else "",
                        published_at=lesson.published_at.isoformat() if lesson.published_at else None,
                        assignment_count=len(assignments),
                    )
                )

            return TeacherLessonListOutput(
                lessons=lessons,
                total=result.total,
                page=result.page,
                page_size=result.page_size,
                total_pages=result.total_pages,
            )
