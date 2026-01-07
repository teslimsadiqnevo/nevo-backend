"""List lessons query."""

from typing import Optional
from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.lessons.dtos import LessonListOutput, LessonOutput
from src.domain.value_objects.pagination import PaginationParams


class ListLessonsQuery:
    """Query to list lessons with filtering."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(
        self,
        teacher_id: Optional[UUID] = None,
        school_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> LessonListOutput:
        """List lessons with optional filtering."""
        pagination = PaginationParams(page=page, page_size=page_size)

        async with self.uow:
            if teacher_id:
                result = await self.uow.lessons.list_by_teacher(
                    teacher_id=teacher_id,
                    pagination=pagination,
                )
            elif school_id:
                result = await self.uow.lessons.list_by_school(
                    school_id=school_id,
                    pagination=pagination,
                )
            else:
                result = await self.uow.lessons.list_published(
                    pagination=pagination,
                )

            lessons = [
                LessonOutput(
                    id=lesson.id,
                    title=lesson.title,
                    description=lesson.description,
                    subject=lesson.subject,
                    topic=lesson.topic,
                    target_grade_level=lesson.target_grade_level,
                    estimated_duration_minutes=lesson.estimated_duration_minutes,
                    status=lesson.status.value,
                    media_url=lesson.media_url,
                    media_type=lesson.media_type,
                    tags=lesson.tags,
                    teacher_id=lesson.teacher_id,
                    created_at=lesson.created_at,
                    view_count=lesson.view_count,
                    adaptation_count=lesson.adaptation_count,
                )
                for lesson in result.items
            ]

            return LessonListOutput(
                lessons=lessons,
                total=result.total,
                page=result.page,
                page_size=result.page_size,
                total_pages=result.total_pages,
            )
