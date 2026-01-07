"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.commands import (
    LoginCommand,
    RegisterCommand,
    RefreshTokenCommand,
)
from src.application.features.auth.dtos import (
    LoginInput,
    RegisterInput,
    RefreshTokenInput,
)
from src.core.exceptions import AuthenticationError, ConflictError, ValidationError
from src.presentation.api.v1.dependencies import get_uow
from src.presentation.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
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
