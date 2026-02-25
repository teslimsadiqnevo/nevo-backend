"""Authentication commands (write operations)."""

from src.application.features.auth.commands.login import LoginCommand
from src.application.features.auth.commands.register import RegisterCommand
from src.application.features.auth.commands.refresh_token import RefreshTokenCommand
from src.application.features.auth.commands.nevo_id_login import NevoIdLoginCommand
from src.application.features.auth.commands.register_teacher import RegisterTeacherCommand
from src.application.features.auth.commands.forgot_password import ForgotPasswordCommand
from src.application.features.auth.commands.reset_password import ResetPasswordCommand
from src.application.features.auth.commands.register_school_admin import RegisterSchoolAdminCommand

__all__ = [
    "LoginCommand",
    "RegisterCommand",
    "RefreshTokenCommand",
    "NevoIdLoginCommand",
    "RegisterTeacherCommand",
    "ForgotPasswordCommand",
    "ResetPasswordCommand",
    "RegisterSchoolAdminCommand",
]
