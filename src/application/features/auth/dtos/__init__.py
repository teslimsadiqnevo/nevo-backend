"""Authentication DTOs."""

from src.application.features.auth.dtos.auth_dtos import (
    LoginInput,
    LoginOutput,
    RegisterInput,
    RegisterOutput,
    RefreshTokenInput,
    RefreshTokenOutput,
    ChangePasswordInput,
    ForgotPasswordInput,
    ResetPasswordInput,
    NevoIdLoginInput,
    SetPinInput,
    SetPinOutput,
)
from src.application.features.auth.dtos.teacher_signup_dtos import (
    TeacherSignUpInput,
    TeacherSignUpOutput,
)
from src.application.features.auth.dtos.school_admin_signup_dtos import (
    SchoolAdminSignUpInput,
    SchoolAdminSignUpOutput,
)

__all__ = [
    "LoginInput",
    "LoginOutput",
    "RegisterInput",
    "RegisterOutput",
    "RefreshTokenInput",
    "RefreshTokenOutput",
    "ChangePasswordInput",
    "ForgotPasswordInput",
    "ResetPasswordInput",
    "NevoIdLoginInput",
    "SetPinInput",
    "SetPinOutput",
    "TeacherSignUpInput",
    "TeacherSignUpOutput",
    "SchoolAdminSignUpInput",
    "SchoolAdminSignUpOutput",
]
