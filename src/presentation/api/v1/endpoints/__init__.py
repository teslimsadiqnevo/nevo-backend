"""API endpoints module."""

from src.presentation.api.v1.endpoints import (
    auth,
    assessments,
    chat,
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
    "chat",
    "email",
    "lessons",
    "students",
    "teachers",
    "schools",
    "progress",
]
