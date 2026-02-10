"""API endpoints module."""

from src.presentation.api.v1.endpoints import (
    auth,
    assessments,
    email,
    lessons,
    students,
    teachers,
    schools,
    progress,
)

__all__ = [
    "auth",
    "assessments",
    "email",
    "lessons",
    "students",
    "teachers",
    "schools",
    "progress",
]
