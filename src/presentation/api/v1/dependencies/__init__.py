"""API dependencies module."""

from src.presentation.api.v1.dependencies.auth import (
    CurrentUser,
    get_current_user,
    get_current_active_user,
    require_role,
)
from src.presentation.api.v1.dependencies.database import get_uow
from src.presentation.api.v1.dependencies.services import (
    get_ai_service,
    get_cache_service,
    get_email_service,
    get_storage_service,
)

__all__ = [
    "CurrentUser",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "get_uow",
    "get_ai_service",
    "get_storage_service",
    "get_cache_service",
    "get_email_service",
]
