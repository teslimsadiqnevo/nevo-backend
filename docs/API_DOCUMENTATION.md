# Nevo API Documentation

> **Version**: 1.0.0
> **Base URL**: `https://api.nevolearning.com/api/v1`
> **Swagger UI**: `https://api.nevolearning.com/docs`
> **ReDoc**: `https://api.nevolearning.com/redoc`

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
   - [Auth](#auth-endpoints)
   - [Students](#student-endpoints)
   - [Teachers](#teacher-endpoints)
   - [Schools](#school-endpoints)
   - [Assessment](#assessment-endpoints)
   - [Chat](#chat-endpoints)
   - [Lessons](#lesson-endpoints)
   - [Progress](#progress-endpoints)
   - [Email](#email-endpoints)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [User Flows](#user-flows)

---

## Getting Started

### Base URL
```
Development: http://localhost:8001/api/v1
Production:  https://api.nevolearning.com/api/v1
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
curl https://api.nevolearning.com/health

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

1. User registers or logs in and receives `access_token` + `refresh_token`
2. Use `access_token` in the `Authorization` header for API calls
3. When access token expires (30 min), use `refresh_token` to get new tokens
4. Refresh tokens expire after 7 days, after which the user must login again

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

#### POST /auth/login
Authenticate a user with email and password. Works for all roles (teacher, school admin, parent).

**Request:**
```json
{
  "email": "teacher@school.edu",
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
    "email": "teacher@school.edu",
    "role": "teacher",
    "name": "Adewale Johnson",
    "school_id": "550e8400-e29b-41d4-a716-446655440001"
  }
}
```

**Errors:**
- `401` - Invalid email or password

---

#### POST /auth/login/nevo-id
Authenticate a student using their Nevo ID and 4-digit PIN. Designed for tablet login where students may not remember email/password.

**Prerequisites:**
1. Student must have completed the onboarding assessment (Nevo ID is auto-generated)
2. Student must have set their PIN via `POST /students/me/pin`

**Request:**
```json
{
  "nevo_id": "NEVO-7K3P2",
  "pin": "1234"
}
```

**Response (200):** Same format as `POST /auth/login`.

**Errors:**
- `401` - Invalid Nevo ID or PIN

---

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

**Role Requirements:**
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

#### POST /auth/register/teacher
One-step teacher sign-up. Creates or finds school by name, generates a class code, and returns tokens immediately.

**Request:**
```json
{
  "full_name": "Sarah Jenkins",
  "school_name": "Lincoln High School",
  "email": "sarah@school.edu",
  "password": "securepass123"
}
```

**Response (201):**
```json
{
  "token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "sarah@school.edu",
    "role": "teacher",
    "name": "Sarah Jenkins",
    "school_id": "550e8400-e29b-41d4-a716-446655440001",
    "school_name": "Lincoln High School"
  },
  "class_code": "NEVO-CLASS-4K7"
}
```

**Errors:**
- `409` - Email already exists
- `400` - School at teacher capacity

---

#### POST /auth/register/school-admin
Set up a new school workspace. Creates a new school and school admin account in one step.

**Request:**
```json
{
  "full_name": "Adaobi Okafor",
  "school_name": "Greenfield Academy",
  "email": "admin@greenfield.edu.ng",
  "password": "securepass123",
  "school_address": "12 Education Lane",
  "school_city": "Lagos",
  "school_state": "Lagos"
}
```

Fields `school_address`, `school_city`, and `school_state` are optional.

**Response (201):**
```json
{
  "token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@greenfield.edu.ng",
    "role": "school_admin",
    "name": "Adaobi Okafor",
    "school_id": "550e8400-e29b-41d4-a716-446655440001",
    "school_name": "Greenfield Academy"
  }
}
```

**Errors:**
- `409` - Email already exists

---

#### POST /auth/forgot-password
Request a password reset email. Always returns 200 regardless of whether the email exists (prevents email enumeration).

**Request:**
```json
{
  "email": "teacher@school.edu"
}
```

**Response (200):**
```json
{
  "message": "If an account with this email exists, a password reset link has been sent."
}
```

---

#### POST /auth/reset-password
Reset password using the token from the reset email. The token is valid for 1 hour.

**Request:**
```json
{
  "reset_token": "eyJ...",
  "new_password": "newSecurePass123"
}
```

**Response (200):**
```json
{
  "message": "Password has been reset successfully. You can now log in."
}
```

**Errors:**
- `401` - Invalid or expired reset token
- `400` - Password too short (minimum 8 characters)

---

#### POST /auth/refresh
Get new tokens using a valid refresh token.

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

**Errors:**
- `401` - Invalid or expired refresh token

---

### Student Endpoints

All student endpoints require authentication with the `STUDENT` role.

#### GET /students/me/dashboard
Get the student home dashboard with stats, streaks, and recent activity.

**Authorization:** Required (Student)

**Response (200):**
```json
{
  "student_name": "Lydia Adeyemi",
  "nevo_id": "NEVO-7K3P2",
  "school_name": "Greenfield Academy",
  "stats": {
    "lessons_completed": 12,
    "current_streak": 5,
    "total_points": 340,
    "average_score": 85.5
  },
  "recent_lessons": [...],
  "achievements": [...]
}
```

---

#### GET /students/me/profile
Get the student's learning profile (NeuroProfile).

**Authorization:** Required (Student)

---

#### GET /students/me/progress
Get the student's overall learning progress.

**Authorization:** Required (Student)

---

#### POST /students/me/pin
Set or update the student's 4-digit PIN for Nevo ID login.

**Authorization:** Required (Student)

**Request:**
```json
{
  "pin": "1234"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "PIN set successfully",
  "nevo_id": "NEVO-7K3P2"
}
```

---

#### GET /students/me/settings
Get profile settings including accessibility preferences.

**Authorization:** Required (Student)

**Response (200):**
```json
{
  "email": "student@example.com",
  "first_name": "Lydia",
  "last_name": "Adeyemi",
  "avatar_url": null,
  "accessibility": {
    "voice_guidance": false,
    "large_text": false,
    "extra_spacing": false
  }
}
```

---

#### PATCH /students/me/settings
Update accessibility preferences.

**Authorization:** Required (Student)

**Request:**
```json
{
  "voice_guidance": true,
  "large_text": false,
  "extra_spacing": true
}
```

All fields are optional. Only provided fields are updated.

**Response (200):** Same format as `GET /students/me/settings`.

---

#### GET /students/me/connections
Get the student's teacher connections.

**Authorization:** Required (Student)

---

#### POST /students/me/connections
Send a connection request to a teacher using their class code.

**Authorization:** Required (Student)

**Request:**
```json
{
  "class_code": "NEVO-CLASS-4K7"
}
```

---

#### DELETE /students/me/connections/{connection_id}
Remove a teacher connection.

**Authorization:** Required (Student)

---

#### GET /students/{student_id}/profile
Get a specific student's learning profile. For teachers, school admins, or parents.

**Authorization:** Required (Teacher, School Admin, or Parent)

---

#### GET /students/{student_id}/progress
Get a specific student's learning progress. For teachers, school admins, or parents.

**Authorization:** Required (Teacher, School Admin, or Parent)

---

### Teacher Endpoints

All teacher endpoints require authentication with the `TEACHER` role.

#### GET /teachers/dashboard
Get the teacher dashboard with class stats and student overview.

**Authorization:** Required (Teacher)

---

#### GET /teachers/students
List students connected to this teacher.

**Authorization:** Required (Teacher)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 20) |

---

#### POST /teachers/feedback
Send feedback to a student.

**Authorization:** Required (Teacher)

---

#### GET /teachers/me/class-code
Get the teacher's class code for students to connect with.

**Authorization:** Required (Teacher)

**Response (200):**
```json
{
  "class_code": "NEVO-CLASS-4K7"
}
```

---

#### GET /teachers/me/connection-requests
Get pending connection requests from students.

**Authorization:** Required (Teacher)

---

#### PATCH /teachers/me/connection-requests/{connection_id}
Accept or reject a student connection request.

**Authorization:** Required (Teacher)

**Request:**
```json
{
  "action": "accept"
}
```

Action must be `"accept"` or `"reject"`.

---

### School Endpoints

#### POST /schools
Create a new school.

**Authorization:** None (for MVP)

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
Get school admin dashboard with stats.

**Authorization:** Required (School Admin)

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
List teachers in the school.

**Authorization:** Required (School Admin)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 20) |

---

#### GET /schools/{school_id}
Get school details by ID.

**Authorization:** Required (any authenticated user)

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
      "is_required": true
    }
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
Submit assessment answers and generate a NeuroProfile.

**Authorization:** Required (Student)

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
1. Answers are saved to the database
2. AI (Gemini) analyzes answers
3. NeuroProfile is created with learning style, complexity tolerance, attention span, sensory triggers, interests, and reading level

---

### Chat Endpoints

#### POST /chat/ask
Send a question to Nevo AI tutor.

**Authorization:** Required (Student)

**Request:**
```json
{
  "message": "Can you explain photosynthesis in a simple way?",
  "lesson_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

The `lesson_id` field is optional. When provided, Nevo uses the lesson content as context.

**Response (200):**
```json
{
  "response": "Of course! Photosynthesis is how plants make their own food...",
  "message_id": "550e8400-e29b-41d4-a716-446655440010"
}
```

---

#### GET /chat/history
Get the student's chat history with Nevo.

**Authorization:** Required (Student)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 20) |

---

### Lesson Endpoints

#### POST /lessons/upload
Upload a new lesson.

**Authorization:** Required (Teacher)

**Content-Type:** `multipart/form-data`

**Request Fields:**
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

**Authorization:** Required (any authenticated user)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `teacher_id` | UUID | Filter by teacher |
| `school_id` | UUID | Filter by school |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 20) |

---

#### GET /lessons/{lesson_id}
Get lesson details.

**Authorization:** Required (any authenticated user)

---

#### GET /lessons/{lesson_id}/play
Get personalized lesson content for a student. This is the core AI feature -- content is adapted based on the student's NeuroProfile.

**Authorization:** Required (Student)

**Response (200):**
```json
{
  "lesson_title": "Introduction to Photosynthesis",
  "adaptation_style": "Visual learning style with medium complexity, chunked for 15-minute attention span",
  "blocks": [
    {
      "id": "block_1",
      "type": "heading",
      "content": "How Plants Make Food",
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
      "order": 2
    },
    {
      "id": "block_4",
      "type": "activity",
      "content": "Draw a plant and label: 1) Where sunlight enters 2) Where water comes from 3) Where the food goes",
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
      "content": "**Key Takeaway**: Plants use sunlight + water + air to make their own food through photosynthesis!",
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
Submit feedback on adapted content.

**Authorization:** Required (Teacher)

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
Update a student's lesson progress.

**Authorization:** Required (Student)

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

**When to call:**
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

### Email Endpoints

#### POST /email/send
Send a custom email.

**Authorization:** Required (any authenticated user)

**Request:**
```json
{
  "to": "parent@example.com",
  "subject": "Student Progress Report",
  "body": "Your child completed 5 lessons this week.",
  "html_body": "<h1>Progress Report</h1><p>Your child completed 5 lessons this week.</p>"
}
```

The `html_body` field is optional.

---

#### POST /email/send-bulk
Send bulk emails (max 100 recipients).

**Authorization:** Required (any authenticated user)

**Request:**
```json
{
  "recipients": [
    { "to": "parent1@example.com", "subject": "Report", "body": "..." },
    { "to": "parent2@example.com", "subject": "Report", "body": "..." }
  ]
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
  VISUAL = "VISUAL",
  AUDITORY = "AUDITORY",
  KINESTHETIC = "KINESTHETIC",
  READING_WRITING = "READING_WRITING",
  MULTIMODAL = "MULTIMODAL"
}
```

### Complexity Levels
```typescript
enum ComplexityTolerance {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH"
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
   POST /schools  (or POST /auth/register/school-admin for one-step setup)

2. Student registers with school_id
   POST /auth/register

3. Student logs in
   POST /auth/login  (or POST /auth/login/nevo-id for tablet login)

4. Get assessment questions
   GET /assessment/questions

5. Student answers questions in UI

6. Submit assessment
   POST /assessment/submit  ->  NeuroProfile created, Nevo ID generated

7. Student sets PIN for future logins
   POST /students/me/pin

8. Student connects with teacher
   POST /students/me/connections  (using teacher's class code)

9. Student is ready to learn!
```

### Student Learning Flow
```
1. Browse available lessons
   GET /lessons

2. Select a lesson
   GET /lessons/{id}  ->  Show preview

3. Start learning (AI adaptation happens)
   GET /lessons/{id}/play  ->  Get personalized blocks

4. Render blocks in order
   - Show content based on block type
   - Handle quiz interactions
   - Track time spent

5. Update progress periodically
   POST /progress/update  (every 30s or on action)

6. Complete lesson
   POST /progress/update  (is_completed: true)

7. Ask Nevo questions about the lesson
   POST /chat/ask  (with lesson_id for context)
```

### Teacher Sign-Up Flow
```
1. Teacher signs up
   POST /auth/register/teacher  ->  Gets tokens + class_code

2. Teacher shares class code with students
   GET /teachers/me/class-code

3. Teacher views connection requests
   GET /teachers/me/connection-requests

4. Teacher accepts/rejects requests
   PATCH /teachers/me/connection-requests/{id}

5. Teacher uploads lessons
   POST /lessons/upload

6. Teacher views dashboard
   GET /teachers/dashboard
```

### School Admin Workspace Setup Flow
```
1. Admin creates workspace
   POST /auth/register/school-admin  ->  Gets tokens + school created

2. Admin views dashboard
   GET /schools/dashboard

3. Admin views teachers
   GET /schools/teachers
```

### Password Reset Flow
```
1. User requests reset
   POST /auth/forgot-password  ->  Email sent with reset link

2. User clicks email link  ->  Frontend reset page loads

3. User submits new password
   POST /auth/reset-password  ->  Password updated

4. User logs in with new password
   POST /auth/login
```

---

## Endpoint Summary

| Group | Count | Endpoints |
|-------|-------|-----------|
| Auth | 8 | login, login/nevo-id, register, register/teacher, register/school-admin, forgot-password, reset-password, refresh |
| Students | 11 | me/dashboard, me/profile, me/progress, me/pin, me/settings (GET+PATCH), me/connections (GET+POST+DELETE), {id}/profile, {id}/progress |
| Teachers | 6 | dashboard, students, feedback, me/class-code, me/connection-requests (GET+PATCH) |
| Schools | 4 | create, dashboard, teachers, {id} |
| Assessment | 2 | questions, submit |
| Chat | 2 | ask, history |
| Lessons | 5 | upload, list, {id}, {id}/play, {id}/feedback |
| Progress | 1 | update |
| Email | 2 | send, send-bulk |
| **Total** | **41** | |

---

## Rate Limits

| Endpoint Category | Limit |
|-------------------|-------|
| Authentication | 10 req/min |
| AI Endpoints (/play, /chat) | 30 req/min |
| Other Endpoints | 100 req/min |

---

## Support

- **Swagger UI**: https://api.nevolearning.com/docs
- **ReDoc**: https://api.nevolearning.com/redoc
- **OpenAPI JSON**: https://api.nevolearning.com/openapi.json
