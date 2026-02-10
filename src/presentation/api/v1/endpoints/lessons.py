"""Lesson endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.lessons.commands import CreateLessonCommand, SubmitFeedbackCommand
from src.application.features.lessons.queries import GetLessonQuery, ListLessonsQuery, PlayLessonQuery
from src.application.features.lessons.dtos import CreateLessonInput, SubmitFeedbackInput
from src.core.config.constants import UserRole
from src.core.exceptions import AuthorizationError, EntityNotFoundError, ValidationError
from src.domain.interfaces.services import IAIService, IStorageService
from src.presentation.api.v1.dependencies import (
    get_current_active_user,
    get_uow,
    get_ai_service,
    get_storage_service,
    require_role,
    CurrentUser,
)
from src.presentation.schemas.lesson import (
    CreateLessonRequest,
    CreateLessonResponse,
    LessonResponse,
    LessonListResponse,
    PlayLessonResponse,
    SubmitFeedbackRequest,
    SubmitFeedbackResponse,
)

router = APIRouter()


@router.post(
    "/upload",
    response_model=CreateLessonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload new lesson",
    description="""
Upload a new lesson as a teacher.

**Content-Type:** `multipart/form-data`

**Required Fields:**
- `title`: Lesson title
- `content`: Full lesson text that will be adapted by AI

**Optional Fields:**
- `description`: Short preview description
- `subject`: Subject area (Science, Math, etc.)
- `topic`: Specific topic
- `target_grade_level`: Grade level 1-12 (default: 3)
- `file`: Media file (image, PDF, video)

**What happens:**
1. Lesson is saved in DRAFT status
2. File is uploaded to cloud storage (if provided)
3. Lesson is ready for student access
    """,
    responses={
        201: {"description": "Lesson created successfully"},
        403: {"description": "Only teachers can upload lessons"},
    }
)
async def upload_lesson(
    title: str = Form(..., description="Lesson title"),
    content: str = Form(..., description="Full lesson text content"),
    description: Optional[str] = Form(None, description="Short description"),
    subject: Optional[str] = Form(None, description="Subject area"),
    topic: Optional[str] = Form(None, description="Specific topic"),
    target_grade_level: int = Form(3, description="Target grade level (1-12)"),
    file: Optional[UploadFile] = File(None, description="Optional media file"),
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER])),
    uow: IUnitOfWork = Depends(get_uow),
    storage_service: IStorageService = Depends(get_storage_service),
):
    """Upload a new lesson (teachers only)."""
    try:
        media_url = None
        media_type = None

        # Upload file if provided
        if file:
            allowed_types = {
                "application/pdf", "image/jpeg", "image/png",
                "image/gif", "image/webp", "video/mp4", "video/webm",
            }
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"File type '{file.content_type}' not allowed",
                )

            file_content = await file.read()

            max_size = 50 * 1024 * 1024  # 50MB
            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File size exceeds maximum of 50MB",
                )

            media_url = await storage_service.upload_file(
                file_content=file_content,
                file_name=file.filename,
                content_type=file.content_type,
                folder="lessons",
            )
            media_type = file.content_type

        command = CreateLessonCommand(uow)
        result = await command.execute(
            CreateLessonInput(
                teacher_id=current_user.id,
                title=title,
                original_text_content=content,
                description=description,
                subject=subject,
                topic=topic,
                target_grade_level=target_grade_level,
                media_url=media_url,
                media_type=media_type,
            )
        )

        return CreateLessonResponse(
            lesson_id=str(result.lesson_id),
            status=result.status,
            message=result.message,
        )

    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


@router.get(
    "",
    response_model=LessonListResponse,
    summary="List lessons",
    description="""
List lessons with optional filtering and pagination.

**Automatic Filtering by Role:**
- **Teachers**: See their own lessons by default
- **Students**: See lessons from their school by default
- **School Admins**: See all lessons from their school

**Query Parameters:**
- `teacher_id`: Filter by specific teacher UUID
- `school_id`: Filter by school UUID
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
    """,
    responses={
        200: {"description": "List of lessons with pagination info"},
    }
)
async def list_lessons(
    teacher_id: Optional[UUID] = None,
    school_id: Optional[UUID] = None,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: CurrentUser = Depends(get_current_active_user),
    uow: IUnitOfWork = Depends(get_uow),
):
    """List lessons with optional filtering."""
    query = ListLessonsQuery(uow)

    # Teachers see their own lessons by default
    if current_user.role == UserRole.TEACHER and not teacher_id:
        teacher_id = current_user.id

    # Students see lessons from their school
    if current_user.role == UserRole.STUDENT and not school_id:
        school_id = current_user.school_id

    result = await query.execute(
        teacher_id=teacher_id,
        school_id=school_id,
        page=page,
        page_size=page_size,
    )

    return LessonListResponse(
        lessons=[
            {
                "id": str(l.id),
                "title": l.title,
                "description": l.description,
                "subject": l.subject,
                "topic": l.topic,
                "target_grade_level": l.target_grade_level,
                "estimated_duration_minutes": l.estimated_duration_minutes,
                "status": l.status,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in result.lessons
        ],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get(
    "/{lesson_id}",
    response_model=LessonResponse,
    summary="Get lesson details",
    description="""
