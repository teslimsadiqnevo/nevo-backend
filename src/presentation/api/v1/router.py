"""API v1 router - Combines all endpoint routers."""

from fastapi import APIRouter

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

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(assessments.router, prefix="/assessment", tags=["Assessment"])
api_router.include_router(email.router, prefix="/email", tags=["Email"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["Teachers"])
api_router.include_router(schools.router, prefix="/schools", tags=["Schools"])
api_router.include_router(progress.router, prefix="/progress", tags=["Progress"])
