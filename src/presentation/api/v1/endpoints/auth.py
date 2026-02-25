"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.commands import (
    LoginCommand,
    RegisterCommand,
    RefreshTokenCommand,
    NevoIdLoginCommand,
    RegisterTeacherCommand,
    ForgotPasswordCommand,
    ResetPasswordCommand,
    RegisterSchoolAdminCommand,
)
from src.application.features.auth.dtos import (
    LoginInput,
    RegisterInput,
    RefreshTokenInput,
    NevoIdLoginInput,
    TeacherSignUpInput,
    ForgotPasswordInput,
    ResetPasswordInput,
    SchoolAdminSignUpInput,
)
from src.core.exceptions import AuthenticationError, ConflictError, ValidationError
from src.domain.interfaces.services import IEmailService
from src.presentation.api.v1.dependencies import get_uow, get_email_service
from src.presentation.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    NevoIdLoginRequest,
    TeacherSignUpRequest,
    TeacherSignUpResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SchoolAdminSignUpRequest,
    SchoolAdminSignUpResponse,
)

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="""
Authenticate a user with email and password.

**Returns:**
- `token`: JWT access token (expires in 30 minutes)
- `refresh_token`: JWT refresh token (expires in 7 days)
- `user`: User details including id, email, role, name, and school_id

**Usage:**
```javascript
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password123' })
});
const { token, refresh_token, user } = await response.json();
// Store token and use in subsequent requests
```
    """,
    responses={
        200: {"description": "Login successful, returns tokens and user info"},
        401: {"description": "Invalid email or password"},
    }
)
async def login(
    request: LoginRequest,
    uow: IUnitOfWork = Depends(get_uow),
):
    """Authenticate user and return JWT tokens."""
    try:
        command = LoginCommand(uow)
        result = await command.execute(
            LoginInput(email=request.email, password=request.password)
        )

        return LoginResponse(
            token=result.access_token,
            refresh_token=result.refresh_token,
            user={
                "id": str(result.user_id),
                "email": result.email,
                "role": result.role.value,
                "name": result.name,
                "school_id": str(result.school_id) if result.school_id else None,
            },
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="""
Register a new user account.

**Role Requirements:**
- `student`: Requires `school_id`
- `teacher`: Requires `school_id`
- `school_admin`: Requires `school_id`
- `parent`: Optional `school_id`

**Flow:**
1. Create a school first (POST /schools) if needed
2. Register user with the school_id
3. User can then login to get tokens

**Note:** Email must be unique across all users.
    """,
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Validation error (invalid role, missing school_id)"},
        409: {"description": "Email already exists"},
    }
)
async def register(
    request: RegisterRequest,
    uow: IUnitOfWork = Depends(get_uow),
):
    """Register a new user account."""
    try:
        command = RegisterCommand(uow)
        result = await command.execute(
            RegisterInput(
                email=request.email,
                password=request.password,
                first_name=request.first_name,
                last_name=request.last_name,
                age=request.age,
                role=request.role,
                school_id=request.school_id,
                phone_number=request.phone_number,
            )
        )

        return RegisterResponse(
            user_id=str(result.user_id),
            email=result.email,
            role=result.role.value,
            message=result.message,
        )

    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="""
Get new access and refresh tokens using a valid refresh token.

**When to use:**
- Access token expired (401 response on API calls)
- Proactively before expiration (recommended: refresh when < 5 min left)

**Token Lifecycle:**
- Access token: 30 minutes
- Refresh token: 7 days

**Best Practice:**
```javascript
// Axios interceptor example
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response.status === 401 && !error.config._retry) {
      error.config._retry = true;
      const { token } = await refreshTokens();
      error.config.headers.Authorization = `Bearer ${token}`;
      return axios(error.config);
    }
    return Promise.reject(error);
  }
);
```
    """,
    responses={
        200: {"description": "New tokens returned"},
        401: {"description": "Invalid or expired refresh token"},
    }
)
async def refresh_token(
    request: RefreshTokenRequest,
    uow: IUnitOfWork = Depends(get_uow),
):
    """Refresh access token using refresh token."""
    try:
        command = RefreshTokenCommand(uow)
        result = await command.execute(
            RefreshTokenInput(refresh_token=request.refresh_token)
        )

        return RefreshTokenResponse(
            token=result.access_token,
            refresh_token=result.refresh_token,
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.post(
    "/login/nevo-id",
    response_model=LoginResponse,
    summary="Login with Nevo ID and PIN",
    description="""
Authenticate a student using their Nevo ID and 4-digit PIN.

**Designed for tablet login** — students who may not remember email/password
can use their unique Nevo ID (format: `NEVO-XXXXX`) and a 4-digit PIN.

**Prerequisites:**
1. Student must have completed the onboarding assessment (Nevo ID is auto-generated)
2. Student must have set their PIN via `POST /students/me/pin`

**Returns:** Same tokens and user info as regular login.

**Usage:**
```javascript
const response = await fetch('/api/v1/auth/login/nevo-id', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ nevo_id: 'NEVO-7K3P2', pin: '1234' })
});
const { token, refresh_token, user } = await response.json();
```
    """,
    responses={
        200: {"description": "Login successful, returns tokens and user info"},
        401: {"description": "Invalid Nevo ID or PIN"},
    }
)
async def login_nevo_id(
    request: NevoIdLoginRequest,
    uow: IUnitOfWork = Depends(get_uow),
):
    """Authenticate student with Nevo ID and PIN."""
    try:
        command = NevoIdLoginCommand(uow)
        result = await command.execute(
            NevoIdLoginInput(nevo_id=request.nevo_id, pin=request.pin)
        )

        return LoginResponse(
            token=result.access_token,
            refresh_token=result.refresh_token,
            user={
                "id": str(result.user_id),
                "email": result.email,
                "role": result.role.value,
                "name": result.name,
                "school_id": str(result.school_id) if result.school_id else None,
            },
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.post(
    "/register/teacher",
    response_model=TeacherSignUpResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Teacher sign-up",
    description="""
Create a teacher account in one step.

**What happens:**
1. School is found by name (case-insensitive) or created automatically
2. Teacher account is created with the provided credentials
3. A class code is auto-generated (e.g. `NEVO-CLASS-4K7`)
4. JWT tokens are returned so the teacher can immediately access the dashboard

**No school_id needed** — just provide the school name.
    """,
    responses={
        201: {"description": "Teacher registered, returns tokens and class code"},
        400: {"description": "Validation error (school at capacity)"},
        409: {"description": "Email already exists"},
    },
)
async def register_teacher(
    request: TeacherSignUpRequest,
    uow: IUnitOfWork = Depends(get_uow),
):
    """Register a new teacher with automatic school lookup/creation."""
    try:
        command = RegisterTeacherCommand(uow)
        result = await command.execute(
            TeacherSignUpInput(
                full_name=request.full_name,
                school_name=request.school_name,
                email=request.email,
                password=request.password,
            )
        )

        return TeacherSignUpResponse(
            token=result.access_token,
            refresh_token=result.refresh_token,
            user={
                "id": str(result.user_id),
                "email": result.email,
                "role": "teacher",
                "name": result.name,
                "school_id": str(result.school_id),
                "school_name": result.school_name,
            },
            class_code=result.class_code,
        )

    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Request password reset",
    description="""
Send a password reset email to the user.

**Security:** Always returns a success message regardless of whether the email
exists — this prevents email enumeration attacks.

**Flow:**
1. User enters their email
2. If the email exists, a reset link is sent (valid for 1 hour)
3. The link points to `{FRONTEND_URL}/reset-password?token=...`
4. User clicks the link and submits a new password via `POST /auth/reset-password`
    """,
    responses={
        200: {"description": "Reset email sent (if account exists)"},
    },
)
async def forgot_password(
    request: ForgotPasswordRequest,
    uow: IUnitOfWork = Depends(get_uow),
    email_service: IEmailService = Depends(get_email_service),
):
    """Send password reset email."""
    command = ForgotPasswordCommand(uow, email_service)
    await command.execute(ForgotPasswordInput(email=request.email))

    return ForgotPasswordResponse(
        message="If an account with this email exists, a password reset link has been sent."
    )


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    summary="Reset password with token",
    description="""
Reset user's password using the token from the reset email.

**Token:** The JWT token received via email link (valid for 1 hour).

**Flow:**
1. Extract `token` from the URL query parameter on the frontend
2. Submit the token along with the new password
3. On success, redirect the user to the login page
    """,
    responses={
        200: {"description": "Password reset successfully"},
        401: {"description": "Invalid or expired reset token"},
        400: {"description": "Validation error (password too short)"},
    },
)
async def reset_password(
    request: ResetPasswordRequest,
    uow: IUnitOfWork = Depends(get_uow),
):
    """Reset password using reset token."""
    try:
        command = ResetPasswordCommand(uow)
        await command.execute(
            ResetPasswordInput(
                reset_token=request.reset_token,
                new_password=request.new_password,
            )
        )

        return ResetPasswordResponse(
            message="Password has been reset successfully. You can now log in."
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.post(
    "/register/school-admin",
    response_model=SchoolAdminSignUpResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set up a new school workspace",
    description="""
Create a school admin account and a new school workspace in one step.

**What happens:**
1. A new school is created with the provided name and optional address details
2. A school admin account is created with the provided credentials
3. JWT tokens are returned so the admin can immediately access the dashboard

**Use this for the "Set up a new school workspace" flow.**
    """,
    responses={
        201: {"description": "School workspace created, returns tokens and school info"},
        409: {"description": "Email already exists"},
    },
)
async def register_school_admin(
    request: SchoolAdminSignUpRequest,
    uow: IUnitOfWork = Depends(get_uow),
):
    """Register a new school admin with automatic school creation."""
    try:
        command = RegisterSchoolAdminCommand(uow)
        result = await command.execute(
            SchoolAdminSignUpInput(
                full_name=request.full_name,
                school_name=request.school_name,
                email=request.email,
                password=request.password,
                school_address=request.school_address,
                school_city=request.school_city,
                school_state=request.school_state,
            )
        )

        return SchoolAdminSignUpResponse(
            token=result.access_token,
            refresh_token=result.refresh_token,
            user={
                "id": str(result.user_id),
                "email": result.email,
                "role": "school_admin",
                "name": result.name,
                "school_id": str(result.school_id),
                "school_name": result.school_name,
            },
        )

    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
