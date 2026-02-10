"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from src.core.config.settings import settings
from src.core.exceptions import NevoException
from src.presentation.api.v1 import api_router


# OpenAPI Tags Metadata for better documentation organization
tags_metadata = [
    {
        "name": "Authentication",
        "description": """
**User authentication operations**

Handles login, registration, and token management. All endpoints return JWT tokens for authorized access.

### Token Types
- **Access Token**: Short-lived (30 min), used for API requests
- **Refresh Token**: Long-lived (7 days), used to get new access tokens

### Flow
1. Register or Login → Get tokens
2. Use access token in `Authorization: Bearer <token>` header
3. When expired, use refresh token to get new tokens
        """,
    },
    {
        "name": "Assessment",
        "description": """
**Student onboarding assessment**

Students complete assessment questions to generate their personalized learning profile (NeuroProfile).

### Assessment Flow
1. `GET /assessment/questions` - Fetch all questions
2. Student answers questions in frontend
3. `POST /assessment/submit` - Submit all answers
4. AI generates NeuroProfile automatically

### Question Types
- `SINGLE_CHOICE` - Select one option
- `MULTIPLE_CHOICE` - Select multiple options
- `SCALE` - Rate on a scale (e.g., 1-5)
        """,
    },
    {
        "name": "Lessons",
        "description": """
**Lesson management and AI personalization**

Teachers upload lessons; students receive AI-adapted versions based on their NeuroProfile.

### Key Endpoints
- `POST /lessons/upload` - Teachers upload new lessons
- `GET /lessons/{id}/play` - **CRITICAL** - Students get personalized version

### Personalization
When a student calls `/play`, the AI:
1. Retrieves the student's NeuroProfile
2. Adapts content to their learning style
3. Adjusts complexity level
4. Chunks content based on attention span
5. Avoids sensory triggers
6. Returns structured content blocks
        """,
    },
    {
        "name": "Students",
        "description": "Student profile and dashboard endpoints. View student progress, profile, and learning statistics.",
    },
    {
        "name": "Teachers",
        "description": "Teacher dashboard and management. View lessons created, student engagement, and content performance.",
    },
    {
        "name": "Schools",
        "description": """
**School administration**

Create and manage schools, teachers, and students.

### Subscription Tiers
- `free` - Limited features
- `basic` - Standard features
- `premium` - All features

### Capacity Limits
Schools have limits on `max_teachers` and `max_students` based on subscription tier.
        """,
    },
    {
        "name": "Progress",
        "description": """
**Student progress tracking**

Real-time tracking of lesson completion, time spent, quiz scores, and learning streaks.

### Tracked Metrics
- `blocks_completed` - Content blocks viewed
- `time_spent_seconds` - Time in lesson
- `quiz_score` - In-lesson quiz results
- `streak` - Consecutive learning days
        """,
    },
    {
        "name": "Email",
        "description": """
**Customizable email sending service**

Send custom emails for any service needs. Supports both single and bulk email sending.

### Features
- Plain text and HTML support
- Bulk email (up to 100 recipients per request)
- Automatic error handling
- Uses Resend service

### Use Cases
- Welcome emails
- Notification emails
- Password resets
- Email verifications
- Newsletters
- Announcements
- Custom communications

### Endpoints
- `POST /email/send` - Send single email
- `POST /email/send-bulk` - Send bulk emails

**Note:** All emails are sent from the configured sender address (`noreply@nevolearning.com`).
        """,
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"Starting {settings.app_name} API...")
    yield
    # Shutdown
    print(f"Shutting down {settings.app_name} API...")


def custom_openapi(app: FastAPI):
    """Generate custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Nevo API",
        version="1.0.0",
        summary="AI-Powered Personalized Learning Platform",
        description="""
# Nevo Backend API

Nevo is an AI-powered personalized learning platform that adapts educational content to each student's unique learning profile.

## 🚀 Quick Start for Frontend Developers

### Base URL
- **Local**: `http://localhost:8000/api/v1`
- **Production**: `https://api.nevolearning.com/api/v1`

### Authentication
All protected endpoints require a JWT token:
```
Authorization: Bearer <access_token>
```

### Typical User Flows

#### Student Flow
```
1. POST /auth/register (role: "student")
2. POST /auth/login
3. GET /assessment/questions
4. POST /assessment/submit
5. GET /lessons
6. GET /lessons/{id}/play  ← AI-adapted content
7. POST /progress/update
```

#### Teacher Flow
```
1. POST /auth/register (role: "teacher")
2. POST /auth/login
3. POST /lessons/upload
4. GET /lessons (view own lessons)
5. POST /lessons/{id}/feedback
```

#### School Admin Flow
```
1. POST /schools (create school first)
2. POST /auth/register (role: "school_admin")
3. GET /schools/dashboard
4. GET /schools/teachers
```

#### Email Service Flow
```
1. POST /auth/login (get authentication token)
2. POST /email/send (send custom email)
   OR
   POST /email/send-bulk (send to multiple recipients)
```

---

## 📊 Core Features

### 🎯 Assessment & Profiling
Students complete an onboarding assessment that generates a **NeuroProfile**:
- Learning style (Visual, Auditory, Kinesthetic, Reading/Writing)
- Complexity tolerance level
- Attention span estimation
- Sensory sensitivities
- Interest areas

### 📚 Lesson Adaptation
The `/lessons/{id}/play` endpoint is the **core AI feature**:
1. Retrieves student's NeuroProfile
2. Adapts lesson content in real-time
3. Returns structured content blocks

### Content Block Types
```json
{
  "type": "heading|text|image|image_prompt|quiz|activity|summary",
  "content": "Block content",
  "order": 0
}
```

---

## 📧 Email Service

The email API provides flexible email sending capabilities for any service needs:

### Single Email
- `POST /email/send` - Send to one recipient
- Supports plain text and HTML
- Automatic error handling

### Bulk Email
- `POST /email/send-bulk` - Send to up to 100 recipients
- Returns success/failure counts
- Lists failed recipients

**Configuration:**
- Uses Resend service
- Sender: `noreply@nevolearning.com`
- Requires authentication

---

## 👥 User Roles

| Role | Code | Permissions |
|------|------|-------------|
| Student | `student` | Take assessments, view lessons, track progress |
| Teacher | `teacher` | Upload lessons, view engagement, provide feedback |
| School Admin | `school_admin` | Manage school, view dashboards |
| Parent | `parent` | View linked student progress |

---

## ❌ Error Handling

All errors return:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `AUTHENTICATION_ERROR` | 401 | Invalid/expired token |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `EXTERNAL_SERVICE_ERROR` | 502 | External service failure (e.g., email service) |
| `INTERNAL_ERROR` | 500 | Server error |

---

## 🔧 Development

### Run Locally
```bash
uvicorn src.app.main:app --reload
```

### Test Endpoints
Use the **"Try it out"** button in Swagger UI below!
        """,
        routes=app.routes,
        tags=tags_metadata,
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT access token (without 'Bearer ' prefix)"
        }
    }

    # Add servers
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Local Development"},
        {"url": "https://api.nevolearning.com", "description": "Production"},
    ]

    # Add contact and license info
    openapi_schema["info"]["contact"] = {
        "name": "Nevo Backend Team",
        "email": "backend@nevolearning.com",
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Nevo API",
        description="AI-powered personalized learning platform API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=tags_metadata,
        lifespan=lifespan,
        swagger_ui_parameters={
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "filter": True,
            "syntaxHighlight.theme": "monokai",
            "docExpansion": "list",
        },
    )

    # Override OpenAPI schema with custom one
    app.openapi = lambda: custom_openapi(app)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    @app.exception_handler(NevoException)
    async def nevo_exception_handler(request: Request, exc: NevoException):
        """Handle Nevo application exceptions."""
        return JSONResponse(
            status_code=_get_status_code(exc.code),
            content=exc.to_dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        if settings.is_development:
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": str(exc),
                        "details": {"type": type(exc).__name__},
                    }
                },
            )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )

    # Include API router
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Health check endpoint
    @app.get("/health", tags=["System"])
    async def health_check():
        """
        Health check endpoint.

        Returns the current status of the API server.
        Use this endpoint for load balancer health checks.
        """
        return {
            "status": "healthy",
            "app": settings.app_name,
            "environment": settings.app_env,
            "version": "1.0.0",
        }

    return app


def _get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes."""
    status_map = {
        "NOT_FOUND": 404,
        "VALIDATION_ERROR": 400,
        "AUTHENTICATION_ERROR": 401,
        "AUTHORIZATION_ERROR": 403,
        "CONFLICT": 409,
        "RATE_LIMIT_EXCEEDED": 429,
        "EXTERNAL_SERVICE_ERROR": 502,
        "INTERNAL_ERROR": 500,
    }
    return status_map.get(error_code, 500)


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
    )
