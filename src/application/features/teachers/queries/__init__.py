"""Teacher queries."""

from src.application.features.teachers.queries.get_teacher_home import GetTeacherHomeQuery
from src.application.features.teachers.queries.get_assignable_students import GetAssignableStudentsQuery
from src.application.features.teachers.queries.list_teacher_lessons import (
    ListTeacherLessonsQuery,
    ListTeacherLessonsInput,
    TeacherLessonListOutput,
)

__all__ = [
    "GetTeacherHomeQuery",
    "GetAssignableStudentsQuery",
    "ListTeacherLessonsQuery",
    "ListTeacherLessonsInput",
    "TeacherLessonListOutput",
]