Get detailed information about a specific lesson.

**Returns:** Lesson metadata including teacher info.

**Note:** This returns the original lesson info, NOT personalized content.
For AI-adapted content, use `GET /lessons/{lesson_id}/play` instead.
    """,
    responses={
        200: {"description": "Lesson details"},
        404: {"description": "Lesson not found"},
    }
)
async def get_lesson(
    lesson_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get lesson details."""
    try:
        query = GetLessonQuery(uow)
        result = await query.execute(lesson_id)

        return LessonResponse(
            id=str(result.id),
            title=result.title,
            description=result.description,
            subject=result.subject,
            topic=result.topic,
            target_grade_level=result.target_grade_level,
            estimated_duration_minutes=result.estimated_duration_minutes,
            status=result.status,
            media_url=result.media_url,
            teacher_id=str(result.teacher_id),
            teacher_name=result.teacher_name,
            created_at=result.created_at.isoformat() if result.created_at else None,
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.get(
    "/{lesson_id}/play",
    response_model=PlayLessonResponse,
    summary="Play lesson with AI personalization",
    description="""
# THE CORE AI FEATURE

Get personalized lesson content adapted to the student's NeuroProfile.

**What happens:**
1. Checks if an adapted version exists for this student
2. If YES: Returns cached personalized version instantly
3. If NO: Triggers AI adaptation (may take 3-10 seconds)

**AI Adaptation includes:**
- Restructuring content for student's learning style
- Adjusting complexity to their level
- Chunking content based on attention span
- Avoiding sensory triggers
- Adding relevant activities and quizzes

**Content Block Types in Response:**

| Type | Description | Frontend Handling |
|------|-------------|-------------------|
| `heading` | Section header | Render as h2/h3 |
| `text` | Main content | Render markdown, highlight emphasis |
| `image` | Image URL | Display image |
| `image_prompt` | Image description | Generate with DALL-E or placeholder |
| `quiz` | Question + options | Interactive quiz component |
| `activity` | Hands-on task | Task card/callout |
| `summary` | Key takeaways | Highlighted box |

**Prerequisites:** Student MUST have completed assessment first.
    """,
    responses={
        200: {"description": "Personalized lesson content blocks"},
        400: {"description": "Student has no NeuroProfile (must complete assessment first)"},
        404: {"description": "Lesson not found"},
    }
)
async def play_lesson(
    lesson_id: UUID,
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
    ai_service: IAIService = Depends(get_ai_service),
):
    """Play a lesson with AI-personalized content (students only)."""
    try:
        query = PlayLessonQuery(uow, ai_service)
        result = await query.execute(lesson_id=lesson_id, student_id=current_user.id)

        return PlayLessonResponse(
            lesson_title=result.lesson_title,
            adaptation_style=result.adaptation_style,
            blocks=result.blocks,
            adapted_lesson_id=str(result.adapted_lesson_id),
            original_lesson_id=str(result.original_lesson_id),
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.post(
    "/{lesson_id}/feedback",
    response_model=SubmitFeedbackResponse,
    summary="Submit feedback on adapted content",
    description="""
Submit teacher feedback on AI-generated adapted content for model improvement.

**Purpose:** Improve AI adaptations through teacher corrections (RLHF training data).

**When to use:**
- AI made a factual error
- Content complexity doesn't match student level
- Better phrasing/explanation available
- Formatting issues

**What happens:**
1. Correction is stored in TrainingDataLog
2. Data used for future model fine-tuning (SLM training)
3. Improves adaptations for similar profiles

**Correction Types:**
- `content`: Text content correction
- `complexity`: Complexity level adjustment
- `accuracy`: Factual correction
- `formatting`: Structure/formatting fix
    """,
    responses={
        200: {"description": "Feedback recorded for AI training"},
        404: {"description": "Lesson or adapted lesson not found"},
    }
)
async def submit_feedback(
    lesson_id: UUID,
    request: SubmitFeedbackRequest,
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Submit feedback on adapted lesson content (teachers only)."""
    try:
        command = SubmitFeedbackCommand(uow)
        result = await command.execute(
            SubmitFeedbackInput(
                lesson_id=lesson_id,
                adapted_lesson_id=request.adapted_lesson_id,
                block_id=request.block_id,
                teacher_id=current_user.id,
                correction=request.correction,
                correction_type=request.correction_type,
                notes=request.notes,
            )
        )

        return result

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
