# Nevo API Documentation

> **Version**: 1.0.0
> **Base URL**: `http://localhost:8000/api/v1`
> **Swagger UI**: `http://localhost:8000/docs`
> **ReDoc**: `http://localhost:8000/redoc`

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
   - [Auth](#auth-endpoints)
   - [Assessment](#assessment-endpoints)
   - [Lessons](#lesson-endpoints)
   - [Progress](#progress-endpoints)
   - [Schools](#school-endpoints)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [User Flows](#user-flows)
7. [WebSocket Events](#websocket-events-coming-soon)

---

## Getting Started

### Base URL
```
Development: http://localhost:8000/api/v1
Production:  https://api.nevo.com/api/v1
```

### Headers
All requests should include:
```http
Content-Type: application/json
```

Protected endpoints require:
```http
Authorization: Bearer <access_token>
```

### Quick Test
```bash
# Health check
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "app": "Nevo",
  "environment": "development",
  "version": "1.0.0"
}
```

---

## Authentication

### How It Works

1. User registers or logs in → receives `access_token` + `refresh_token`
2. Use `access_token` in `Authorization` header for API calls
3. When access token expires (30 min), use `refresh_token` to get new tokens
4. Refresh tokens expire after 7 days → user must login again

### Token Storage (Frontend)
```javascript
// Recommended: Store in memory + httpOnly cookie for refresh token
// NOT recommended: localStorage (XSS vulnerable)

// Example with axios interceptor
axios.interceptors.request.use(config => {
  const token = getAccessToken(); // from memory/state
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## Endpoints

### Auth Endpoints

#### POST /auth/register
Create a new user account.

**Request:**
```json
{
  "email": "student@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "school_id": "uuid-of-school",
  "phone_number": "+2341234567890"
}
```

**Role Options:**
- `student` - Requires `school_id`
- `teacher` - Requires `school_id`
- `school_admin` - Requires `school_id`
- `parent` - Optional `school_id`

**Response (201):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "role": "student",
  "message": "User registered successfully"
}
```

**Errors:**
- `409` - Email already exists
- `400` - Invalid role or missing school_id

---

#### POST /auth/login
Authenticate and receive tokens.

**Request:**
```json
{
  "email": "student@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "student@example.com",
    "role": "student",
    "name": "John Doe",
    "school_id": "uuid-of-school"
  }
}
```

**Errors:**
- `401` - Invalid email or password
- `401` - Account is deactivated

---

#### POST /auth/refresh
Get new tokens using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

### Assessment Endpoints

#### GET /assessment/questions
Get onboarding assessment questions.

**Authorization:** None required

**Response (200):**
```json
{
  "questions": [
    {
      "id": 1,
      "text": "How do you prefer to learn new things?",
      "type": "SINGLE_CHOICE",
      "category": "learning_style",
      "options": [
        "Watching videos or looking at pictures",
        "Listening to explanations",
        "Doing hands-on activities",
        "Reading and writing notes"
      ],
      "scale_min": 1,
      "scale_max": 5,
      "is_required": true
    },
    {
      "id": 2,
      "text": "Which of these things bother you when learning?",
      "type": "MULTIPLE_CHOICE",
      "category": "sensory_triggers",
      "options": [
        "Loud sounds",
        "Bright or flashing lights",
        "Crowded or busy visuals",
        "Fast-changing content",
        "None of these"
      ],
      "is_required": true
    },
    {
      "id": 3,
      "text": "How long can you focus on one activity without getting tired?",
      "type": "SINGLE_CHOICE",
      "category": "attention_span",
      "options": [
        "5-10 minutes",
        "10-20 minutes",
        "20-30 minutes",
        "More than 30 minutes"
      ],
      "is_required": true
    }
    // ... more questions
  ],
  "total_questions": 8,
  "categories": [
    "learning_style",
    "sensory_triggers",
    "attention_span",
    "complexity_preference",
    "interests",
    "reading_level",
    "confidence"
  ]
}
```

---

#### POST /assessment/submit
Submit assessment answers and generate NeuroProfile.

**Authorization:** Required (Student only)

**Request:**
```json
{
  "answers": [
    { "question_id": 1, "value": "Watching videos or looking at pictures" },
    { "question_id": 2, "value": ["Loud sounds", "Bright or flashing lights"] },
    { "question_id": 3, "value": "10-20 minutes" },
    { "question_id": 4, "value": "medium" },
    { "question_id": 5, "value": ["science", "art", "music"] },
    { "question_id": 6, "value": "grade_3_5" },
    { "question_id": 7, "value": 4 },
    { "question_id": 8, "value": 3 }
  ]
}
```

**Response (200):**
```json
{
  "status": "completed",
  "message": "Assessment completed and profile generated",
  "assessment_id": "550e8400-e29b-41d4-a716-446655440001",
  "profile_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**What Happens:**
1. Answers are saved to database
2. AI (Gemini) analyzes answers
3. NeuroProfile is created with:
   - `learning_style`: VISUAL | AUDITORY | KINESTHETIC | READING_WRITING
   - `complexity_tolerance`: LOW | MEDIUM | HIGH
   - `attention_span_minutes`: number
   - `sensory_triggers`: array of triggers to avoid
   - `interests`: array of interests
   - `reading_level`: grade level string

---

### Lesson Endpoints

#### POST /lessons/upload
Upload a new lesson (Teachers only).

**Authorization:** Required (Teacher only)

**Content-Type:** `multipart/form-data`

**Request:**
```
title: "Introduction to Photosynthesis"
content: "Photosynthesis is the process by which plants convert sunlight..."
description: "Learn how plants make their own food"
subject: "Science"
topic: "Biology - Plants"
target_grade_level: 5
file: (optional) lesson_image.jpg
```

**Response (201):**
```json
{
  "lesson_id": "550e8400-e29b-41d4-a716-446655440003",
  "status": "draft",
  "message": "Lesson uploaded successfully"
}
```

---

#### GET /lessons
List lessons with optional filtering.

**Authorization:** Required

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `teacher_id` | UUID | Filter by teacher |
| `school_id` | UUID | Filter by school |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 20) |

**Response (200):**
```json
{
  "lessons": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "title": "Introduction to Photosynthesis",
      "description": "Learn how plants make their own food",
      "subject": "Science",
      "topic": "Biology - Plants",
      "target_grade_level": 5,
      "estimated_duration_minutes": 15,
      "status": "published",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20,
  "total_pages": 2
}
```

---

#### GET /lessons/{lesson_id}
Get lesson details.

**Authorization:** Required

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "title": "Introduction to Photosynthesis",
  "description": "Learn how plants make their own food",
  "subject": "Science",
  "topic": "Biology - Plants",
  "target_grade_level": 5,
  "estimated_duration_minutes": 15,
  "status": "published",
  "media_url": "https://s3.amazonaws.com/nevo/lessons/image.jpg",
  "teacher_id": "550e8400-e29b-41d4-a716-446655440004",
  "teacher_name": "Jane Smith",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### GET /lessons/{lesson_id}/play ⭐ CRITICAL ENDPOINT
Get personalized lesson content for a student.

**Authorization:** Required (Student only)

**This is the core AI feature!**

**Response (200):**
```json
{
  "lesson_title": "Introduction to Photosynthesis",
  "adaptation_style": "Visual learning style with medium complexity, chunked for 15-minute attention span",
  "blocks": [
    {
      "id": "block_1",
      "type": "heading",
      "content": "🌱 How Plants Make Food",
      "order": 0
    },
    {
      "id": "block_2",
      "type": "image_prompt",
      "content": "A colorful diagram showing a plant with arrows indicating sunlight, water, and carbon dioxide going in, and oxygen and glucose coming out",
      "order": 1
    },
    {
      "id": "block_3",
      "type": "text",
      "content": "Plants are amazing! They can make their own food using just sunlight, water, and air. This process is called **photosynthesis**.",
      "order": 2,
      "emphasis": ["photosynthesis"]
    },
    {
      "id": "block_4",
      "type": "activity",
      "content": "🎨 Draw a plant and label: 1) Where sunlight enters 2) Where water comes from 3) Where the food goes",
      "order": 3
    },
    {
      "id": "block_5",
      "type": "quiz",
      "content": "Quick check!",
      "question": "What do plants need to make food?",
      "options": [
        "Sunlight, water, and air",
        "Soil and fertilizer only",
        "Meat and vegetables",
        "Rain only"
      ],
      "correct_index": 0,
      "order": 4
    },
    {
      "id": "block_6",
      "type": "summary",
      "content": "✨ **Key Takeaway**: Plants use sunlight + water + air to make their own food through photosynthesis!",
      "order": 5
    }
  ],
  "adapted_lesson_id": "550e8400-e29b-41d4-a716-446655440005",
  "original_lesson_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

**Content Block Types:**

| Type | Description | Frontend Handling |
|------|-------------|-------------------|
| `heading` | Section header | Render as h2/h3 |
| `text` | Main content | Render markdown |
| `image` | Actual image URL | Display image |
| `image_prompt` | AI image description | Generate with DALL-E or show placeholder |
| `quiz` | Interactive question | Show options, check answer |
| `activity` | Hands-on task | Display as callout/card |
| `summary` | Key takeaways | Display as highlighted box |

---

#### POST /lessons/{lesson_id}/feedback
Submit feedback on adapted content (Teachers only).

**Authorization:** Required (Teacher only)

**Request:**
```json
{
  "adapted_lesson_id": "550e8400-e29b-41d4-a716-446655440005",
  "block_id": "block_3",
  "correction": "Plants are amazing! They create their own food using sunlight, water, and carbon dioxide from the air. This process is called **photosynthesis** (foto-SIN-thuh-sis).",
  "correction_type": "content",
  "notes": "Added pronunciation guide for the term"
}
```

**Response (200):**
```json
{
  "status": "recorded",
  "message": "Feedback recorded for AI training"
}
```

---

### Progress Endpoints

#### POST /progress/update
Update student's lesson progress.

**Authorization:** Required (Student only)

**Request:**
```json
{
  "lesson_id": "550e8400-e29b-41d4-a716-446655440003",
  "blocks_completed": 4,
  "time_spent_seconds": 480,
  "quiz_score": 85.5,
  "is_completed": false
}
```

**Call this endpoint:**
- When student views a new block
- Every 30 seconds while active
- When quiz is answered
- When lesson is completed

**Response (200):**
```json
{
  "status": "updated",
  "progress": {
    "lesson_id": "550e8400-e29b-41d4-a716-446655440003",
    "blocks_completed": 4,
    "total_blocks": 6,
    "time_spent_seconds": 480,
    "quiz_score": 85.5,
    "is_completed": false,
    "completion_percentage": 66.7
  },
  "streak": {
    "current_streak": 5,
    "longest_streak": 12
  }
}
```

---

### School Endpoints

#### POST /schools
Create a new school.

**Authorization:** None (for MVP - should require admin)

**Request:**
```json
{
  "name": "Lagos International School",
  "address": "123 Victoria Island",
  "city": "Lagos",
  "state": "Lagos",
  "country": "Nigeria",
  "phone_number": "+234-1-234-5678",
  "email": "admin@lagosintl.edu.ng"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "name": "Lagos International School",
  "address": "123 Victoria Island",
  "city": "Lagos",
  "state": "Lagos",
  "country": "Nigeria",
  "is_active": true,
  "teacher_count": 0,
  "student_count": 0,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### GET /schools/dashboard
Get school admin dashboard.

**Authorization:** Required (School Admin only)

**Response (200):**
```json
{
  "school_id": "550e8400-e29b-41d4-a716-446655440006",
  "school_name": "Lagos International School",
  "total_teachers": 15,
  "total_students": 250,
  "total_lessons": 45,
  "active_students_today": 180,
  "average_school_score": 78.5,
  "students_completed_assessment": 230,
  "lessons_delivered_today": 320
}
```

---

#### GET /schools/teachers
List teachers in school.

**Authorization:** Required (School Admin only)

**Query Parameters:**
- `page` (int): Page number
- `page_size` (int): Items per page

**Response (200):**
```json
{
  "teachers": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440007",
      "email": "jane.smith@school.edu",
      "first_name": "Jane",
      "last_name": "Smith",
      "lesson_count": 12,
      "created_at": "2024-01-10T09:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

## Data Models

### User Roles
```typescript
enum UserRole {
  STUDENT = "student",
  TEACHER = "teacher",
  SCHOOL_ADMIN = "school_admin",
  PARENT = "parent",
  SUPER_ADMIN = "super_admin"
}
```

### Learning Styles
```typescript
enum LearningStyle {
  VISUAL = "VISUAL",           // Learns best with images, diagrams
  AUDITORY = "AUDITORY",       // Learns best with audio, discussions
  KINESTHETIC = "KINESTHETIC", // Learns best with hands-on activities
  READING_WRITING = "READING_WRITING", // Learns best with text
  MULTIMODAL = "MULTIMODAL"    // Mix of styles
}
```

### Complexity Levels
```typescript
enum ComplexityTolerance {
  LOW = "LOW",       // Simple language, short sentences
  MEDIUM = "MEDIUM", // Standard complexity
  HIGH = "HIGH"      // Advanced vocabulary, complex ideas
}
```

### Content Block Types
```typescript
enum ContentBlockType {
  HEADING = "heading",
  TEXT = "text",
  IMAGE = "image",
  IMAGE_PROMPT = "image_prompt",
  QUIZ = "quiz",
  ACTIVITY = "activity",
  SUMMARY = "summary"
}
```

### Lesson Status
```typescript
enum LessonStatus {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived"
}
```

---

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {
      "field": "specific field info"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description | Example |
|------|-------------|-------------|---------|
| `VALIDATION_ERROR` | 400 | Invalid input | Missing required field |
| `AUTHENTICATION_ERROR` | 401 | Auth failed | Invalid/expired token |
| `AUTHORIZATION_ERROR` | 403 | Not permitted | Student accessing teacher endpoint |
| `NOT_FOUND` | 404 | Resource missing | Lesson doesn't exist |
| `CONFLICT` | 409 | Already exists | Email already registered |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Slow down |
| `EXTERNAL_SERVICE_ERROR` | 502 | External API failed | Gemini API down |
| `INTERNAL_ERROR` | 500 | Server error | Unexpected failure |

### Handling in Frontend
```javascript
try {
  const response = await api.post('/auth/login', credentials);
  // Success
} catch (error) {
  if (error.response) {
    const { code, message } = error.response.data.error;

    switch (code) {
      case 'AUTHENTICATION_ERROR':
        showToast('Invalid email or password');
        break;
      case 'VALIDATION_ERROR':
        showFieldErrors(error.response.data.error.details);
        break;
      case 'RATE_LIMIT_EXCEEDED':
        showToast('Too many attempts. Please wait.');
        break;
      default:
        showToast(message);
    }
  }
}
```

---

## User Flows

### Student Onboarding Flow
```
1. School Admin creates school
   POST /schools

2. Student registers with school_id
   POST /auth/register

3. Student logs in
   POST /auth/login → Store tokens

4. Get assessment questions
   GET /assessment/questions

5. Student answers questions in UI

6. Submit assessment
   POST /assessment/submit → NeuroProfile created

7. Student is ready to learn!
```

### Student Learning Flow
```
1. Browse available lessons
   GET /lessons

2. Select a lesson
   GET /lessons/{id} → Show preview

3. Start learning (AI adaptation happens)
   GET /lessons/{id}/play → Get personalized blocks

4. Render blocks in order
   - Show content based on block type
   - Handle quiz interactions
   - Track time spent

5. Update progress periodically
   POST /progress/update (every 30s or on action)

6. Complete lesson
   POST /progress/update (is_completed: true)
```

### Teacher Lesson Upload Flow
```
1. Teacher logs in
   POST /auth/login

2. Create lesson
   POST /lessons/upload (multipart/form-data)

3. View own lessons
   GET /lessons?teacher_id={me}

4. Review student adaptations (optional)
   - View how AI adapted their content

5. Provide feedback for AI improvement
   POST /lessons/{id}/feedback
```

---

## WebSocket Events (Coming Soon)

Future real-time features:
- Live progress updates for parents
- Real-time collaboration
- Instant notifications

---

## Rate Limits

| Endpoint Category | Limit |
|-------------------|-------|
| Authentication | 10 req/min |
| AI Endpoints (/play) | 30 req/min |
| Other Endpoints | 100 req/min |

---

## Support

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

For issues, contact the backend team.
