"""API endpoints module."""

from src.presentation.api.v1.endpoints import (
    auth,
    assessments,
    lessons,
    students,
    teachers,
    schools,
    progress,
)

__all__ = [
    "auth",
    "assessments",
    "lessons",
    "students",
    "teachers",
    "schools",
    "progress",
]
